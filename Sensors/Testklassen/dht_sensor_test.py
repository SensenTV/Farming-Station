import asyncio
import sqlite3
import board
import adafruit_dht

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


db_lock = asyncio.Lock()
conn = sqlite3.connect("./SQLite/sensors.db", check_same_thread=False)
cursor = conn.cursor()


async def safe_db_execute(query, params=()):
    async with db_lock:
        cursor.execute(query, params)
        conn.commit()


async def read_dht():
    """
    Liest den DHT11-Sensor aus und speichert den Wert in der DB.
    Diese Methode ist async, damit man sie mit asyncio aufrufen kann.
    """
    try:
        # Sensorwert holen
        humidity = dhtDevice.humidity

        # Nur speichern, wenn der Sensor einen gültigen Wert liefert
        if humidity is not None:
            update_sensor_state("humidity", humidity)

            # Wert in die Datenbank schreiben (UPDATE auf erste Zeile)
            await safe_db_execute(
                "UPDATE Humidity_Sensor SET live_value = ? WHERE rowid = ?",
                (safe_round(sensor_state["humidity"]), 1)
            )
            print(
                f"[DHT11] Humidity aktualisiert: {sensor_state['humidity']}%")
        else:
            # Sensor hat None zurückgegeben → alten Wert behalten
            print("[DHT11] Kein gültiger Wert erhalten (None) → behalte alten Wert")

    except RuntimeError as error:
        # Fehler treten beim DHT oft auf, einfach überspringen
        print(f"[DHT11] Fehler: {error.args[0]}")
        await asyncio.sleep(2.0)

    except KeyboardInterrupt:
        print("\n[DHT11] Script beendet vom User.")
        dhtDevice.exit()

    finally:
        print("read_dht fertig")
