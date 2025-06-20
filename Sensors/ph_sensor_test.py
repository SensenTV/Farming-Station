import time
import Adafruit_ADS1x15

# PH Sensor
# Initial the Device
ADC = Adafruit_ADS1x15.ADS1115(busnum= 1)
ADC_CHANNEL = 2

try:
    while True:
        # Read ADC  Value
        adc_value = ADC.read_adc(ADC_CHANNEL)

        # Convert to millivolt
        volt = adc_value*5.0/1024/6

        #Convert to ph
        ph_value = volt

        print(f"PH Value: {adc_value}")

        time.sleep(2.0)

except KeyboardInterrupt:
    print("\nScript terminated by User.")