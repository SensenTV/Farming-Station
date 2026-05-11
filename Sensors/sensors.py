import time
from datetime import datetime, time
import time
import asyncio
from threading import Lock
import sqlite3

import board
import busio
import adafruit_dht
import Adafruit_ADS1x15
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_hcsr04
from w1thermsensor import W1ThermSensor
from gpiozero import PWMLED, LED, Button, PWMOutputDevice


# =============================
# Hardware-Initialisierung
# =============================

# Led initialisierung
pump_led = PWMLED(12)     # GPIO 12 (Pin 32)
light_led = PWMLED(6)     # GPIO 6  (Pin 31)
pump_schl = PWMLED(5)     # GPIO 5  (Pin 29)

# Fan initialisierung
fan_pin = 26  # GPIO-Pin am HW-517
fan = PWMOutputDevice(fan_pin)  # automatisch über pigpio

# DHT22 Temperature and Humidity Sensor
# Verbunden an GPIO 17, Pin 11
dhtDevice = adafruit_dht.DHT22(board.D17)

# Water Sensor (ADS Channel 3) --- entfernt


# Ultrasonic Sensor für Wasserstand
# Echo Pin verbunden an GPIO 27, Pin 13
# Trigger pin verbunden an GPIO 22, Pin 15
sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.D27, echo_pin=board.D22)
d_max = 50  # Abstand(cm) bei leerem Tank
d_min = 5   # Abstand(cm) bei vollem Tank

# PH Sensor (ADS Channel 1)
mess_n = (1.419, 4.01)       # niedriger Ph
mess_h = (2.022, 9.14)       # hoher Ph
cali_m = (mess_h[1] - mess_n[1]) / (mess_h[0] - mess_n[0])
cali_y = mess_n[1] - (cali_m * mess_n[0])
ph_val = 0
avg_val = 0
buffer_arr = [0.0] * 10
temp = 0.0

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1

# TDS Sensor (ADS Channel 0)
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1
SCOUNT = 11
VREF = 5.0                 # nur relevant, falls externer ADC skaliert
tds_border = await get_tds_barrier()  # TDS-Schwellenwert

# Flowrate Sensor --- entfernt


# =============================
# Hilfsfunktionen Hardware
# =============================

def count_pulse():
    """Zählt Impulse für die Flowrate"""
    global pulse_count, total_pulses
    pulse_count += 1
    total_pulses += 1

def parse_time(value):
    """Konvertiert String in datetime.time, falls nötig"""
    if isinstance(value, str):
        return datetime.strptime(value, "%H:%M").time()
    return value

def ec_from_voltage(v):
    """Gibt die Funktion raus um Volt in EC umzuwandeln"""
    a = 70.712
    b = 135.264
    c = 213.240
    d = 267.609

    return a * v**3 + b * v**2 + c * v + d

