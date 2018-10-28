import mysql.connector

import crawler.config as cnfg

class Logger:
    dbstate = None

    def __init__(self):
        self.dbstate = mysql.connector.connect(
            host=cnfg.MYSQL_CONFIG['host'],
            port=cnfg.MYSQL_CONFIG['port'],
            user=cnfg.MYSQL_CONFIG['user'],
            passwd=cnfg.MYSQL_CONFIG['password'],
            database=cnfg.MYSQL_CONFIG['dbname']
        )

    def log(self, message, type=""):
        try:
            cursor = self.dbstate.cursor()
            cursor.execute("INSERT INTO logs (type, message) VALUES (%s, %s);", (type, message))
            self.dbstate.commit()
        except:
            print("Logger query fails")
