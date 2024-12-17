import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    
    # Configurar la base de datos
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # En Render, usar el directorio /tmp para la base de datos
    if os.environ.get('RENDER'):
        DB_PATH = '/tmp/mantenimiento.db'
    else:
        DB_PATH = os.path.join(basedir, 'mantenimiento.db')
    
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración del pool de conexiones
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280
    }
    
    # Configuración adicional
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
