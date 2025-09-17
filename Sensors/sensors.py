import time
import board
import busio
import adafruit_dht
import Adafruit_ADS1x15
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_hcsr04
import sqlite3
import datetime
from w1thermsensor import W1ThermSensor
from threading import Lock
import asyncio

# DHT11 Temperature and Humidity Sensor
# Verbunden an GPIO 17, Pin 1
# Initial the dht device, with data pin connected to:
# dhtDevice = None
#

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
#sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.D22, echo_pin=board.D27)

#PH Sensor
#Verbunden an ADS Channel 2
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
#Verbunden mit ADS Channel 1
# Initial the Device
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1
temperature = 25

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

# Macht Werte in die Datenbank nach 2 Stunden
async def add_to_db():

        now = datetime.datetime.now().replace(microsecond=0)
        await safe_db_execute("INSERT INTO Humidity_Sensor (value, timestamp) VALUES(?,?)",
                       (safe_round(sensor_state["humidity"]), now))
        await safe_db_execute("INSERT INTO Temp_Sensor (value, timestamp) VALUES(?,?)",
                       (safe_round(sensor_state["temperature"]), now))
        await safe_db_execute("INSERT INTO WaterLevel_Sensor (value, timestamp) VALUES(?,?)",
                       (safe_round(sensor_state["water_level"]), now))
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
            update_sensor_state("water_level", (adc_value - Min_ADC_Value) / (Max_ADC_Value - Min_ADC_Value) * 100)
            await safe_db_execute(
                "UPDATE WaterLevel_Sensor SET live_value = ? WHERE rowid = ?",
                (safe_round(sensor_state["water_level"]), 1)
            )

        except KeyboardInterrupt:
            print("\nScript terminated by User.")

        # Ultrasonic Sensor for Water level
        #try:
            #update_sensor_state("ultrasonic",sonar.distance)
            #await safe_db_execute(
                    #"UPDATE Ultrasonic_Sensor SET live_value =? WHERE rowid = ?",
                            #(safe_round(sensor_state["ultrasonic"]), 1)
            #)

        #except RuntimeError:
            #print("Retrying!")
        #except KeyboardInterrupt:
            #print("\nScript terminated by User.")

        #PH Sensor
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


async def main():
    while True:
        await sensor_activate()
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
