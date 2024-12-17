from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, User
from werkzeug.security import generate_password_hash
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/users')
@login_required
@admin_required
def users_list():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role')

            if not username or not email or not password or not role:
                flash('Todos los campos son requeridos', 'danger')
                return redirect(url_for('admin.new_user'))

            if User.query.filter_by(username=username).first():
                flash('El nombre de usuario ya existe', 'danger')
                return redirect(url_for('admin.new_user'))

            if User.query.filter_by(email=email).first():
                flash('El email ya está registrado', 'danger')
                return redirect(url_for('admin.new_user'))

            if role not in ['tecnico', 'supervisor', 'admin']:
                flash('Rol inválido', 'danger')
                return redirect(url_for('admin.new_user'))

            user = User(
                username=username,
                email=email,
                role=role,
                is_active=True
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()

            flash(f'Usuario {username} creado exitosamente', 'success')
            return redirect(url_for('admin.users_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear usuario: {str(e)}', 'danger')
            return redirect(url_for('admin.new_user'))

    return render_template('admin/new_user.html')

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        is_active = request.form.get('is_active') == 'on'
        
        # Verificar si el nuevo username ya existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user_id:
            flash('El nombre de usuario ya existe', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))

        # Verificar si el nuevo email ya existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user_id:
            flash('El email ya está registrado', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))

        user.username = username
        user.email = email
        user.role = role
        user.is_active = is_active

        # Si se proporciona una nueva contraseña, actualizarla
        new_password = request.form.get('password')
        if new_password:
            user.password_hash = generate_password_hash(new_password)

        db.session.commit()
        flash('Usuario actualizado exitosamente', 'success')
        return redirect(url_for('admin.users_list'))

    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/<int:user_id>/toggle_active', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('No puedes desactivar tu propia cuenta', 'danger')
    else:
        user.is_active = not user.is_active
        db.session.commit()
        status = 'activado' if user.is_active else 'desactivado'
        flash(f'Usuario {user.username} {status} exitosamente', 'success')
    return redirect(url_for('admin.users_list'))
