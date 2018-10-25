import mysql.connector

class Logger:
    dbstate = None

    def __init__(self):
        self.dbstate = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='',
            database='cars'
        )

    def log(self, message, type=""):
        try:
            cursor = self.dbstate.cursor()
            cursor.execute("INSERT INTO logs (type, message) VALUES (%s, %s);" % (type, message))
            self.dbstate.commit()
        except:
            print("Logger query fails")