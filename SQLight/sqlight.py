import sqlite3

connection = sqlite3.connect('farming_station.db')
cursor = connection.cursor()

cursor.execute(""
               "CREATE TABLE IF NOT EXISTS beispiel "
               "( id INTEGER PRIMARY KEY, "
               "name TEXT)")

cursor.execute(""
               "CREATE TABLE IF NOT EXISTS pH_Value"
               "(pH_id INTEGER PRIMARY KEY,"
               "Value FLOAT,"
               "Timestamp SMALLDATETIME)")

connection.commit()
connection.close()