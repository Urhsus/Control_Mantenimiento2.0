from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import db, Part
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

parts_bp = Blueprint('parts', __name__)

@parts_bp.route('/')
@login_required
def list_parts():
    try:
        parts = Part.query.all()
        return render_template('parts/list.html', parts=parts)
    except Exception as e:
        current_app.logger.error(f'Error al listar repuestos: {str(e)}', exc_info=True)
        flash('Error al cargar la lista de repuestos', 'error')
        return redirect(url_for('main.index'))

@parts_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_part():
    if not current_user.is_supervisor():
        flash('No tienes permiso para agregar repuestos', 'error')
        return redirect(url_for('parts.list_parts'))
        
    if request.method == 'POST':
        try:
            # Obtener y limpiar datos del formulario
            code = request.form.get('code', '').strip()
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip() or None
            unit_cost = request.form.get('unit_cost', '0').strip()

            current_app.logger.debug(f"Datos del formulario: code='{code}', name='{name}', description='{description}', unit_cost='{unit_cost}'")

            # Validación básica
            if not code or not name or not unit_cost:
                flash('Todos los campos marcados son requeridos', 'error')
                return render_template('parts/new.html')

            # Validar costo unitario
            try:
                unit_cost = float(unit_cost)
                if unit_cost < 0:
                    raise ValueError("El costo no puede ser negativo")
            except ValueError as e:
                current_app.logger.error(f"Error en costo unitario: {str(e)}")
                flash('El costo unitario debe ser un número válido y no negativo', 'error')
                return render_template('parts/new.html')

            # Verificar si el código ya existe
            existing_part = Part.query.filter_by(code=code).first()
            if existing_part:
                flash('El código de repuesto ya existe', 'error')
                return render_template('parts/new.html')
            
            # Crear el nuevo repuesto
            part = Part(
                code=code,
                name=name,
                description=description,
                unit_cost=unit_cost
            )
            
            db.session.add(part)
            db.session.commit()
            
            current_app.logger.info(f"Repuesto creado exitosamente: {code}")
            flash('Repuesto agregado exitosamente', 'success')
            return redirect(url_for('parts.list_parts'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al crear repuesto: {str(e)}", exc_info=True)
            flash('Error al crear el repuesto. Por favor, inténtalo de nuevo.', 'error')
            return render_template('parts/new.html')
        
    return render_template('parts/new.html')

@parts_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_part(id):
    if not current_user.is_supervisor():
        flash('No tienes permiso para editar repuestos', 'error')
        return redirect(url_for('parts.list_parts'))
    
    part = Part.query.get_or_404(id)
    
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        description = request.form.get('description')
        unit_cost = request.form.get('unit_cost')
        
        current_app.logger.debug(f"Datos del formulario: code='{code}', name='{name}', description='{description}', unit_cost='{unit_cost}'")

        # Verificar si el código ya existe (excluyendo el repuesto actual)
        existing_part = Part.query.filter(Part.code == code, Part.id != id).first()
        if existing_part:
            flash('El código de repuesto ya existe', 'error')
            return render_template('parts/edit.html', part=part)
            
        try:
            unit_cost = float(unit_cost)
        except ValueError as e:
            current_app.logger.error(f"Error en costo unitario: {str(e)}")
            flash('El costo unitario debe ser un número válido', 'error')
            return render_template('parts/edit.html', part=part)
            
        part.code = code
        part.name = name
        part.description = description
        part.unit_cost = unit_cost
        
        db.session.commit()
        current_app.logger.info(f"Repuesto actualizado exitosamente: {code}")
        
        flash('Repuesto actualizado exitosamente', 'success')
        return redirect(url_for('parts.list_parts'))
    
    return render_template('parts/edit.html', part=part)

@parts_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_part(id):
    if not current_user.is_supervisor():
        flash('No tienes permiso para eliminar repuestos', 'error')
        return redirect(url_for('parts.list_parts'))
    
    part = Part.query.get_or_404(id)
    
    db.session.delete(part)
    db.session.commit()
    current_app.logger.info(f"Repuesto eliminado exitosamente: {id}")
    
    flash('Repuesto eliminado exitosamente', 'success')
    return redirect(url_for('parts.list_parts'))
