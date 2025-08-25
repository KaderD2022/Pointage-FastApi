from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, List

from app.database import get_db
from app.models import Attendance, Leave, Employee
from app.utils.auth import get_current_admin

router = APIRouter(prefix="/activity", tags=["Activity"])

@router.get("/recent")
async def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
) -> List[Dict]:
    """Retourne les activités récentes"""
    # Derniers pointages
    recent_attendances = db.query(
        Attendance, Employee.first_name, Employee.last_name
    ).join(
        Employee, Attendance.employee_id == Employee.id
    ).order_by(
        Attendance.created_at.desc()
    ).limit(limit).all()
    
    activities = []
    
    for attendance, first_name, last_name in recent_attendances:
        activities.append({
            "type": "attendance",
            "employee_name": f"{first_name} {last_name}",
            "timestamp": attendance.created_at,
            "details": f"Pointage {attendance.attendance_type}",
            "status": "on_time" if not (attendance.is_late_morning or attendance.is_late_afternoon) else "late"
        })
    
    # Dernières demandes de congé
    recent_leaves = db.query(
        Leave, Employee.first_name, Employee.last_name
    ).join(
        Employee, Leave.employee_id == Employee.id
    ).order_by(
        Leave.created_at.desc()
    ).limit(limit).all()
    
    for leave, first_name, last_name in recent_leaves:
        activities.append({
            "type": "leave",
            "employee_name": f"{first_name} {last_name}",
            "timestamp": leave.created_at,
            "details": f"Demande de {leave.leave_type}",
            "status": leave.status
        })
    
    # Trier par date et limiter
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    return activities[:limit]