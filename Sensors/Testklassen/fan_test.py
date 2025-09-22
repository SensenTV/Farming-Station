import time
from gpiozero import PWMOutputDevice

fan_pin = 26  # GPIO-Pin am HW-517
fan = PWMOutputDevice(fan_pin)  # automatisch über pigpio

while True:
    # Einschalten
    fan.value = 1.0  # Vollgas
    time.sleep(5)