def median(values):
    """Medianberechnung einer Zahlenliste"""
    values = sorted(values)
    n = len(values)
    return values[n // 2] if n % 2 else (values[n//2 - 1] + values[n//2]) / 2

# =============================
# Sensor-State
# =============================


sensor_state = {
    "humidity": None,
    "temperature": None,
    "water_level": None,
    "ultrasonic": None,
    "ph": None,
    "tds": None,
}


def update_sensor_state(key, value):
    """Aktualisiert einen Wert im sensor_state nur, wenn value nicht None ist"""
    if value is not None:
        sensor_state[key] = value


def safe_round(value, ndigits=2):
    """Rundet Werte auf ndigits, falls nicht None"""
    return round(value, ndigits) if value is not None else None

# =============================
# Datenbank-Setup
# =============================


db_lock = asyncio.Lock()
conn = sqlite3.connect("./SQLite/sensors.db", check_same_thread=False)
cursor = conn.cursor()


async def safe_db_execute(query, params=()):
    """
    Führt ein SQL-Query aus.
    - SELECT -> liefert Liste von Tupeln
    - UPDATE/INSERT/DELETE -> commit
    """
    async with db_lock:
        cursor.execute(query, params)

        if query.strip().upper().startswith("SELECT"):
            return cursor.fetchall()
        else:
            conn.commit()
            return None


async def safe_db_fetchone(query, params=()):
    """SELECT und liefert erste Zeile oder None"""
    rows = await safe_db_execute(query, params)
    if rows and len(rows) > 0:
        return rows[0]
    return None

# =============================
# Konfigurations-Funktionen
# =============================


async def get_pump_config():
    """Liest Intervall und Dauer (on_for) aus der DB"""
    row = await safe_db_fetchone("SELECT intervall, on_for FROM Pump LIMIT 1;")
    return row if row else (10, 10)  # fallback


async def get_fan_config():
    """Liest Intervall und Dauer (on_for) aus der DB"""
    row = await safe_db_fetchone("SELECT intervall, on_for FROM Fan LIMIT 1;")
    return row if row else (120, 60)  # fallback


async def get_light_config():
    """Liest Start- und Endzeit der Lichtphasen"""
    row1 = await safe_db_fetchone("SELECT start_time, end_time FROM Light WHERE ROWID = 1;")
    row2 = await safe_db_fetchone("SELECT start_time, end_time FROM Light WHERE ROWID = 2;")

    start1, end1 = map(parse_time, row1) if row1 else (
        time(12, 0), time(17, 0))
    start2, end2 = map(parse_time, row2) if row2 else (time(0, 0), time(5, 0))

    return (start1, end1), (start2, end2)

async def get_tds_barrier():
    """Liest den EC/TDS Grenzwert aus der DB"""
    
    row = await safe_db_fetchone(
        "SELECT tds_barrier FROM EC_Sensor WHERE rowid = 1"
    )

    if row and row[0] is not None:
        return float(row[0])

    return 1000  # fallback


# =============================
# Sensorwerte in DB speichern (alle 2 Stunden)
# =============================

async def add_to_db():
    """
    Speichert die aktuellen Sensorwerte in den jeweiligen Tabellen
    mit Timestamp.
    """
    now = datetime.now().replace(microsecond=0)

    # Humidity
    await safe_db_execute(
        "INSERT INTO Humidity_Sensor (value, timestamp) VALUES (?, ?)",
        (safe_round(sensor_state["humidity"]), now)
    )

    # Temperature
    await safe_db_execute(
        "INSERT INTO Temp_Sensor (value, timestamp) VALUES (?, ?)",
        (safe_round(sensor_state["temperature"]), now)
    )

    # Ultrasonic Sensor
    await safe_db_execute(
        "INSERT INTO Ultrasonic_Sensor (value, timestamp) VALUES (?, ?)",
        (safe_round(sensor_state["ultrasonic"]), now)
    )

    # PH Sensor
    await safe_db_execute(
        "INSERT INTO PH_Sensor (value, timestamp) VALUES (?, ?)",
        (safe_round(sensor_state["ph"]), now)
    )

    # TDS Sensor
    await safe_db_execute(
        "INSERT INTO EC_Sensor (value, timestamp) VALUES (?, ?)",
        (safe_round(sensor_state["tds"]), now)
    )


# =============================
# Sensor-Aktivierung / Messungen
# =============================

async def sensor_activate():
    """Liest alle Sensoren aus und schreibt Live-Werte in die DB"""
    # Water Sensor
    # Wurde entfernt-------------------------------------------------------------------

    # Ultrasonic Sensor
    try:
        distance = sonar.distance
        fill_percent = max(
            0, min(100, (d_max - distance) / (d_max - d_min) * 100))
        update_sensor_state("ultrasonic", fill_percent)
        await safe_db_execute("UPDATE Ultrasonic_Sensor SET live_value=? WHERE rowid=?",
                              (safe_round(fill_percent), 1))
    except RuntimeError:
        print("Retrying!")
    except KeyboardInterrupt:
        print("\nScript terminated by User.")

    # PH Sensor
    try:
        chan = AnalogIn(ads, ADS.P1)
        for i in range(10):
            buffer_arr[i] = chan.voltage
            await asyncio.sleep(0.05)
        buffer_arr.sort()
        avg_val = sum(buffer_arr[2:8]) / 6
        update_sensor_state("ph", cali_m * avg_val + cali_y - 1.95)
        await safe_db_execute("UPDATE PH_Sensor SET live_value=? WHERE rowid=?",
                              (safe_round(sensor_state["ph"]), 1))
    except KeyboardInterrupt:
        print("\nScript terminated by User.")

    # TDS Sensor
    try:
        buffer = []
        tds_chan = AnalogIn(ads, ADS.P0)   # TDS/EC Sensor an A0
        for _ in range(SCOUNT):
            buffer.append(tds_chan.voltage)
            await asyncio.sleep(0.05)

        median_voltage = median(buffer)

        tds_value = ec_from_voltage(median_voltage)

        update_sensor_state("tds", tds_value)
        await safe_db_execute("UPDATE EC_Sensor SET live_value=? WHERE rowid=?",
                              (safe_round(sensor_state["tds"]), 1))
        if tds_value < tds_border:
            pump_schl.on()
            await asyncio.sleep(1)
            pump_schl.off()
            await asyncio.sleep(2)
        else:
            pump_schl.off()
        
    except KeyboardInterrupt:
        print("\nScript terminated by User.")

    # Temperatur Sensor DS18B20
    try:
        sensor = W1ThermSensor()
        update_sensor_state("temperature", sensor.get_temperature())
        await safe_db_execute("UPDATE Temp_Sensor SET live_value=? WHERE rowid=?",
                              (safe_round(sensor_state["temperature"]), 1))
    except Exception as e:
        print(f"Temperatursensor Fehler: {e}")

    print("sensor_activate fertig")


async def read_dht():
    """Liest DHT11 aus und schreibt Wert in die DB"""
    try:
        humidity = dhtDevice.humidity
        if humidity is not None:
            update_sensor_state("humidity", humidity)
            await safe_db_execute("UPDATE Humidity_Sensor SET live_value=? WHERE rowid=?",
                                  (safe_round(sensor_state["humidity"]), 1))
            print(
                f"[DHT11] Humidity aktualisiert: {sensor_state['humidity']}%")
        else:
            print("[DHT11] Kein gültiger Wert erhalten (None) → behalte alten Wert")
    except RuntimeError as error:
        print(f"[DHT11] Fehler: {error.args[0]}")
        await asyncio.sleep(2.0)
    except KeyboardInterrupt:
        print("\n[DHT11] Script beendet vom User.")
        dhtDevice.exit()
    finally:
        print("read_dht fertig")

# =============================
# Pumpen- / Flowrate-Zyklus
# =============================


async def pump_and_waterflow_cycle():
    """Steuert die Pumpe zyklisch und überwacht die Flowrate"""
    # Flowrate Sensor wurde entfernt----------------------------------------------------------
    await safe_db_execute("UPDATE FlowRate_Sensor SET status=? WHERE rowid=?", ("offline", 1))
    while True:
        intervall, dauer = await get_pump_config()
        print(f"Warte {intervall}m bis zum nächsten Pumpenlauf...")
        await asyncio.sleep(intervall*60)

        print(f"Pumpe EIN für {dauer}m")
        pump_led.on()
        await safe_db_execute("UPDATE Pump SET status=? WHERE rowid=?", ("online", 1))

        start_time = datetime.now().timestamp()
        last_time = start_time

        while time.time()-start_time < dauer*60:
            await asyncio.sleep(intervall * 60)

        pump_led.off()
        print("Pumpe AUS")
        await safe_db_execute("UPDATE Pump SET status=? WHERE rowid=?", ("offline", 1))


async def start_pump_loop():
    asyncio.create_task(pump_and_waterflow_cycle())

# =============================
# Fan-Zyklus mit Intensität
# =============================


async def fan_cycle_and_intensity():
    """Steuert den Fan zyklisch mit Intensität aus der DB"""
    print("Fan-Cycle gestartet")
    while True:
        intervall, dauer = await get_fan_config()
        print(f"Warte {intervall} Minuten bis zum nächsten Lüfterstart...")
        await asyncio.sleep(intervall*60)

        # Intensität aus DB
        row = await safe_db_execute("SELECT intensity FROM Fan WHERE rowid=?", (1,))
        print("DB-Result:", row)

        intensity = str(row[0][0]).strip().capitalize() if row else "Stark"
        print("Bereinigter Intensitätswert:", repr(intensity))

        intensity_map = {"Stark": 1.0, "Mittel": 0.75, "Schwach": 0.5}
        fan_value = intensity_map.get(intensity, 1.0)

        print(f"Lüfter an (Intensität: {intensity}, Wert: {fan_value})")
        fan.value = fan_value
        await safe_db_execute("UPDATE Fan SET status=? WHERE rowid=?", ("online", 1))

        await asyncio.sleep(dauer*60)

        fan.value = 0.0
        await safe_db_execute("UPDATE Fan SET status=? WHERE rowid=?", ("offline", 1))
        print("Lüfter aus")


async def start_fan_loop():
    asyncio.create_task(fan_cycle_and_intensity())

# =============================
# Lichtsteuerung
# =============================


async def light_cycle():
    """Steuert Licht nach Uhrzeit und DB-Konfiguration"""
    while True:
        (start1, end1), (start2, end2) = await get_light_config()
        now = datetime.now().time()

        def in_range(start, end, current):
            if start <= end:
                return start <= current <= end
            else:
                return current >= start or current <= end

        light_led.on() if in_range(start1, end1, now) or in_range(
            start2, end2, now) else light_led.off()
        await asyncio.sleep(1)


async def start_light():
    asyncio.create_task(light_cycle())
