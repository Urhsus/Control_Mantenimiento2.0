from app import create_app, db
from models import *  # Importa todos tus modelos
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

def migrate_data():
    # Cargar variables de entorno
    load_dotenv()
    
    # Crear la aplicación
    app = create_app()
    
    with app.app_context():
        # Crear todas las tablas en PostgreSQL
        db.create_all()
        
        # Configurar la conexión a SQLite (base de datos original)
        sqlite_path = os.path.join(app.instance_path, 'mantenimiento.db')
        sqlite_uri = f'sqlite:///{sqlite_path}'
        sqlite_engine = create_engine(sqlite_uri)
        
        # Obtener todos los modelos de SQLAlchemy
        models = db.Model._decl_class_registry.values()
        models = [m for m in models if hasattr(m, '__tablename__')]
        
        # Migrar datos tabla por tabla
        for Model in models:
            print(f"Migrando {Model.__tablename__}...")
            # Leer datos de SQLite
            with sqlite_engine.connect() as sqlite_conn:
                data = sqlite_conn.execute(f"SELECT * FROM {Model.__tablename__}").fetchall()
                columns = sqlite_conn.execute(f"SELECT * FROM {Model.__tablename__} LIMIT 1").keys()
            
            # Insertar datos en PostgreSQL
            if data:
                insert_data = [dict(zip(columns, row)) for row in data]
                db.session.bulk_insert_mappings(Model, insert_data)
                db.session.commit()
                print(f"  - {len(data)} registros migrados")
            else:
                print("  - No hay datos para migrar")

if __name__ == '__main__':
    migrate_data()
