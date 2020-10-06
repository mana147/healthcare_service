import mysql.connector
import json


class Handle_Mysql:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def mydb(self):
        return mysql.connector.connect( self.host, self.user, self.password, self.database)


    def Select_table(self,  table_name):
        sql = "SELECT * FROM `" + table_name + "`"
        return sql


# ===========================================
# if __name__ == "__main__":
#     mycursor = mydb.cursor()
#     mycursor.execute(Select_table('users'))
#     myresult = mycursor.fetchall()

#     f = open("data.txt", "w+")

#     print(myresult[:])

#     for x in myresult:
#         # print( x )
#         f.write(str(x) + '\n')

#     f.close()

#     b = myresult[0][10]
#     # print(b)
#     obj = json.loads(b)
#     print(obj['list'][0])

# ===========================================
