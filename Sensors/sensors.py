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
from threading import Lock

# DHT11 Temperature and Humidity Sensor
# Verbunden an GPIO 17, Pin 1
# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT11(board.D17)

# Water Sensor
# Verbunden an ADS Channel 3
# Initial the Device
ADC = Adafruit_ADS1x15.ADS1115(busnum= 1)
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
mess_n = (3.773,4.01)       # niedriger Ph     
mess_h = (3.229,9.14)       # hoher Ph
cali_m = (mess_h[1] - mess_n[1]) / (mess_h[0] - mess_n[0])
cali_y = mess_n[1] - (cali_m * mess_n[0])
ph_val = 0
avg_val = 0
buffer_arr = [0.0] *10
temp = 0.0

i2c = busio.I2C(board.SCL,board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1

# TDS Sensor
#Verbunden mit ADS Channel 1
# Initial the Device
i2c = busio.I2C(board.SCL,board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1
temperature = 25

sensor_state = {
    "humidity":None,
    "temperature":None,
    "water_level":None,
    "ultrasonic":None,
    "ph":None,
    "tds":None,
}

def safe_round(value, ndigits=2):
    return round(value, ndigits) if value is not None else None

# Macht Werte in die Datenbank nach 2 Stunden
def add_to_db():

    # SQL Initialisieren
    db_path = "./SQLite/sensors.db"
    conn = sqlite3.connect(db_path,check_same_thread=False)
    cursor = conn.cursor()
    db_lock = Lock()
    with db_lock:

        now = datetime.datetime.now().replace(microsecond=0)
        cursor.execute("INSERT INTO Humidity_Sensor (value, timestamp) VALUES(?,?)",
                       (safe_round(sensor_state["humidity"]),now))
        cursor.execute("INSERT INTO WaterLevel_Sensor (value, timestamp) VALUES(?,?)",
                       (safe_round(sensor_state["water_level"]),now))
        cursor.execute("INSERT INTO Ultrasonic_Sensor (value, timestamp) VALUES(?,?)",
                       (safe_round(sensor_state["ultrasonic"]),now))
        cursor.execute("INSERT INTO PH_Sensor (value, timestamp) VALUES(?,?)",
                       (safe_round(sensor_state["ph"]),now))
        cursor.execute("INSERT INTO EC_Sensor (value, timestamp) VALUES(?,?)",
                       (safe_round(sensor_state["tds"]),now))

    conn.commit()
    conn.close()

def sensor_activate():
    # SQL Initialisieren
    db_path = "./SQLite/sensors.db"
    conn = sqlite3.connect(db_path,check_same_thread=False)
    cursor = conn.cursor()
    db_lock = Lock()
    with db_lock:
        #while True:

        # DHT11 Temperature and Humidity Sensor
        try:
            # Print the values to the serial port
            sensor_state["humidity"] = dhtDevice.humidity
            cursor.execute(
                "UPDATE Humidity_Sensor SET live_value = ? WHERE rowid = ?",
                (safe_round(sensor_state["humidity"]), 1)
            )
            conn.commit()
            

        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)
            #continue
        except KeyboardInterrupt:
            print("\nScript terminated by User.")
            dhtDevice.exit()
        

        # Water Sensor
        try:
            # Read ADC Value
            adc_value = ADC.read_adc(ADC_Channel, gain=Gain)

            #Convert ADC Value to water level percentage
            sensor_state["water_level"] = (adc_value - Min_ADC_Value) / (Max_ADC_Value - Min_ADC_Value) * 100

            cursor.execute(
                "UPDATE WaterLevel_Sensor SET live_value = ? WHERE rowid = ?",
                (safe_round(sensor_state["water_level"]), 1)
            )
            conn.commit()

        except KeyboardInterrupt:
            print("\nScript terminated by User.")

        # Ultrasonic Sensor for Water level
        #try:
            #sensor_state["ultrasonic"] = sonar.distance
            #cursor.execute(
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
                chan = AnalogIn(ads,ADS.P2)
                buffer_arr[i] = chan.voltage
                time.sleep(0.05)

            for i in range(9):
                for j in range(i + 1, 10):
                    if buffer_arr[i] > buffer_arr[j]:
                        temp = buffer_arr[i]
                        buffer_arr[i] = buffer_arr[j]
                        buffer_arr[j] = temp
                        
            avg_val = sum(buffer_arr[2:8]) / 6
            sensor_state["ph"] = cali_m * avg_val + cali_y - 1.95

            cursor.execute(
                "UPDATE PH_Sensor SET live_value = ? WHERE rowid = ?",
                (safe_round(sensor_state["ph"]), 1)
            )
            conn.commit()

        except KeyboardInterrupt:
            print("\nScript terminated by User.")

        # TDS Sensor
        try:
            # Read ADC Value
            adc_value = AnalogIn(ads,ADS.P1)

            compensationCoefficient = 1.0 + 0.02 * (temperature - 25.0)

            compensationVolt = adc_value.voltage/compensationCoefficient

            sensor_state["tds"] = (133.42*compensationVolt*compensationVolt*compensationVolt - 255.86*compensationVolt*compensationVolt + 857.39*compensationVolt)*0.5 # Convert Voltage to tds value

            cursor.execute(
                "UPDATE EC_Sensor SET live_value = ? WHERE rowid = ?",
                (safe_round(sensor_state["tds"]), 1)
            )
            conn.commit()

        except KeyboardInterrupt:
            print("\nScript terminated by User.")

        conn.commit()
        conn.close()