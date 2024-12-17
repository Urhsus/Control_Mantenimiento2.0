import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def create_database():
    try:
        # Conectar al servidor MySQL
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '')
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            # Crear la base de datos si no existe
            db_name = os.getenv('MYSQL_DB', 'mantenimiento')
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"Base de datos '{db_name}' creada o ya existente")

            # Usar la base de datos
            cursor.execute(f"USE {db_name}")
            
            print("Base de datos inicializada correctamente")
            
    except Error as e:
        print(f"Error mientras se conectaba a MySQL: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión a MySQL cerrada")

if __name__ == "__main__":
    create_database()
