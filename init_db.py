from app import create_app
from extensions import db
from models import User, Part, Repair, RepairPart

def init_db():
    app = create_app()
    with app.app_context():
        # Eliminar todas las tablas existentes
        db.drop_all()
        
        # Crear las nuevas tablas
        db.create_all()
        
        # Crear usuario admin por defecto
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('admin123')
        
        # Agregar el usuario admin a la base de datos
        db.session.add(admin)
        db.session.commit()
        
        print("Base de datos inicializada correctamente.")
        print("Usuario admin creado:")
        print("Username: admin")
        print("Password: admin123")

if __name__ == '__main__':
    init_db()
