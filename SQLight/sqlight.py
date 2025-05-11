import sqlite3

# Verbindung zur Datenbank
connection = sqlite3.connect('farming_station.db')
cursor = connection.cursor()

# Tabelle 'beispiel' erstellen
cursor.execute("""
    CREATE TABLE IF NOT EXISTS beispiel (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
""")

# Tabelle 'pH_Value' erstellen
cursor.execute("""
    CREATE TABLE IF NOT EXISTS pH_Value (
        pH_id INTEGER PRIMARY KEY,
        Value FLOAT,
        Timestamp TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS EC_Value (
        EC_id INTEGER PRIMARY KEY,
        Value FLOAT,
        Timestamp TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Temperature (
        temp_id INTEGER PRIMARY KEY,
        Value FLOAT,
        Timestamp TEXT
    )
""")

# Änderungen speichern und Verbindung schließen
connection.commit()
connection.close()
