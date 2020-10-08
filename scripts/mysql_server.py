import mysql.connector as mysql
import json


def Select_table(table_name):
    sql = "SELECT * FROM `" + table_name + "`"
    return sql


def Select_id(table_name, column_name, value):
    list_column = 'id,active,id_userhw,name,number,email,level,user_enable'
    
    sql =   'SELECT ' + list_column + \
            ' FROM ' + table_name + \
            ' WHERE ' + column_name + ' LIKE ' + '"'+value+'"'
    return sql

# def table_data():
#     print('table_data')
#     mycursor = config()
#     mycursor.execute(Select_table('users'))
#     value = mycursor.fetchall()
#     print(value)

# ===========================================
if __name__ == "__main__":
    # cursor.reset()

    mydb = mysql.connect(
        host="localhost",
        user="root",
        password="",
        database="iot_database")
    cursor = mydb.cursor()

    cursor.execute(Select_table('users'))
    data = cursor.fetchall()
    print(data)

    cursor.close()
    mydb.close()
