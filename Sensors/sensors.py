import time
import board
import adafruit_dht
import Adafruit_ADS1x15

# DHT11 Temperature and Humidity Sensor
# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT11(board.D4)
# Water Sensor
# Initial the Device
ADC = Adafruit_ADS1x15.ADS1115(busnum= 1)
ADC_Channel = 3
Gain = 1
Min_ADC_Value = 0
Max_ADC_Value = 32767 

def dht_sensor():
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
        #except Exception as error:
            #dhtDevice.exit()
            #raise error

        time.sleep(2.0)

def water_sensor():
    try:
        while True:
            # Read ADC Value
            adc_value = ADC.read_adc(ADC_Channel, gain=Gain)

            #Convert ADC Value to water level percentage
            water_level = (adc_value - Min_ADC_Value) / (Max_ADC_Value - Min_ADC_Value) * 100

            print(f"ADC Value: {adc_value} | Water Level: {water_level:.2f}%")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nScript terminated by User.")