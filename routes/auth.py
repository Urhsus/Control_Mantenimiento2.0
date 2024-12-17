from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Has iniciado sesión correctamente', 'success')
            return redirect(url_for('main.index'))
        flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Si hay usuarios en el sistema, verificar permisos
    if User.query.count() > 0:
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('No tienes permiso para registrar usuarios', 'error')
            return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        # Si es el primer usuario, asignar rol de admin
        role = request.form.get('role', 'admin' if User.query.count() == 0 else 'tecnico')
        
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'error')
            return render_template('auth/register.html')
            
        if User.query.filter_by(email=email).first():
            flash('El correo electrónico ya está registrado', 'error')
            return render_template('auth/register.html')
            
        user = User(
            username=username,
            email=email,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Usuario registrado exitosamente', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')
