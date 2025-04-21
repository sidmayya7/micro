import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="mysql-hotel",  # this should match your container name
        user="root",
        password="root",
        database="hotel_db"
    )
