import time

import board

import adafruit_dht

# DHT11 Temperature and Humidity Sensor
# Verbunden an GPIO 17, Pin 11
# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT11(board.D17)

while True:
    try:
        # Print the values to the serial port
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity
        print(f"Temp: {temperature_c:.1f} C    Humidity: {humidity}% ")

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    time.sleep(2.0)