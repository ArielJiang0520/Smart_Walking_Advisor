import mysql.connector

class Database:
    def __init__(self):
        try:
            self.db = mysql.connector.connect(user='root', password='123456',
                                          host='127.0.0.1',
                                          database='cs125')
        except mysql.connector.Error as err:
          if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
          elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
          else:
            print(err)
        else:
          self.cursor = self.db.cursor()
