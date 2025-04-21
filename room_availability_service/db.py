import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="mysql-hotel",  # name of the MySQL service in Docker
        user="root",
        password="root",
        database="hotel_db"
    )
