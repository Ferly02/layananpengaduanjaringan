import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
    )
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS sinar;")
    connection.commit()
    print("Database 'sinar' created successfully or already exists.")
except Exception as e:
    print(f"Error connecting to MySQL or creating database: {e}")
finally:
    if 'connection' in locals() and connection.open:
        connection.close()
