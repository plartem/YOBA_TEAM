import mysql.connector

import config

class Logger:
    dbstate = None

    def __init__(self):
        self.dbstate = mysql.connector.connect(
            host=config.MYSQL_CONFIG['host'],
            port=config.MYSQL_CONFIG['port'],
            user=config.MYSQL_CONFIG['user'],
            passwd=config.MYSQL_CONFIG['password'],
            database=config.MYSQL_CONFIG['dbname']
        )

    def log(self, message, type=""):
        try:
            cursor = self.dbstate.cursor()
            cursor.execute("INSERT INTO logs (type, message) VALUES (%s, %s);", (type, message))
            self.dbstate.commit()
        except:
            print("Logger query fails")