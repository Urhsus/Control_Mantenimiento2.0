from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Part

parts_bp = Blueprint('parts', __name__)

@parts_bp.route('/parts')
@login_required
def list_parts():
    parts = Part.query.all()
    return render_template('parts/list.html', parts=parts)

@parts_bp.route('/parts/new', methods=['GET', 'POST'])
@login_required
def new_part():
    if not current_user.is_supervisor():
        flash('No tienes permiso para agregar repuestos', 'error')
        return redirect(url_for('parts.list_parts'))
        
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        description = request.form.get('description')
        unit_cost = request.form.get('unit_cost')
        
        if Part.query.filter_by(code=code).first():
            flash('El código de repuesto ya existe', 'error')
            return render_template('parts/new.html')
            
        part = Part(
            code=code,
            name=name,
            description=description,
            unit_cost=float(unit_cost)
        )
        
        db.session.add(part)
        db.session.commit()
        
        flash('Repuesto agregado exitosamente', 'success')
        return redirect(url_for('parts.list_parts'))
        
    return render_template('parts/new.html')

@parts_bp.route('/parts/<int:id>/edit', methods=['GET', 'POST'])
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
        
        # Verificar si el código ya existe (excluyendo el repuesto actual)
        existing_part = Part.query.filter(Part.code == code, Part.id != id).first()
        if existing_part:
            flash('El código de repuesto ya existe', 'error')
            return render_template('parts/edit.html', part=part)
            
        part.code = code
        part.name = name
        part.description = description
        part.unit_cost = float(unit_cost)
        
        db.session.commit()
        
        flash('Repuesto actualizado exitosamente', 'success')
        return redirect(url_for('parts.list_parts'))
        
    return render_template('parts/edit.html', part=part)

@parts_bp.route('/parts/<int:id>/delete', methods=['POST'])
@login_required
def delete_part(id):
    if not current_user.is_supervisor():
        flash('No tienes permiso para eliminar repuestos', 'error')
        return redirect(url_for('parts.list_parts'))
        
    part = Part.query.get_or_404(id)
    
    db.session.delete(part)
    db.session.commit()
    
    flash('Repuesto eliminado exitosamente', 'success')
    return redirect(url_for('parts.list_parts'))
