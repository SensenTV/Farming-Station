import asyncio
import sqlite3
import datetime
import board
import adafruit_dht
from threading import Lock

# DHT11 Temperature and Humidity Sensor
# Verbunden an GPIO 17, Pin 11
dhtDevice = adafruit_dht.DHT11(board.D17)

sensor_state = {"humidity": None}

def update_sensor_state(key, value):
    """Aktualisiert einen Wert im sensor_state nur wenn er nicht None ist"""
    if value is not None:
        sensor_state[key] = value

def safe_round(value, ndigits=2):
    return round(value, ndigits) if value is not None else None

async def read_dht():
    """
    Liest den DHT11-Sensor aus und speichert den Wert in der DB.
    Diese Methode ist async, damit man sie mit asyncio aufrufen kann.
    """
    db_path = "./SQLite/sensors.db"
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    db_lock = Lock()

    with db_lock:
        try:
            update_sensor_state("humidity",dhtDevice.humidity)
            cursor.execute(
                "UPDATE Humidity_Sensor SET live_value = ? WHERE rowid = ?",
                (safe_round(sensor_state["humidity"]), 1)
            )
            conn.commit()
            print(f"[DHT11] Humidity aktualisiert: {sensor_state['humidity']}%")

        except RuntimeError as error:
            # Fehler treten beim DHT oft auf, einfach überspringen
            print(f"[DHT11] Fehler: {error.args[0]}")
            await asyncio.sleep(2.0)

        except KeyboardInterrupt:
            print("\n[DHT11] Script beendet vom User.")
            dhtDevice.exit()

        finally:
            conn.close()
            print("read_dht fertig")
