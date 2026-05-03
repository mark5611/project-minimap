import sqlite3

class DataBaseConnection():
    def __init__(self):
        self.connection = sqlite3.connect('decoded_data/SpeedGuardDB.db')
        self.cursor = self.connection.cursor()

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

if __name__ == "__main__":
    db = DataBaseConnection()
    db.resetDB()
