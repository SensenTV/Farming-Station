import time
from gpiozero import PWMLED
from gpiozero import LED


led_Y = PWMLED(6)     # GPIO 6 (Pin 31)


while True:

    led_Y.on()
