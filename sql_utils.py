from db_conf import *
from web_crawler import read_json, POSITIONS_DATA_DIR


def create_db():
    connection = connect_mysql()
    cursor = connection.cursor()
    # Create the JOBS database
    cursor.execute('CREATE DATABASE IF NOT EXISTS JOBS')
    connection.commit()
    cursor.close()
    connection.close()


def create_table():
    connection = connect_mysql()
    cursor = connection.cursor()
    # Switch to the JOBS database
    cursor.execute('USE JOBS')
    # Create the JOBS table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS JOBS (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            country VARCHAR(100) NOT NULL,
            city VARCHAR(100) NOT NULL,
            description TEXT
        )
    ''')
    connection.commit()
    cursor.close()
    connection.close()


def insert_into_mysql(files_path=POSITIONS_DATA_DIR):
    connection = connect_mysql()
    cursor = connection.cursor()
    cursor.execute('USE JOBS')
    query = 'INSERT INTO JOBS (title, country, city, description) VALUES (%s, %s, %s, %s)'
    for file in os.listdir(files_path):
        file_path = os.path.join(files_path, file)
        data = read_json(file_path)
        values = (data['name'], data['country'], data['city'], data['description'])
        cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()


