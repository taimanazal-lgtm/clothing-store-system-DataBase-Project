import mysql.connector

#-------------------------
# MySQL Connection
#-------------------------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="2004",
        database="meraki"
    )


def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="2004",
        database="meraki"
    )
