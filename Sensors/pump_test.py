import time
from gpiozero import PWMLED
from gpiozero import LED

led_R = PWMLED(12)     # GPIO 12 (Pin 32)
led_Y = PWMLED(13)     # GPIO 13 (Pin 33)
led_G = LED(17)        # GPIO 17 (Pin 11)
