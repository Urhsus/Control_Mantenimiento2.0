from extensions import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates
import re

class TimestampMixin:
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones
    repairs = db.relationship('Repair', backref='technician', lazy=True, cascade='all, delete-orphan')

    @validates('email')
    def validate_email(self, key, email):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError('Formato de email inválido')
        return email

    @validates('role')
    def validate_role(self, key, role):
        if role not in ['tecnico', 'supervisor', 'admin']:
            raise ValueError('Rol inválido')
        return role

    def set_password(self, password):
        if len(password) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_supervisor(self):
        return self.role in ['supervisor', 'admin']

    def is_technician(self):
        return self.role == 'tecnico'

    def __repr__(self):
        return f'<User {self.username}>'

class Part(TimestampMixin, db.Model):
    __tablename__ = 'parts'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    unit_cost = db.Column(db.Float, nullable=False)
    
    # Relaciones
    repairs = db.relationship('RepairPart', backref='part', lazy=True, cascade='all, delete-orphan')

    @validates('unit_cost')
    def validate_unit_cost(self, key, cost):
        if cost < 0:
            raise ValueError('El costo unitario no puede ser negativo')
        return cost

    @validates('code')
    def validate_code(self, key, code):
        if not code or not code.strip():
            raise ValueError('El código no puede estar vacío')
        return code.strip().upper()

    def __repr__(self):
        return f'<Part {self.code}>'

class Repair(TimestampMixin, db.Model):
    __tablename__ = 'repairs'
    
    id = db.Column(db.Integer, primary_key=True)
    technician_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    rov_code = db.Column(db.String(20), nullable=False, index=True)
    controller_code = db.Column(db.String(20), nullable=False)
    pilot_name = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(50), nullable=True)
    centro_cultivo = db.Column(db.String(100), nullable=True)
    repair_type = db.Column(db.String(20), nullable=False)
    reported_failure = db.Column(db.Text, nullable=False)
    observations = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pendiente')
    
    # Relaciones
    parts = db.relationship('RepairPart', backref='repair', lazy=True, cascade='all, delete-orphan')

    @validates('repair_type')
    def validate_repair_type(self, key, type_):
        if type_ not in ['preventiva', 'correctiva']:
            raise ValueError('Tipo de reparación inválido')
        return type_

    @validates('status')
    def validate_status(self, key, status):
        if status not in ['pendiente', 'en_proceso', 'completada', 'cancelada']:
            raise ValueError('Estado inválido')
        return status

    def __repr__(self):
        return f'<Repair {self.id} - ROV {self.rov_code}>'

class RepairPart(db.Model):
    __tablename__ = 'repair_parts'
    
    id = db.Column(db.Integer, primary_key=True)
    repair_id = db.Column(db.Integer, db.ForeignKey('repairs.id', ondelete='CASCADE'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost_at_time = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_repair_part', 'repair_id', 'part_id'),
    )

    @validates('quantity')
    def validate_quantity(self, key, quantity):
        if quantity <= 0:
            raise ValueError('La cantidad debe ser mayor que 0')
        return quantity

    @validates('unit_cost_at_time')
    def validate_unit_cost(self, key, cost):
        if cost < 0:
            raise ValueError('El costo unitario no puede ser negativo')
        return cost

    def __repr__(self):
        return f'<RepairPart {self.repair_id}:{self.part_id}>'
