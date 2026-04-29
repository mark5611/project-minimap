import sqlite3

class DataBaseConnection:
    def __init__(self):
        self.connection = sqlite3.connect('SpeedGuardDB.db')
        self.cursor = self.connection.cursor()

    def Query(self, query):
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            print(result)
        except Exception as e:
            print(e)
        finally:
            self.connection.close()
            self.cursor.close()
