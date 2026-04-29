import sqlite3

class DataBaseConnection:
    def __init__(self):
        self.connection = sqlite3.connect('SpeedGuardDB.db')
        self.cursor = self.connection.cursor()

    def selectQuery(self, query):
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        finally:'''
            self.connection.close()
            self.cursor.close()'''

    def addQuery(self, query):
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        finally:'''
            self.connection.close()
            self.cursor.close()'''

    def otherQuery(self, query: str):
        try:
            self.cursor.execute(query)
            print("Completed successfully")
        except Exception as e:
            print("Error while creating table: ", e)
        finally:'''
            self.connection.close()
            self.cursor.close()'''


if __name__ == '__main__':
    db = DataBaseConnection()