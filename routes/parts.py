from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from models import db, Part
import logging
import pandas as pd
from werkzeug.utils import secure_filename
import os

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

@parts_bp.route('/template')
@login_required
def download_template():
    if not current_user.is_supervisor():
        flash('No tienes permiso para descargar la plantilla', 'error')
        return redirect(url_for('parts.list_parts'))
    
    try:
        # Crear un DataFrame de ejemplo
        df = pd.DataFrame({
            'code': ['ROV001', 'ROV002', 'ROV003'],
            'name': ['Motor DC', 'Sensor Temp', 'Cable USB'],
            'description': ['Motor 12V para ROV', 'Sensor de temperatura', 'Cable USB tipo C'],
            'unit_cost': [150.00, 75.50, 25.00]
        })
        
        # Guardar el DataFrame como Excel
        template_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'template_repuestos.xlsx')
        df.to_excel(template_path, index=False)
        
        return send_file(template_path, as_attachment=True, download_name='plantilla_repuestos.xlsx')
    except Exception as e:
        current_app.logger.error(f'Error al crear plantilla: {str(e)}')
        flash('Error al generar la plantilla', 'error')
        return redirect(url_for('parts.list_parts'))

@parts_bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_parts():
    if not current_user.is_supervisor():
        flash('No tienes permiso para importar repuestos', 'error')
        return redirect(url_for('parts.list_parts'))
        
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
            
        if not file.filename.endswith('.xlsx'):
            flash('El archivo debe ser un Excel (.xlsx)', 'error')
            return redirect(request.url)
            
        try:
            # Leer el archivo Excel
            df = pd.read_excel(file)
            
            # Verificar las columnas requeridas
            required_columns = ['code', 'name', 'unit_cost']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                flash(f'Faltan las siguientes columnas: {", ".join(missing_columns)}', 'error')
                return redirect(request.url)
            
            success_count = 0
            error_count = 0
            
            # Procesar cada fila
            for index, row in df.iterrows():
                try:
                    # Verificar si el código ya existe
                    existing_part = Part.query.filter_by(code=str(row['code']).strip()).first()
                    if existing_part:
                        current_app.logger.warning(f"Código duplicado: {row['code']}")
                        error_count += 1
                        continue
                    
                    # Crear nuevo repuesto
                    part = Part(
                        code=str(row['code']).strip(),
                        name=str(row['name']).strip(),
                        description=str(row.get('description', '')).strip() if 'description' in row else None,
                        unit_cost=float(row['unit_cost'])
                    )
                    db.session.add(part)
                    success_count += 1
                    
                except Exception as e:
                    current_app.logger.error(f"Error en la fila {index + 2}: {str(e)}")
                    error_count += 1
                    continue
            
            db.session.commit()
            flash(f'Importación completada. {success_count} repuestos importados exitosamente. {error_count} errores.', 'success')
            return redirect(url_for('parts.list_parts'))
            
        except Exception as e:
            current_app.logger.error(f"Error al procesar el archivo: {str(e)}")
            flash('Error al procesar el archivo. Verifica el formato.', 'error')
            return redirect(request.url)
    
    return render_template('parts/import.html')
