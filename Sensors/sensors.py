import time
import board
import busio
import adafruit_dht
import Adafruit_ADS1x15
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_hcsr04
import sqlite3
from datetime import datetime, time
import time
from w1thermsensor import W1ThermSensor
from threading import Lock
import asyncio
from gpiozero import PWMLED
from gpiozero import LED
from gpiozero import Button
from gpiozero import PWMOutputDevice

# Led initialisierung
pump_led = PWMLED(12)     # GPIO 12 (Pin 32)
light_led = PWMLED(6)     # GPIO 13 (Pin 33)

# Fan initialisierung
fan_pin = 26  # GPIO-Pin am HW-517
fan = PWMOutputDevice(fan_pin)  # automatisch über pigpio

# DHT11 Temperature and Humidity Sensor
# Verbunden an GPIO 17, Pin 1
# Initial the dht device, with data pin connected to:
# dhtDevice = None
dhtDevice = adafruit_dht.DHT11(board.D17)

# Water Sensor
# Verbunden an ADS Channel 3
# Initial the Device
ADC = Adafruit_ADS1x15.ADS1115(busnum=1)
ADC_Channel = 3
Gain = 1
Min_ADC_Value = 0
Max_ADC_Value = 32767

# Ultrasonic Sensor for Water level
# Echo Pin verbunden an GPIO 27, Pin 13
# Trigger pin verbunden an GPIO 22, Pin 15
# Initial Device
sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.D27, echo_pin=board.D22)
# Tankparameter in cm
d_max = 50  # Abstand bei leerem Tank
d_min = 5   # Abstand bei vollem Tank

# PH Sensor
# Verbunden an ADS Channel 2
mess_n = (3.773, 4.01)       # niedriger Ph
mess_h = (3.229, 9.14)       # hoher Ph
cali_m = (mess_h[1] - mess_n[1]) / (mess_h[0] - mess_n[0])
cali_y = mess_n[1] - (cali_m * mess_n[0])
ph_val = 0
avg_val = 0
buffer_arr = [0.0] * 10
temp = 0.0

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1

# TDS Sensor
# Verbunden mit ADS Channel 1
# Initial the Device
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1
temperature = 25

# Flowrate Lore
PIN = 24
K = 450.0  # Impulse pro Liter

pulse_count = 0
total_pulses = 0


def count_pulse():
    global pulse_count, total_pulses
    pulse_count += 1
    total_pulses += 1


# Button mit internem Pull-up (Sensor ist open-collector -> benötigt Pull-up)
waterflow = Button(PIN, pull_up=True)
waterflow.when_pressed = count_pulse  # bei Flanke (aktiv low) zählt

PRINT_INTERVAL = 1.0  # Sekunden


def parse_time(value):
    if isinstance(value, str):
        return datetime.strptime(value, "%H:%M").time()
    return value


sensor_state = {
    "humidity": None,
    "temperature": None,
    "water_level": None,
    "ultrasonic": None,
    "ph": None,
    "tds": None,
}


def update_sensor_state(key, value):
    """Aktualisiert einen Wert im sensor_state nur wenn er nicht None ist"""
    if value is not None:
        sensor_state[key] = value


def safe_round(value, ndigits=2):
    return round(value, ndigits) if value is not None else None


db_lock = asyncio.Lock()
conn = sqlite3.connect("./SQLite/sensors.db", check_same_thread=False)
cursor = conn.cursor()


async def safe_db_execute(query, params=()):
    async with db_lock:
        cursor.execute(query, params)
        conn.commit()

# Helfer für SELECT-Abfragen


async def safe_db_fetchone(query, params=()):
    async with db_lock:
        cursor.execute(query, params)
        return cursor.fetchone()

# Pumpenkonfiguration aus DB holen


async def get_pump_config():
    """Liest Intervall und Dauer (on_for) aus der DB"""
    row = await safe_db_fetchone("SELECT intervall, on_for FROM Pump LIMIT 1;")
    if row:
        return row[0], row[1]
    return 10, 10  # fallback falls keine Werte in DB

# Lüfterkonfiguration aus DB holen


async def get_fan_config():
    """Liest Intervall und Dauer (on_for) aus der DB"""
    row = await safe_db_fetchone("SELECT intervall, on_for FROM Fan LIMIT 1;")
    if row:
        return row[0], row[1]
    return 120, 60  # fallback falls keine Werte in DB


