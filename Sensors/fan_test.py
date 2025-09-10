import time
from gpiozero import DigitalOutputDevice

fan = DigitalOutputDevice(26) #GPIO26 Pin 37

fan.on()
print(fan.value)
time.sleep(5)
fan.off()


