import time
import board
import busio
import adafruit_dht
import Adafruit_ADS1x15
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_hcsr04

# DS18b20 Temperatur Sensor wird nicht mit one-wire im system erkannt
# GR-CP6 G3 Water Flow Sensor braucht Resistor um auf 3.3v zu kommen 

def dht_sensor():

    # DHT11 Temperature and Humidity Sensor
    # Initial the dht device, with data pin connected to:
    dhtDevice = adafruit_dht.DHT11(board.D4)

    while True:
        try:
            # Print the values to the serial port
            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity
            print(f"Temp: {temperature_c:.1f} C    Humidity: {humidity}% ")

        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)
            continue
        except KeyboardInterrupt:
            print("\nScript terminated by User.")
            dhtDevice.exit()
        except Exception as error:
            dhtDevice.exit()
            raise error

        time.sleep(2.0)

def water_sensor():

    # Water Sensor
    # Initial the Device
    ADC = Adafruit_ADS1x15.ADS1115(busnum= 1)
    ADC_Channel = 3
    Gain = 1
    Min_ADC_Value = 0
    Max_ADC_Value = 32767 

    while True:
        try:
            # Read ADC Value
            adc_value = ADC.read_adc(ADC_Channel, gain=Gain)

            #Convert ADC Value to water level percentage
            water_level = (adc_value - Min_ADC_Value) / (Max_ADC_Value - Min_ADC_Value) * 100

            print(f"ADC Value: {adc_value} | Water Level: {water_level:.2f}%")

        except KeyboardInterrupt:
            print("\nScript terminated by User.")

        time.sleep(1)

def ultrasonic_sensor():

    # Ultrasonic Sensor for Water level
    # Initial Device
    sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.D22, echo_pin=board.D27)

    while True:
        try:
            print(sonar.distance, f"cm")
        except RuntimeError:
            print("Retrying!")
        except KeyboardInterrupt:
            print("\nScript terminated by User.")

        time.sleep(1)

def ph_sensor():

    #PH Sensor
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

    try:
        while True:
            for i in range(10):
                chan = AnalogIn(ads,ADS.P0)
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
        
            print(f" Spannung: {avg_val:.3f} V")
            print(f" PH: {ph_val:.3f}")
            
            time.sleep(2.0)

    except KeyboardInterrupt:
        print("\nScript terminated by User.")

ph_sensor()