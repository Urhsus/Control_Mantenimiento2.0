import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    
    # Configurar la base de datos
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # Usar una ruta simple y directa para SQLite
    DB_PATH = os.path.join(basedir, 'mantenimiento.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Simplificar las opciones del motor
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280
    }
    
    # Configuración adicional
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
