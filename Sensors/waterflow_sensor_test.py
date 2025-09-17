# untested
import time
import board
from gpiozero import InputDevice

# Verbunden an GPIO 24 Pin 18
waterflow = InputDevice(24)

try:
    while True:
        print(waterflow.value)
        time.sleep(1.0)

except KeyboardInterrupt:
    print("\nScript terminated by User.")