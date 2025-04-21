import mysql.connector
import os

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "mysql-hotel"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", "root"),
        database=os.getenv("DB_NAME", "mysql-hotel")
    )