async def get_light_config():
    """Liest die Uhrzeiten von wann bis wann das Licht (LED) gestartet wird"""
    row1 = await safe_db_fetchone("SELECT start_time, end_time FROM Light WHERE ROWID = 1;")
    row2 = await safe_db_fetchone("SELECT start_time, end_time FROM Light WHERE ROWID = 2;")

    if row1:
        start1, end1 = map(parse_time, row1)
    else:
        start1, end1 = time(12, 0), time(17, 0)  # Default 12:00–17:00

    if row2:
        start2, end2 = map(parse_time, row2)
    else:
        start2, end2 = time(0, 0), time(5, 0)    # Default 00:00–05:00

    return (start1, end1), (start2, end2)


# Macht Werte in die Datenbank nach 2 Stunden


async def add_to_db():

    now = datetime.now().replace(microsecond=0)
    await safe_db_execute("INSERT INTO Humidity_Sensor (value, timestamp) VALUES(?,?)",
                          (safe_round(sensor_state["humidity"]), now))
    await safe_db_execute("INSERT INTO Temp_Sensor (value, timestamp) VALUES(?,?)",
                          (safe_round(sensor_state["temperature"]), now))
    await safe_db_execute("INSERT INTO Ultrasonic_Sensor (value, timestamp) VALUES(?,?)",
                          (safe_round(sensor_state["ultrasonic"]), now))
    await safe_db_execute("INSERT INTO PH_Sensor (value, timestamp) VALUES(?,?)",
                          (safe_round(sensor_state["ph"]), now))
    await safe_db_execute("INSERT INTO EC_Sensor (value, timestamp) VALUES(?,?)",
                          (safe_round(sensor_state["tds"]), now))


async def sensor_activate():
    # Water Sensor
    try:
        adc_value = ADC.read_adc(ADC_Channel, gain=Gain)
        update_sensor_state(
            "water_level", (adc_value - Min_ADC_Value) / (Max_ADC_Value - Min_ADC_Value) * 100)
        await safe_db_execute(
            "UPDATE WaterLevel_Sensor SET live_value = ? WHERE rowid = ?",
            (safe_round(sensor_state["water_level"]), 1)
        )

    except KeyboardInterrupt:
        print("\nScript terminated by User.")

    # Ultrasonic Sensor for Water level
    try:
        # gemessener Abstand vom Sensor
        distance = sonar.distance

        # Füllstand in Prozent berechnen
        fill_percent = (d_max - distance) / (d_max - d_min) * 100
        fill_percent = max(0, min(100, fill_percent))  # Begrenzen auf 0-100%

        # Sensorwert aktualisieren
        update_sensor_state("ultrasonic", fill_percent)

        # In DB speichern
        await safe_db_execute(
            "UPDATE Ultrasonic_Sensor SET live_value =? WHERE rowid = ?",
            (safe_round(fill_percent), 1)
        )

    except RuntimeError:
        print("Retrying!")
    except KeyboardInterrupt:
        print("\nScript terminated by User.")

    # PH Sensor
    try:
        for i in range(10):
            chan = AnalogIn(ads, ADS.P2)
            buffer_arr[i] = chan.voltage
            await asyncio.sleep(0.05)

        buffer_arr.sort()
        avg_val = sum(buffer_arr[2:8]) / 6
        update_sensor_state("ph", cali_m * avg_val + cali_y - 1.95)

        await safe_db_execute(
            "UPDATE PH_Sensor SET live_value = ? WHERE rowid = ?",
            (safe_round(sensor_state["ph"]), 1)
        )

    except KeyboardInterrupt:
        print("\nScript terminated by User.")

    # TDS Sensor
    try:
        adc_value = AnalogIn(ads, ADS.P1)
        compensationCoefficient = 1.0 + 0.02 * (temperature - 25.0)
        compensationVolt = adc_value.voltage / compensationCoefficient
        update_sensor_state("tds", (133.42 * compensationVolt**3 -
                                    255.86 * compensationVolt**2 +
                                    857.39 * compensationVolt) * 0.5)
        await safe_db_execute(
            "UPDATE EC_Sensor SET live_value = ? WHERE rowid = ?",
            (safe_round(sensor_state["tds"]), 1)
        )

    except KeyboardInterrupt:
        print("\nScript terminated by User.")

    # DF18B20 Temperatur Sensor
    try:
        sensor = W1ThermSensor()
        update_sensor_state("temperature", sensor.get_temperature())
        await safe_db_execute(
            "UPDATE Temp_Sensor SET live_value = ? WHERE rowid = ?",
            (safe_round(sensor_state["temperature"]), 1)
        )

    except Exception as e:
        print(f"Temperatursensor Fehler: {e}")

    except KeyboardInterrupt:
        print("\nScript terminated by User.")

    print("sensor_activate fertig")


