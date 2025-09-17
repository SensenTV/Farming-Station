from w1thermsensor import W1ThermSensor
import time

# DS18B20 Sensor für Temperatur
# Verbunden an GPIO 4 Pin 7


while True:
    try:
        sensor = W1ThermSensor()
        temperature = sensor.get_temperature()  # Standard ist °C
        print(f"Temperatur: {temperature:.2f} °C")

        time.sleep(1)

    except KeyboardInterrupt:
        print("\nScript terminated by User.")
        break

