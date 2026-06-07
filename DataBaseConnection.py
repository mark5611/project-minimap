import datetime
import sqlite3
from pathlib import Path


class DataBaseConnection():
    def __init__(self):
        required_directory1 = Path("./decoded_data")
        required_directory1.mkdir(exist_ok=True)
        self.connection = sqlite3.connect('decoded_data/SpeedGuardDB.db')
        self.cursor = self.connection.cursor()
        self.create_database()

    def Query(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)
            return None

    def deleteAll(self, table):
        self.cursor.execute(f"DELETE FROM {table}")
        self.connection.commit()

    def resetDB(self):
        self.cursor.execute("DELETE FROM SPEED_CAMERA")
        self.cursor.execute("DELETE FROM ROAD")
        self.cursor.execute("DELETE FROM ROAD_COORDS")
        self.cursor.execute("DELETE FROM SESSIONS")
        self.cursor.execute("DELETE FROM DETECTIONS")
        self.cursor.execute("DELETE FROM REGION")
        self.cursor.execute("UPDATE SETTINGS SET EMPTY_DATABASE = 1")
        self.connection.commit()

    def create_database(self):
        self.cursor.executescript(f"""
            CREATE TABLE IF NOT EXISTS DETECTIONS (
                DETECTION_ID INTEGER,
                SESSION_ID   INTEGER,
                ROAD_ID      INTEGER,
                CAMERA_ID    INTEGER,
                TIMESTAMP    TEXT,
                TYPE         TEXT
            );
            CREATE TABLE IF NOT EXISTS REGION (
                REGION_ID    INTEGER PRIMARY KEY,
                NAME         TEXT,
                COUNTRY_CODE TEXT,
                LAST_UPDATED TEXT
            );
            CREATE TABLE IF NOT EXISTS ROAD (
                ROAD_ID   INTEGER,
                NAME      TEXT,
                MAX_SPEED INTEGER,
                REGION_ID INTEGER
            );
            CREATE TABLE IF NOT EXISTS ROAD_COORDS (
                COORD_ID INTEGER,
                ROAD_ID  INTEGER,
                LAT      REAL,
                LON      REAL
            );
            CREATE TABLE IF NOT EXISTS SESSIONS (
                SESSION       INTEGER,
                START_TIME    TEXT,
                END_TIME      TEXT,
                SUCCESS_COUNT INTEGER,
                FAIL_COUNT    INTEGER
            );
            CREATE TABLE IF NOT EXISTS SETTINGS (
                SETTING_ID             INTEGER PRIMARY KEY,
                CAMERA_DETECTION_RANGE INTEGER,
                COUNTRY_SELECTION      TEXT,
                VOICE_ALERT_PREFERENCE TEXT,
                EMPTY_DATABASE         BOOLEAN
            );
            CREATE TABLE IF NOT EXISTS SPEED_CAMERA (
                CAMERA_ID INTEGER,
                REGION_ID INTEGER,
                LAT       REAL,
                LON       REAL
            );

            INSERT OR IGNORE INTO SETTINGS (SETTING_ID, CAMERA_DETECTION_RANGE, COUNTRY_SELECTION, VOICE_ALERT_PREFERENCE, EMPTY_DATABASE)
            VALUES (1, 800, 'austria', 'male', 1);
        """)
        self.connection.commit()


if __name__ == "__main__":
    db = DataBaseConnection()
    db.resetDB()
    #db.deleteAll("REGION")
    #db.Query("INSERT INTO REGION VALUES (?, ?, ?, ?)", (None, "Austria", "AT", "2026-06-01"))
