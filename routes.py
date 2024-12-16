from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from models import db, Repair, ROV, Part, RepairPart
from datetime import datetime
from utils.excel_export import create_repair_report, create_failure_frequency_report, create_monthly_cost_report
import io
from sqlalchemy import func

auth_bp = Blueprint('auth', __name__)
main_bp = Blueprint('main', __name__)
repairs_bp = Blueprint('repairs', __name__)

@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@repairs_bp.route('/repairs')
@login_required
def repairs_list():
    repairs = Repair.query.all()
    return render_template('repairs/list.html', repairs=repairs)

@repairs_bp.route('/repairs/new', methods=['GET', 'POST'])
@login_required
def new_repair():
    if request.method == 'POST':
        # Lógica para crear nueva reparación
        pass
    rovs = ROV.query.all()
    parts = Part.query.all()
    return render_template('repairs/new.html', rovs=rovs, parts=parts)

@repairs_bp.route('/repairs/<int:repair_id>')
@login_required
def repair_detail(repair_id):
    repair = Repair.query.get_or_404(repair_id)
    return render_template('repairs/detail.html', repair=repair)

@repairs_bp.route('/export_excel')
@login_required
def export_excel():
    date_str = request.args.get('date')
    repair_type = request.args.get('type')
    
    query = Repair.query
    
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        query = query.filter(func.date(Repair.start_date) == date)
    
    if repair_type:
        query = query.filter(Repair.repair_type == repair_type)
    
    repairs = query.all()
    
    wb = create_repair_report(repairs)
    
    # Guardar el archivo en un buffer en memoria
    excel_file = io.BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'reporte_reparaciones_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )

@repairs_bp.route('/reports')
@login_required
def reports():
    if current_user.role != 'supervisor':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.index'))
    
    # Obtener estadísticas generales
    total_repairs = Repair.query.count()
    preventive = Repair.query.filter_by(repair_type='preventiva').count()
    corrective = Repair.query.filter_by(repair_type='correctiva').count()
    
    # Calcular costo total
    total_cost = db.session.query(
        func.sum(RepairPart.quantity * RepairPart.unit_cost_at_time)
    ).scalar() or 0
    
    stats = {
        'total_repairs': total_repairs,
        'preventive': preventive,
        'corrective': corrective,
        'total_cost': total_cost
    }
    
    current_year = datetime.now().year
    return render_template('reports/index.html', stats=stats, current_year=current_year)

@repairs_bp.route('/reports/failure-frequency')
@login_required
def failure_frequency_report():
    if current_user.role != 'supervisor':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.index'))
    
    start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
    end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
    
    wb = create_failure_frequency_report(start_date, end_date)
    
    excel_file = io.BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'reporte_fallas_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.xlsx'
    )

@repairs_bp.route('/reports/monthly-cost')
@login_required
def monthly_cost_report():
    if current_user.role != 'supervisor':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.index'))
    
    year = int(request.args.get('year'))
    month = int(request.args.get('month'))
    
    wb = create_monthly_cost_report(year, month)
    
    excel_file = io.BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'reporte_costos_{year}_{month:02d}.xlsx'
    )
