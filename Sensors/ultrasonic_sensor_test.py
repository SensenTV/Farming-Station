from Bluetin_Echo import Echo
import board
import time
import adafruit_hcsr04

# Define GPIO Pin
sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.D22, echo_pin=board.D27)

while True:
    try:
        print(sonar.distance, f"cm")
    except RuntimeError:
        print("Retrying!")
    time.sleep(1)