async def read_dht():
    """
    Liest den DHT11-Sensor aus und speichert den Wert in der DB.
    Diese Methode ist async, damit man sie mit asyncio aufrufen kann.
    """
    try:
        # Sensorwert holen
        humidity = dhtDevice.humidity

        # Nur speichern, wenn der Sensor einen gültigen Wert liefert
        if humidity is not None:
            update_sensor_state("humidity", humidity)

            # Wert in die Datenbank schreiben (UPDATE auf erste Zeile)
            await safe_db_execute(
                "UPDATE Humidity_Sensor SET live_value = ? WHERE rowid = ?",
                (safe_round(sensor_state["humidity"]), 1)
            )
            print(
                f"[DHT11] Humidity aktualisiert: {sensor_state['humidity']}%")
        else:
            # Sensor hat None zurückgegeben → alten Wert behalten
            print("[DHT11] Kein gültiger Wert erhalten (None) → behalte alten Wert")

    except RuntimeError as error:
        # Fehler treten beim DHT oft auf, einfach überspringen
        print(f"[DHT11] Fehler: {error.args[0]}")
        await asyncio.sleep(2.0)

    except KeyboardInterrupt:
        print("\n[DHT11] Script beendet vom User.")
        dhtDevice.exit()

    finally:
        print("read_dht fertig")


async def pump_and_waterflow_cycle():
    global pulse_count, total_pulses
    """
    Steuert die Pumpe (LED) zyklisch
    und überwacht gleichzeitig den Wasserfluss.
    """
    while True:
        # Hole Pumpenkonfiguration (Intervall + Dauer)
        intervall, dauer = await get_pump_config()
        print(f"⏱️ Warte {intervall}m bis zum nächsten Pumpenlauf...")
        await asyncio.sleep(intervall * 60)

        # Pumpe EIN
        print(f"💡 Pumpe EIN für {dauer}m")
        pump_led.on()
        await safe_db_execute("UPDATE Pump SET status = ? WHERE rowid = 1", ("online",))

        # Flowrate überwachen während die Pumpe läuft
        start_time = time.time()
        last_time = start_time

        while time.time() - start_time < dauer * 60:
            await asyncio.sleep(PRINT_INTERVAL)
            now = time.time()
            elapsed = now - last_time
            last_time = now

            pulses = pulse_count
            pulse_count = 0

            flow_l_min = (pulses / elapsed) * (60.0 / K) if pulses else 0.0
            print(f"💧 Durchfluss: {flow_l_min:.3f} L/min | Impulse: {pulses}")

            # Werte in die DB schreiben
            await safe_db_execute(
                "UPDATE FlowRate_Sensor SET value = ?, status = ? WHERE rowid = 1",
                (flow_l_min, "online")
            )

        # Pumpe AUS
        pump_led.off()
        print("💡 Pumpe AUS")
        await safe_db_execute("UPDATE Pump SET status = ? WHERE rowid = 1", ("offline",))
        await safe_db_execute("UPDATE FlowRate_Sensor SET status = ? WHERE rowid = 1", ("offline",))


async def start_pump_loop():
    asyncio.create_task(pump_and_waterflow_cycle())


async def fan_cycle():
    """
    Steuert die Fan zyklisch
    """
    while True:
        intervall, dauer = await get_fan_config()
        print(f"Warte {intervall}m bis zum nächsten Lüfterstart...")
        await asyncio.sleep(intervall*60)

        print("Lüfter an")
        fan.value = 1.0
        await safe_db_execute("UPDATE Fan SET status = ? WHERE rowid = 1", ("online",))
        await asyncio.sleep(dauer*60)
        fan.value = 0.0
        await safe_db_execute("UPDATE Fan SET status = ? WHERE rowid = 1", ("offline",))
        print("Lüfter aus")


async def start_fan_loop():
    asyncio.create_task(fan_cycle())


async def light_cycle():
    """
    Steuert das Licht nach der aktuellen Uhrzeit anhand der gespeicherten Konfiguration.
    """
    while True:
        (start1, end1), (start2, end2) = await get_light_config()
        now = datetime.now().time()

        def in_range(start, end, current):
            if start <= end:
                return start <= current <= end
            else:
                return current >= start or current <= end

        if in_range(start1, end1, now) or in_range(start2, end2, now):
            light_led.on()
        else:
            light_led.off()

        await asyncio.sleep(1)


async def start_light():
    asyncio.create_task(light_cycle())
