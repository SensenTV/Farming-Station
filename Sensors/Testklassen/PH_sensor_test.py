import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Verbunden an ADS Channel 2
# Kalibrierungsmesswerte, erste Zahl Volt, zweite den Ph Wert
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
    
        print(f" Spannung: {avg_val:.3f} V")
        print(f" PH: {ph_val:.3f}")
        
        time.sleep(2.0)

except KeyboardInterrupt:
    print("\nScript terminated by User.")
