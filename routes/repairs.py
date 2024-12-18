from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from models import db, Repair, Part, RepairPart
from datetime import datetime
import openpyxl
from io import BytesIO

repairs_bp = Blueprint('repairs', __name__, url_prefix='/repairs')

@repairs_bp.route('/')
@login_required
def repairs_list():
    repairs = Repair.query.all()
    return render_template('repairs/list.html', repairs=repairs)

@repairs_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_repair():
    # Obtener la lista de partes al inicio de la función
    parts = Part.query.all()
    
    if request.method == 'POST':
        try:
            repair = Repair(
                rov_code=request.form['rov_code'],
                pilot_name=request.form['pilot_name'],
                repair_type=request.form['repair_type'],
                reported_failure=request.form['reported_failure'],
                observations=request.form.get('observations', ''),
                controller_code=request.form['controller_code'],
                team=request.form['team'],
                centro_cultivo=request.form['centro_cultivo'],
                technician_id=current_user.id,
                status='pendiente',
                start_date=datetime.now()
            )
            db.session.add(repair)
            db.session.commit()

            # Procesar los repuestos seleccionados
            parts_list = request.form.getlist('parts[]')
            quantities = request.form.getlist('quantities[]')
            
            for part_id, quantity in zip(parts_list, quantities):
                if part_id and quantity and int(quantity) > 0:
                    part = Part.query.get(int(part_id))
                    if part:
                        repair_part = RepairPart(
                            repair_id=repair.id,
                            part_id=part.id,
                            quantity=int(quantity),
                            unit_cost_at_time=part.unit_cost
                        )
                        db.session.add(repair_part)
            
            db.session.commit()
            flash('Reparación creada exitosamente', 'success')
            return redirect(url_for('repairs.repairs_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la reparación: {str(e)}', 'error')
            return render_template('repairs/new.html', parts=parts), 400
    
    # GET request
    return render_template('repairs/new.html', parts=parts)

@repairs_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_repair(id):
    repair = Repair.query.get_or_404(id)
    if request.method == 'POST':
        repair.rov_code = request.form['rov_code']
        repair.pilot_name = request.form['pilot_name']
        repair.repair_type = request.form['repair_type']
        repair.reported_failure = request.form['reported_failure']
        repair.observations = request.form.get('observations', '')
        repair.controller_code = request.form['controller_code']
        repair.status = request.form['status']
        if request.form['status'] == 'completada':
            repair.end_date = datetime.now()
        db.session.commit()
        flash('Reparación actualizada exitosamente', 'success')
        return redirect(url_for('repairs.repairs_list'))
    return render_template('repairs/edit.html', repair=repair)

@repairs_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_repair(id):
    if not current_user.is_supervisor():
        flash('No tienes permiso para eliminar reparaciones', 'error')
        return redirect(url_for('repairs.repairs_list'))
    repair = Repair.query.get_or_404(id)
    db.session.delete(repair)
    db.session.commit()
    flash('Reparación eliminada exitosamente', 'success')
    return redirect(url_for('repairs.repairs_list'))

@repairs_bp.route('/export-excel')
@login_required
def export_excel():
    if not current_user.is_supervisor():
        flash('No tienes permiso para exportar reparaciones', 'error')
        return redirect(url_for('repairs.repairs_list'))

    # Crear un nuevo libro de trabajo
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reparaciones"

    # Encabezados
    headers = [
        'ID', 'Código ROV', 'Técnico', 'Piloto', 'Tipo', 'Falla Reportada',
        'Observaciones', 'Fecha Inicio', 'Fecha Fin', 'Estado', 'Código Controlador'
    ]
    ws.append(headers)

    # Datos
    repairs = Repair.query.all()
    for repair in repairs:
        ws.append([
            repair.id,
            repair.rov_code,
            repair.technician.username,
            repair.pilot_name,
            repair.repair_type,
            repair.reported_failure,
            repair.observations,
            repair.start_date.strftime('%Y-%m-%d %H:%M:%S'),
            repair.end_date.strftime('%Y-%m-%d %H:%M:%S') if repair.end_date else '',
            repair.status,
            repair.controller_code
        ])

    # Guardar el archivo en memoria
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)

    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'reparaciones_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

@repairs_bp.route('/<int:repair_id>')
@login_required
def repair_detail(repair_id):
    repair = Repair.query.get_or_404(repair_id)
    return render_template('repairs/detail.html', repair=repair)

@repairs_bp.route('/reports')
@login_required
def reports():
    # Obtener estadísticas básicas
    total_repairs = Repair.query.count()
    pending_repairs = Repair.query.filter_by(status='pendiente').count()
    completed_repairs = Repair.query.filter_by(status='completada').count()
    
    # Obtener las reparaciones más recientes
    recent_repairs = Repair.query.order_by(Repair.start_date.desc()).limit(5).all()
    
    # Calcular el costo total de todas las reparaciones
    total_cost = 0
    for repair in Repair.query.all():
        for repair_part in repair.parts:
            total_cost += repair_part.unit_cost_at_time * repair_part.quantity
    
    return render_template('repairs/reports.html',
                         total_repairs=total_repairs,
                         pending_repairs=pending_repairs,
                         completed_repairs=completed_repairs,
                         recent_repairs=recent_repairs,
                         total_cost=total_cost)
