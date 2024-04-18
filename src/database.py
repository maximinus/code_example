import time
import pickle
import sqlite3

from pathlib import Path
from datetime import datetime


DATABASE_FILE = Path(__file__).parent.parent / 'ingestion.db'
print(str(DATABASE_FILE))
ALLOWABLE_WRITE_RETRIES = 20


CREATE_TABLE_INTEGER_READS = """
CREATE TABLE IF NOT EXISTS integer_entries (
    id INTEGER PRIMARY KEY,
    start_datetime DATETIME,
    name TEXT,
    frequency FLOAT
)
"""

CREATE_TABLE_INTEGER_DATA = """
CREATE TABLE IF NOT EXISTS integer_data (
    id INTEGER PRIMARY KEY,
    data BLOB,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    integer_entries_id INTEGER,
    FOREIGN KEY(integer_entries_id) REFERENCES integer_entries(id)
)
"""

GET_SENSOR_DATA = """
SELECT integer_data.*
FROM integer_data
JOIN integer_entries ON integer_data.integer_entries_id = integer_entries.id
WHERE integer_entries.name = "{sensor_name}"
ORDER BY integer_data.created DESC
LIMIT 1;
"""

TABLES = [('integer_entries', CREATE_TABLE_INTEGER_READS),
          ('integer_data', CREATE_TABLE_INTEGER_DATA)]


def get_existing_sensors():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT name FROM integer_entries ORDER BY name")
    except sqlite3.OperationalError as ex:
        # no table maybe; anyhow, no sensors for us
        print(f'Error: {ex}')
        return []
    # sqlite returns a list of tuples, we only need the first entry in that tuple
    return [x[0] for x in cursor.fetchall()]


def get_last_data(sensor_name):
    # get the last entry of sensor data
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    sql_command = GET_SENSOR_DATA.replace('{sensor_name}', sensor_name)
    cursor.execute(sql_command)
    pickled_data = cursor.fetchall()[0]
    return pickle.loads(pickled_data[1])


def create_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    for table in TABLES:
        cursor.execute(table[1])
    conn.close()


def create_ingestion_point(self, ingestion_name, frequency):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO integer_entries (start_datetime, name, frequency) VALUES (?, ?, ?)',
                   (datetime.now(), ingestion_name, float(frequency)))
    conn.commit()
    conn.close()
    return cursor.lastrowid


def write_binary_data(table_id, data):
    # returns False if the table does not exist, or too many attempts were made
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    serialised_data = pickle.dumps(data)
    for _ in range(ALLOWABLE_WRITE_RETRIES):
        try:
            cursor.execute('INSERT INTO integer_data (integer_entries_id, data) VALUES (?, ?)',
                           (table_id, serialised_data))
            conn.commit()
            conn.close()
            return True
        except sqlite3.OperationalError as ex:
            # could be blocked, sleep a little and try again
            print(f'DB Error: {ex}')
            time.sleep(0.02)
    return False
