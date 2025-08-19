from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app.models.leave import Leave
from app.routes import qrcodes  # Ajouter cette ligne
from app.database import get_db
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceStats,
    TimePeriod
)
from app.utils.auth import oauth2_scheme, decode_token
from app.utils.qrcode import verify_qr_code, generate_qr_code_data
from app.utils.time_calculations import (
    calculate_working_hours,
    MORNING_START,
    AFTERNOON_START
)
from app.utils.holidays import is_holiday

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/record", response_model=AttendanceResponse)
async def record_attendance(
    data: AttendanceCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Vérifier le token
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    # Vérifier le QR code
    if not verify_qr_code(data.qr_data, data.employee_id):
        raise HTTPException(status_code=400, detail="QR code invalide ou expiré")
    
    # Vérifier si l'employé existe
    employee = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Vérifier si c'est un jour férié
    holiday = is_holiday(today)
    
    # Vérifier si l'employé est en congé
    on_leave = db.query(Leave).filter(
        Leave.employee_id == data.employee_id,
        Leave.start_date <= today,
        Leave.end_date >= today,
        Leave.status == "approved"
    ).first() is not None
    
    # Récupérer ou créer l'enregistrement de pointage
    attendance = db.query(Attendance).filter(
        Attendance.employee_id == data.employee_id,
        Attendance.date == today
    ).first()
    
    if not attendance:
        attendance = Attendance(
            employee_id=data.employee_id,
            date=today,
            is_holiday=holiday,
            is_on_leave=on_leave,
            is_absent=not (holiday or on_leave)
        )
        db.add(attendance)
    
    now = datetime.now()
    
    # Enregistrer le pointage selon le type
    if data.attendance_type == "morning_arrival":
        attendance.morning_arrival = now
        attendance.is_late_morning = now.time() > MORNING_START
        attendance.is_absent = False
        message = "Bravo vous avez pointé votre arrivée pour le service du matin"
    
    elif data.attendance_type == "morning_departure":
        attendance.morning_departure = now
        message = "Bravo vous avez pointé pour aller en pause"
    
    elif data.attendance_type == "afternoon_arrival":
        attendance.afternoon_arrival = now
        attendance.is_late_afternoon = now.time() > AFTERNOON_START
        attendance.is_absent = False
        message = "Bravo vous avez pointé votre arrivée pour le service de l'après-midi"
    
    elif data.attendance_type == "afternoon_departure":
        attendance.afternoon_departure = now
        message = "Bravo vous avez pointé pour la dernière fois de la journée"
    
    db.commit()
    db.refresh(attendance)
    
    return {
        "message": message,
        "attendance": attendance,
        "is_late": (
            (data.attendance_type == "morning_arrival" and attendance.is_late_morning) or
            (data.attendance_type == "afternoon_arrival" and attendance.is_late_afternoon)
        )
    }

@router.get("/stats/{employee_id}", response_model=AttendanceStats)
async def get_attendance_stats(
    employee_id: int,
    period: TimePeriod,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Vérifier le token et les autorisations
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    # Récupérer les enregistrements de pointage pour la période
    # Implémentation à compléter selon la période (jour, semaine, mois, etc.)
    records = db.query(Attendance).filter(
        Attendance.employee_id == employee_id,
        # Filtre par période à ajouter
    ).all()
    
    # Calculer les statistiques
    stats = calculate_working_hours([r.__dict__ for r in records])
    
    return stats