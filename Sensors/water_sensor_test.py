import time
import Adafruit_ADS1x15

# Water Sensor
# Initial the Device
ADC = Adafruit_ADS1x15.ADS1115(busnum= 1)
ADC_CHANNEL = 3
GAIN = 1
Min_ADC_Value = 0
Max_ADC_Value = 32767 


try:
    while True:
        # Read ADC Value
        adc_value = ADC.read_adc(ADC_CHANNEL, gain=GAIN)

        #Convert ADC Value to water level percentage
        water_level = (adc_value - Min_ADC_Value) / (Max_ADC_Value - Min_ADC_Value) * 100

        print(f"ADC Value: {adc_value} | Water Level: {water_level:.2f}%")

        time.sleep(2.0)

except KeyboardInterrupt:
    print("\nScript terminated by User.")