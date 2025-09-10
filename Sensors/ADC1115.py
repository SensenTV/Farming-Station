
# cd ~/Desktop/Python/sensoren_test
# Virtual Enviorment und so
# mkdir Ordnername              zum Ordner erschaffen
# cd sensorTest_DHT11
# python3 -m venv venv          zum Enviorment erschaffen
# source venv/bin/activate      zum rein gehen 
# deactivate

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


i2c = busio.I2C(board.SCL,board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1
chan = AnalogIn(ads,ADS.P0)

while True:
    print(f"Voltage: {chan.voltage}V")
    
    cmd = input("")
    if cmd.lower() == 'e':
        print("Programm Beendet")
        break
