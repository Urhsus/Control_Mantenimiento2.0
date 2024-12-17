from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash
import os

def reset_database():
    app = create_app()
    
    with app.app_context():
        # Eliminar la base de datos existente
        db_path = os.path.join(app.instance_path, 'mantenimiento.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Base de datos eliminada: {db_path}")

        # Crear todas las tablas
        db.create_all()
        print("Tablas creadas exitosamente")

        # Crear usuario administrador por defecto
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),  # Cambiar esta contraseña
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        
        # Crear usuario supervisor de ejemplo
        supervisor = User(
            username='supervisor',
            email='supervisor@example.com',
            password_hash=generate_password_hash('supervisor123'),  # Cambiar esta contraseña
            role='supervisor',
            is_active=True
        )
        db.session.add(supervisor)
        
        # Crear usuario técnico de ejemplo
        tecnico = User(
            username='tecnico',
            email='tecnico@example.com',
            password_hash=generate_password_hash('tecnico123'),  # Cambiar esta contraseña
            role='tecnico',
            is_active=True
        )
        db.session.add(tecnico)
        
        db.session.commit()
        print("Usuarios por defecto creados exitosamente")
        print("\nCredenciales de acceso:")
        print("Admin - usuario: admin, contraseña: admin123")
        print("Supervisor - usuario: supervisor, contraseña: supervisor123")
        print("Técnico - usuario: tecnico, contraseña: tecnico123")

if __name__ == '__main__':
    reset_database()
