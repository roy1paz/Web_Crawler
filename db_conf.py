import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv('HOST')
ROOT = os.getenv('ROOT')
PASSWORD = os.getenv('PASSWORD')


def connect_mysql():
    try:
        connection = mysql.connector.connect(
            host=HOST,
            user=ROOT,
            password=PASSWORD
        )
        return connection
    except mysql.connector.Error as e:
        raise Exception(f'MySQL Connection not available: {e}')

