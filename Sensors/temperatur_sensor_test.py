
# cd ~/Desktop/Python/sensoren_test
# source venv/bin/activate
# python3 DS18B20.py

from w1thermsensor import W1ThermSensor
import time

while True:
    try:
        sensor = W1ThermSensor()
        temperature = sensor.get_temperature()  # Standard ist °C
        print(f"Temperatur: {temperature:.2f} °C")

        time.sleep(1)

    except KeyboardInterrupt:
        print("\nScript terminated by User.")
        break

