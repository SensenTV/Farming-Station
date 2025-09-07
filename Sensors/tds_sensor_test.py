import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# TDS Sensor
#Verbunden mit ADS Channel 1
# Initial the Device
i2c = busio.I2C(board.SCL,board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1
temperature = 25

try:
    while True:
        # Read ADC Value
        adc_value = AnalogIn(ads,ADS.P1)

        compensationCoefficient = 1.0 + 0.02 * (temperature - 25.0)

        compensationVolt = adc_value.voltage/compensationCoefficient

        tds_value = (133.42*compensationVolt*compensationVolt*compensationVolt - 255.86*compensationVolt*compensationVolt + 857.39*compensationVolt)*0.5 # Convert Voltage to tds value

        print(f"TDS Value: {tds_value} ppm")
        print(f"adcvalue Value: {adc_value.voltage}")

        time.sleep(2.0)

except KeyboardInterrupt:
    print("\nScript terminated by User.")