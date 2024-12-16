from extensions import db
from flask_login import UserMixin
from datetime import datetime
import secrets

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128))  # Contraseña almacenada (encriptada)
    role = db.Column(db.String(20), nullable=False)  # 'tecnico' o 'supervisor'
    repairs = db.relationship('Repair', backref='technician', lazy=True)

class ROV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    control_code = db.Column(db.String(20), nullable=False)
    equipment = db.Column(db.String(100), nullable=False)
    center = db.Column(db.String(100), nullable=False)
    repairs = db.relationship('Repair', backref='rov', lazy=True)

class Repair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rov_id = db.Column(db.Integer, db.ForeignKey('rov.id'), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pilot_name = db.Column(db.String(100), nullable=False)
    repair_type = db.Column(db.String(20), nullable=False)  # 'preventiva' o 'correctiva'
    reported_failure = db.Column(db.Text, nullable=False)
    observations = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='en_proceso')
    parts = db.relationship('RepairPart', backref='repair', lazy=True)

class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    unit_cost = db.Column(db.Float, nullable=False)
    repairs = db.relationship('RepairPart', backref='part', lazy=True)

class RepairPart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repair_id = db.Column(db.Integer, db.ForeignKey('repair.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost_at_time = db.Column(db.Float, nullable=False)
