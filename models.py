from extensions import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'tecnico', 'supervisor' o 'admin'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    repairs = db.relationship('Repair', backref='technician', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_supervisor(self):
        return self.role == 'supervisor' or self.role == 'admin'

    def is_technician(self):
        return self.role == 'tecnico'

    @property
    def active(self):
        return self.is_active

    @active.setter
    def active(self, value):
        self.is_active = value

class Part(db.Model):
    __tablename__ = 'parts'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    unit_cost = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    repairs = db.relationship('RepairPart', backref='part', lazy=True)

class Repair(db.Model):
    __tablename__ = 'repairs'
    id = db.Column(db.Integer, primary_key=True)
    technician_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rov_code = db.Column(db.String(20), nullable=False)
    pilot_name = db.Column(db.String(100), nullable=False)
    repair_type = db.Column(db.String(20), nullable=False)  # 'preventiva' o 'correctiva'
    reported_failure = db.Column(db.Text, nullable=False)
    observations = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pendiente')
    controller_code = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    parts = db.relationship('RepairPart', backref='repair', lazy=True)

class RepairPart(db.Model):
    __tablename__ = 'repair_parts'
    id = db.Column(db.Integer, primary_key=True)
    repair_id = db.Column(db.Integer, db.ForeignKey('repairs.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost_at_time = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
