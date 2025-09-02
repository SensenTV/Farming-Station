# date_deletion.py
import sqlite3
import datetime

def delete_old_data():
    db_path = r"C:\Users\steve\PycharmProjects\Farming-Station\SQLite\sensors.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Grenze berechnen
    grenze = datetime.datetime.now() - datetime.timedelta(days=365)

    # Tabellen, die bereinigt werden sollen
    tables = [
        "EC_Sensor",
        "Humidity_Sensor",
        "PH_Sensor",
        "Temp_Sensor",
        "Ultrasonic_Sensor",
    ]

    for table in tables:
        cursor.execute(f"""
            DELETE FROM {table}
            WHERE timestamp < ?
        """, (grenze,))

    conn.commit()
    conn.close()

