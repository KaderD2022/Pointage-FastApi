from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.utils.auth import get_current_admin
from app.database import get_db
from app.models import Employee, Attendance, Leave, Holiday
from app.utils.auth import get_current_admin
from app.utils.stats_calculations import calculate_employee_stats
from app.utils.time_calculations import get_time_periods
from app.utils.reports import (
    generate_employees_report_pdf,
    generate_attendance_report_pdf,
    generate_leaves_report_pdf,
    generate_stats_report_pdf,
    generate_global_qr_pdf
)
from app.utils.stats_calculations import (
    calculate_total_employees,
    calculate_on_time_employees,
    calculate_late_employees,
    calculate_total_leaves,
    calculate_holidays,
    calculate_worked_hours,
    calculate_employee_stats
)
from app.schemas.admin import PeriodFilter
# app/routes/admin.py
from app.utils.reports import (
    generate_employees_report_pdf,
    generate_attendance_report_pdf,
    generate_leaves_report_pdf,
    generate_stats_report_pdf,
    generate_global_qr_pdf
)
router = APIRouter(prefix="/admin", tags=["Administration"])

# Liste des employés avec statistiques
@router.get("/employees")
async def get_employees_report(
    period: str = "month",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    admin: Employee = Depends(get_current_admin)
):
    try:
        start, end = get_time_periods(period, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    employees = db.query(Employee).all()
    employees_data = []
    
    for emp in employees:
        stats = calculate_employee_stats(db, emp.id, start, end)
        employees_data.append({
            "id": emp.id,
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "email": emp.email,
            "stats": stats
        })
    
    return employees_data

@router.get("/employees/pdf")
async def get_employees_pdf_report(
    period: str = "month",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    admin: Employee = Depends(get_current_admin)
):
    try:
        start, end = get_time_periods(period, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    employees_data = []  # Récupérer comme dans la route précédente
    pdf_buffer = generate_employees_report_pdf(employees_data, start, end)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"employees_report_{period}.pdf"}
    )

# Gestion des congés
@router.get("/leaves")
async def get_leaves(
    status: Optional[str] = None,
    period: str = "month",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    admin: Employee = Depends(get_current_admin)
):
    try:
        start, end = get_time_periods(period, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    query = db.query(Leave).filter(
        Leave.start_date <= end,
        Leave.end_date >= start
    )
    
    if status:
        query = query.filter(Leave.status == status)
        
    return query.all()

@router.post("/leaves/{leave_id}/approve")
async def approve_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    admin: Employee = Depends(get_current_admin)
):
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Congé non trouvé")
    
    leave.status = "approved"
    db.commit()
    return {"message": "Congé approuvé"}

# Statistiques globales
@router.get("/stats")
async def get_stats(
    period: str = "month",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    admin: Employee = Depends(get_current_admin)
):
    try:
        start, end = get_time_periods(period, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    total_employees = calculate_total_employees(db)
    on_time = calculate_on_time_employees(db, start, end)
    late = calculate_late_employees(db, start, end)
    leaves = calculate_total_leaves(db, start, end)
    holidays = calculate_holidays(db, start, end)
    
    # Calcul des pourcentages
    on_time_percent = (on_time / total_employees * 100) if total_employees > 0 else 0
    late_percent = (late / total_employees * 100) if total_employees > 0 else 0
    
    return {
        "period": f"{start} to {end}",
        "total_employees": total_employees,
        "on_time_employees": on_time,
        "late_employees": late,
        "total_leaves": leaves,
        "holidays": holidays,
        "percentages": {
            "on_time": round(on_time_percent, 2),
            "late": round(late_percent, 2),
            # Ajoutez d'autres pourcentages si nécessaire
        }
    }