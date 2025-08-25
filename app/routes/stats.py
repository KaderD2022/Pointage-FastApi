from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import Dict

from app.database import get_db
from app.models import Employee, Attendance, Leave
from app.utils.auth import get_current_admin
from app.utils.time_calculations import get_time_periods

router = APIRouter(prefix="/stats", tags=["Statistics"])

@router.get("/dashboard")
async def get_dashboard_stats(
    period: str = "month",
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
) -> Dict:
    """Retourne les statistiques pour le dashboard admin"""
    start_date, end_date = get_time_periods(period)
    
    # Statistiques de base
    total_employees = db.query(Employee).count()
    
    # Employés présents aujourd'hui
    today = date.today().isoformat()
    present_today = db.query(Attendance).filter(
        Attendance.date == today,
        Attendance.is_absent == False
    ).count()
    
    # Retards ce mois
    late_this_month = db.query(Attendance).filter(
        Attendance.date >= start_date.isoformat(),
        Attendance.date <= end_date.isoformat(),
        (Attendance.is_late_morning == True) | (Attendance.is_late_afternoon == True)
    ).count()
    
    # Congés en cours
    current_leaves = db.query(Leave).filter(
        Leave.status == "approved",
        Leave.start_date <= end_date.isoformat(),
        Leave.end_date >= start_date.isoformat()
    ).count()
    
    # Pourcentages
    presence_rate = (present_today / total_employees * 100) if total_employees > 0 else 0
    
    return {
        "total_employees": total_employees,
        "present_today": present_today,
        "late_this_month": late_this_month,
        "current_leaves": current_leaves,
        "presence_rate": round(presence_rate, 1),
        "period": f"{start_date} to {end_date}"
    }

@router.get("/attendance-trend")
async def get_attendance_trend(
    days: int = 7,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
) -> Dict:
    """Retourne les données pour le graphique des pointages"""
    from datetime import timedelta
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    trend_data = []
    current_date = start_date
    
    while current_date <= end_date:
        day_stats = db.query(Attendance).filter(
            Attendance.date == current_date.isoformat()
        ).all()
        
        present = sum(1 for a in day_stats if not a.is_absent)
        late = sum(1 for a in day_stats if a.is_late_morning or a.is_late_afternoon)
        absent = sum(1 for a in day_stats if a.is_absent)
        
        trend_data.append({
            "date": current_date.isoformat(),
            "present": present,
            "late": late,
            "absent": absent
        })
        
        current_date += timedelta(days=1)
    
    return {
        "period": f"{start_date} to {end_date}",
        "data": trend_data
    }