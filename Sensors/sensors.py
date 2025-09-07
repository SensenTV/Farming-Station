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

# DS18b20 Temperatur Sensor wird nicht mit one-wire im system erkannt
# GR-CP6 G3 Water Flow Sensor braucht Resistor um auf 3.3v zu kommen 

# Macht Werte in die Datenbank nach 2 Stunden
def add_to_db():
            cursor.execute("INSERT INTO Humidity_Sensor VALUES (humidity, datetime.datetime.now, humidity)")
            cursor.execute("INSERT INTO WaterLevel_Sensor VALUES (water_level, datetime.datetime.now, water_level)")
            cursor.execute("INSERT INTO Ultrasonic_Sensor VALUES (sonar.distance, datetime.datetime.now, sonar.distance)")
            cursor.execute("INSERT INTO PH_Sensor VALUES (ph_val, datetime.datetime.now, ph_val)")
            cursor.execute("INSERT INTO EC_Sensor VALUES (tds_value, datetime.datetime.now, tds_value)")

def sensor_activate():
    # SQL Initialisieren
    db_path = "./SQLite/sensors.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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
    sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.D22, echo_pin=board.D27)

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



    while True:

        # DHT11 Temperature and Humidity Sensor
        try:
            # Print the values to the serial port
            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity
            cursor.execute("UPDATE Humidity_Sensor SET live_value = ? Where rowid = ?",(humidity,1))
            

        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)
            continue
        except KeyboardInterrupt:
            print("\nScript terminated by User.")
            dhtDevice.exit()
        

        # Water Sensor
        try:
            # Read ADC Value
            adc_value = ADC.read_adc(ADC_Channel, gain=Gain)

            #Convert ADC Value to water level percentage
            water_level = (adc_value - Min_ADC_Value) / (Max_ADC_Value - Min_ADC_Value) * 100

            cursor.execute("UPDATE WaterLevel_Sensor SET live_value = ? WHERE rowid = ?",(water_level,1))

        except KeyboardInterrupt:
            print("\nScript terminated by User.")

        # Ultrasonic Sensor for Water level
        try:
            cursor.execute("UPDATE Ultrasonic_Sensor SET live_value = ? WHERE rowid = ?",(sonar.distance,1))

        except RuntimeError:
            print("Retrying!")
        except KeyboardInterrupt:
            print("\nScript terminated by User.")

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
            ph_val = cali_m * avg_val + cali_y - 1.95

            cursor.execute("UPDATE PH_Sensor SET live_value = ? WHERE rowid = ?",(ph_val,1))

        except KeyboardInterrupt:
            print("\nScript terminated by User.")

        # TDS Sensor
        try:
            # Read ADC Value
            adc_value = AnalogIn(ads,ADS.P1)

            compensationCoefficient = 1.0 + 0.02 * (temperature - 25.0)

            compensationVolt = adc_value.voltage/compensationCoefficient

            tds_value = (133.42*compensationVolt*compensationVolt*compensationVolt - 255.86*compensationVolt*compensationVolt + 857.39*compensationVolt)*0.5 # Convert Voltage to tds value

            cursor.execute("UPDATE EC_Sensor SET live_value = ? WHERE rowid = ?",(tds_value,1))

        except KeyboardInterrupt:
            print("\nScript terminated by User.")

        # 2 Stunden in ms = 7200000
        #self.after(7200000, add_to_db)

        conn.commit()
        time.sleep(1.0)