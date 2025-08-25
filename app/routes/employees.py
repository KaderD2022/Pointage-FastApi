from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import pandas as pd
from io import BytesIO
import json

from app.database import get_db
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.leave import Leave
from app.schemas.employee import (
    EmployeeCreate, 
    EmployeeResponse, 
    EmployeeUpdate,
    EmployeeStats
)
from app.utils.auth import get_password_hash, get_current_admin, oauth2_scheme, decode_token
from app.utils.qrcode import generate_qr_code_data, create_qr_code_image
from app.utils.reports import generate_employees_report_pdf
from app.utils.time_calculations import get_time_periods, calculate_employee_stats

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("/", response_model=List[EmployeeResponse])
async def get_employees(
    service: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """Récupérer tous les employés avec filtres"""
    query = db.query(Employee)
    
    if service and service != "all":
        query = query.filter(Employee.service == service)
    
    if status and status != "all":
        if status == "active":
            query = query.filter(Employee.is_active == True)
        elif status == "inactive":
            query = query.filter(Employee.is_active == False)
    
    if search:
        query = query.filter(
            (Employee.first_name.ilike(f"%{search}%")) |
            (Employee.last_name.ilike(f"%{search}%")) |
            (Employee.email.ilike(f"%{search}%")) |
            (Employee.matricule.ilike(f"%{search}%")) |
            (Employee.service.ilike(f"%{search}%"))
        )
    
    employees = query.order_by(Employee.first_name, Employee.last_name).all()
    return employees

@router.get("/stats", response_model=EmployeeStats)
async def get_employees_stats(
    period: str = "month",
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """Récupérer les statistiques des employés"""
    try:
        start_date, end_date = get_time_periods(period)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    total_employees = db.query(Employee).count()
    active_employees = db.query(Employee).filter(Employee.is_active == True).count()
    
    # Employés en congé
    on_leave_employees = db.query(Employee).join(Leave).filter(
        Leave.status == "approved",
        Leave.start_date <= end_date.isoformat(),
        Leave.end_date >= start_date.isoformat(),
        Employee.is_active == True
    ).distinct().count()
    
    # Calculer les heures totales et pénalités
    total_hours = 0
    total_penalties = 0
    
    # Pour chaque employé actif, calculer les stats
    active_emps = db.query(Employee).filter(Employee.is_active == True).all()
    for emp in active_emps:
        stats = calculate_employee_stats(db, emp.id, start_date, end_date)
        total_hours += stats.get("worked_hours", 0)
        total_penalties += stats.get("penalty_hours", 0)
    
    # Congés restants (estimation)
    total_remaining_leaves = active_employees * 25  # 25 jours par an par employé
    
    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "on_leave_employees": on_leave_employees,
        "total_hours_month": round(total_hours, 2),
        "total_penalties": round(total_penalties, 2),
        "total_remaining_leaves": total_remaining_leaves
    }

@router.post("/", response_model=EmployeeResponse)
async def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """Créer un nouvel employé"""
    # Vérifier si l'email existe déjà
    existing_employee = db.query(Employee).filter(Employee.email == employee.email).first()
    if existing_employee:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    # Vérifier si le matricule existe déjà
    if employee.matricule:
        existing_matricule = db.query(Employee).filter(Employee.matricule == employee.matricule).first()
        if existing_matricule:
            raise HTTPException(status_code=400, detail="Matricule déjà utilisé")
    
    # Créer l'employé
    db_employee = Employee(
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        hashed_password=get_password_hash(employee.password),
        service=employee.service,
        fonction=employee.fonction,
        matricule=employee.matricule,
        date_embauche=employee.date_embauche,
        is_admin=employee.is_admin if hasattr(employee, 'is_admin') else False,
        is_active=True
    )
    
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    
    return db_employee

@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """Récupérer un employé spécifique"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    return employee

@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """Mettre à jour un employé"""
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Mettre à jour les champs fournis
    update_data = employee_data.dict(exclude_unset=True)
    
    if 'password' in update_data:
        update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
    
    for field, value in update_data.items():
        setattr(db_employee, field, value)
    
    db.commit()
    db.refresh(db_employee)
    
    return db_employee

@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """Supprimer un employé"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Pour la sécurité, on désactive plutôt que supprimer
    employee.is_active = False
    db.commit()
    
    return {"message": "Employé désactivé avec succès"}

@router.post("/{employee_id}/qr-code")
async def generate_employee_qr_code(
    employee_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """Générer un QR code pour un employé"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    qr_data = generate_qr_code_data(employee_id)
    qr_image = create_qr_code_image(qr_data)
    
    return {"qr_code": qr_image, "employee_id": employee_id}

@router.get("/{employee_id}/stats")
async def get_employee_stats(
    employee_id: int,
    period: str = "month",
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """Récupérer les statistiques détaillées d'un employé"""
    try:
        start_date, end_date = get_time_periods(period)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    stats = calculate_employee_stats(db, employee_id, start_date, end_date)
    
    return {
        "employee_id": employee_id,
        "period": f"{start_date} to {end_date}",
        "stats": stats
    }

@router.get("/export/pdf")
async def export_employees_pdf(
    service: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """Exporter les employés en PDF"""
    # Récupérer les employés avec filtres
    query = db.query(Employee)
    
    if service and service != "all":
        query = query.filter(Employee.service == service)
    
    if status and status != "all":
        if status == "active":
            query = query.filter(Employee.is_active == True)
        elif status == "inactive":
            query = query.filter(Employee.is_active == False)
    
    employees = query.all()
    
    # Préparer les données pour le PDF
    employees_data = []
    for emp in employees:
        # Calculer les stats pour chaque employé
        start_date, end_date = get_time_periods("month")
        stats = calculate_employee_stats(db, emp.id, start_date, end_date)
        
        employees_data.append({
            "id": emp.id,
            "matricule": emp.matricule,
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "email": emp.email,
            "service": emp.service,
            "fonction": emp.fonction,
            "date_embauche": emp.date_embauche.isoformat() if emp.date_embauche else None,
            "is_active": emp.is_active,
            "worked_hours": stats.get("worked_hours", 0),
            "late_days": stats.get("late_days", 0),
            "absent_days": stats.get("absent_days", 0),
            "penalty_hours": stats.get("penalty_hours", 0)
        })
    
    # Générer le PDF
    pdf_buffer = generate_employees_report_pdf(
        employees_data, 
        datetime.now().date().isoformat(),
        datetime.now().date().isoformat()
    )
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=employees_report.pdf"}
    )

@router.get("/export/excel")
async def export_employees_excel(
    service: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """Exporter les employés en Excel"""
    query = db.query(Employee)
    
    if service and service != "all":
        query = query.filter(Employee.service == service)
    
    if status and status != "all":
        if status == "active":
            query = query.filter(Employee.is_active == True)
        elif status == "inactive":
            query = query.filter(Employee.is_active == False)
    
    employees = query.all()
    
    # Préparer les données pour Excel
    data = []
    for emp in employees:
        data.append({
            "Matricule": emp.matricule,
            "Prénom": emp.first_name,
            "Nom": emp.last_name,
            "Email": emp.email,
            "Service": emp.service,
            "Fonction": emp.fonction,
            "Date d'embauche": emp.date_embauche.isoformat() if emp.date_embauche else "",
            "Statut": "Actif" if emp.is_active else "Inactif"
        })
    
    # Créer le DataFrame
    df = pd.DataFrame(data)
    
    # Créer le fichier Excel en mémoire
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Employés')
    
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=employees.xlsx"}
    )

@router.get("/services/list")
async def get_services_list(
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """Récupérer la liste des services distincts"""
    services = db.query(Employee.service).distinct().all()
    services_list = [service[0] for service in services if service[0]]
    
    return {"services": services_list}