import mysql.connector
import json

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="iot_database"
)

mycursor = mydb.cursor()

def Select_table(table_name):
    sql = "SELECT * FROM `" + table_name + "`"
    return sql


def Select_id(table_name, column_name, value):
    list_column = 'id,active,id_userhw,name,number,email,level,user_enable'
    
    sql =   'SELECT ' + list_column + \
            ' FROM ' + table_name + \
            ' WHERE ' + column_name + ' LIKE ' + '"'+value+'"'

    return sql


# ===========================================
if __name__ == "__main__":

    # thực thi lệnh sql
    mycursor.execute(Select_table('users'))
    # mycursor.execute(Select_id('users', 'id_userhw', 'us01hw01'))
    # lấy tất cả sau khi thực thi
    value = mycursor.fetchall()

    print(value)
    
    # if mycursor.fetchall() == 
