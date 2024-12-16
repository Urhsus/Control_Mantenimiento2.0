from app import create_app
from extensions import db
from models import User, ROV, Part
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_db():
    app = create_app()
    with app.app_context():
        # Crear todas las tablas
        db.create_all()

        # Crear usuario administrador inicial
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role='supervisor'
            )
            db.session.add(admin)

        # Crear algunos ROVs de ejemplo
        if not ROV.query.first():
            rovs = [
                ROV(code='ROV001', control_code='CTR001', equipment='ROV Surveyor', center='Centro Norte'),
                ROV(code='ROV002', control_code='CTR002', equipment='ROV Observer', center='Centro Sur'),
                ROV(code='ROV003', control_code='CTR003', equipment='ROV Explorer', center='Centro Este')
            ]
            for rov in rovs:
                db.session.add(rov)

        # Crear algunos repuestos de ejemplo
        if not Part.query.first():
            parts = [
                Part(code='P001', name='Motor principal', description='Motor eléctrico 24V', unit_cost=1500.00),
                Part(code='P002', name='Cámara HD', description='Cámara submarina HD', unit_cost=2500.00),
                Part(code='P003', name='Batería', description='Batería de litio 48V', unit_cost=800.00),
                Part(code='P004', name='Cable umbilical', description='Cable 100m', unit_cost=1200.00)
            ]
            for part in parts:
                db.session.add(part)

        db.session.commit()

if __name__ == '__main__':
    init_db()
    print("Base de datos inicializada con datos de ejemplo.")
