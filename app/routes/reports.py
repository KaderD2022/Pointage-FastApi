from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from datetime import datetime, date, timedelta
from reportlab.lib.styles import getSampleStyleSheet
import io
from app.routes import qrcodes  # Ajouter cette ligne
from app.database import get_db
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.leave import Leave
from app.utils.auth import oauth2_scheme, decode_token
from app.utils.reports import (
    generate_employees_report_pdf,      # Changé
    generate_attendance_report_pdf,     # Changé (au lieu de generate_attendance_pdf)
    generate_leaves_report_pdf,         # Changé
    generate_stats_report_pdf,          # Changé
    generate_global_qr_pdf              # Changé
)
from app.schemas.reports import ReportPeriod

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/attendance/{employee_id}")
async def generate_employee_attendance_report(
    employee_id: int,
    period_type: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Génère un rapport PDF des pointages pour un employé"""
    # Vérification de l'authentification
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    # Vérifier que l'utilisateur demande son propre rapport ou est admin
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    if payload["sub"] != employee.email and not payload.get("is_admin"):
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    # Déterminer la période
    today = date.today()
    period_text = ""
    
    if period_type == "day":
        period_text = f"Jour - {today.strftime('%d/%m/%Y')}"
        start_date = today.strftime("%Y-%m-%d")
        end_date = start_date
    elif period_type == "week":
        start_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=6-today.weekday())).strftime("%Y-%m-%d")
        period_text = f"Semaine - du {start_date} au {end_date}"
    elif period_type == "month":
        start_date = date(today.year, today.month, 1).strftime("%Y-%m-%d")
        last_day = date(today.year, today.month + 1, 1) - timedelta(days=1)
        end_date = last_day.strftime("%Y-%m-%d")
        period_text = f"Mois - {today.strftime('%B %Y')}"
    elif period_type == "quarter":
        quarter = (today.month - 1) // 3 + 1
        first_month = 3 * quarter - 2
        last_month = 3 * quarter
        start_date = date(today.year, first_month, 1).strftime("%Y-%m-%d")
        end_date = date(today.year, last_month + 1, 1) - timedelta(days=1)
        end_date = end_date.strftime("%Y-%m-%d")
        period_text = f"Trimestre {quarter} - {today.year}"
    elif period_type == "year":
        start_date = date(today.year, 1, 1).strftime("%Y-%m-%d")
        end_date = date(today.year, 12, 31).strftime("%Y-%m-%d")
        period_text = f"Année - {today.year}"
    elif period_type == "custom" and start_date and end_date:
        period_text = f"Période personnalisée - du {start_date} au {end_date}"
    else:
        raise HTTPException(status_code=400, detail="Type de période invalide")
    
    # Récupérer les données de pointage
    attendance_records = db.query(Attendance).filter(
        Attendance.employee_id == employee_id,
        Attendance.date >= start_date,
        Attendance.date <= end_date
    ).all()
    
    # Convertir en format dictionnaire pour le PDF
    records_data = [{
        "date": record.date,
        "morning_arrival": record.morning_arrival.strftime("%H:%M") if record.morning_arrival else "-",
        "morning_departure": record.morning_departure.strftime("%H:%M") if record.morning_departure else "-",
        "afternoon_arrival": record.afternoon_arrival.strftime("%H:%M") if record.afternoon_arrival else "-",
        "afternoon_departure": record.afternoon_departure.strftime("%H:%M") if record.afternoon_departure else "-",
        "is_holiday": record.is_holiday,
        "is_on_leave": record.is_on_leave,
        "is_absent": record.is_absent,
        "is_late_morning": record.is_late_morning,
        "is_late_afternoon": record.is_late_afternoon
    } for record in attendance_records]
    
    # Générer le PDF
    pdf_buffer = generate_attendance_report_pdf(
        records_data,
        period_text,
        f"{employee.first_name} {employee.last_name}"
    )
    
    # Retourner le PDF en réponse
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=rapport_pointage_{employee_id}_{period_type}.pdf"
        }
    )

@router.get("/employees")
async def generate_employees_report(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Génère un PDF avec la liste des employés"""
    # Vérification admin
    payload = decode_token(token)
    if not payload or not payload.get("is_admin"):
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    # Récupérer les employés
    employees = db.query(Employee).all()
    
    # Convertir en format dictionnaire pour le PDF
    employees_data = [{
        "id": emp.id,
        "first_name": emp.first_name,
        "last_name": emp.last_name,
        "email": emp.email,
        "is_active": emp.is_active
    } for emp in employees]
    
    # Générer le PDF
    pdf_buffer = generate_employees_report_pdf(employees_data)
    
    # Retourner le PDF en réponse
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=liste_employes.pdf"
        }
    )

@router.get("/leaves")
async def generate_leaves_report(
    status: Optional[str] = None,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Génère un PDF avec la liste des congés"""
    # Vérification admin
    payload = decode_token(token)
    if not payload or not payload.get("is_admin"):
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    # Récupérer les congés
    query = db.query(
        Leave,
        Employee.first_name,
        Employee.last_name
    ).join(
        Employee, Leave.employee_id == Employee.id
    )
    
    if status:
        query = query.filter(Leave.status == status)
    
    leaves = query.all()
    
    # Convertir en format dictionnaire pour le PDF
    leaves_data = [{
        "employee_first_name": first_name,
        "employee_last_name": last_name,
        "leave_type": leave.leave_type,
        "start_date": leave.start_date,
        "end_date": leave.end_date,
        "status": leave.status
    } for leave, first_name, last_name in leaves]
    
    # Générer le PDF
    pdf_buffer = generate_leaves_report_pdf(leaves_data)
    
    # Retourner le PDF en réponse
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=liste_conges.pdf"
        }
    )
    
    
    
def generate_employees_report_pdf(employees_data, start_date, end_date):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Titre et période
    elements.append(Paragraph("Rapport des Employés", styles['Title']))
    elements.append(Paragraph(f"Période: {start_date} à {end_date}", styles['Normal']))
    
    # Tableau des employés
    table_data = [["ID", "Nom", "Présence", "Retards", "Heures travaillées"]]
    for emp in employees_data:
        table_data.append([
            str(emp['id']),
            f"{emp['first_name']} {emp['last_name']}",
            str(emp['stats']['present_days']),
            str(emp['stats']['late_days']),
            str(emp['stats']['worked_hours'])
        ])
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer
