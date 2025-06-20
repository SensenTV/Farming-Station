import time
import board
import adafruit_dht
import Adafruit_ADS1x15
import adafruit_hcsr04

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

ultrasonic_sensor()