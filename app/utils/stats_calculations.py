from sqlalchemy.orm import Session
from datetime import date
from app.models import Employee, Attendance, Leave, Holiday

def calculate_total_employees(db: Session) -> int:
    """Calcule le nombre total d'employés"""
    return db.query(Employee).count()

def calculate_on_time_employees(db: Session, start_date: date, end_date: date) -> int:
    """Calcule le nombre d'employés à l'heure"""
    return db.query(Employee).join(Attendance).filter(
        Attendance.date >= start_date,
        Attendance.date <= end_date,
        Attendance.is_late_morning == False,
        Attendance.is_late_afternoon == False,
        Attendance.is_absent == False
    ).distinct().count()

def calculate_late_employees(db: Session, start_date: date, end_date: date) -> int:
    """Calcule le nombre d'employés en retard"""
    return db.query(Employee).join(Attendance).filter(
        Attendance.date >= start_date,
        Attendance.date <= end_date,
        (Attendance.is_late_morning == True) | (Attendance.is_late_afternoon == True)
    ).distinct().count()

def calculate_total_leaves(db: Session, start_date: date, end_date: date) -> int:
    """Calcule le nombre total de congés"""
    return db.query(Leave).filter(
        Leave.start_date <= end_date,
        Leave.end_date >= start_date
    ).count()

def calculate_holidays(db: Session, start_date: date, end_date: date) -> int:
    """Calcule le nombre de jours fériés"""
    return db.query(Holiday).filter(
        Holiday.date >= start_date,
        Holiday.date <= end_date
    ).count()

def calculate_employee_stats(db: Session, employee_id: int, start_date: date, end_date: date) -> dict:
    """Calcule les statistiques pour un employé spécifique"""
    attendances = db.query(Attendance).filter(
        Attendance.employee_id == employee_id,
        Attendance.date >= start_date,
        Attendance.date <= end_date
    ).all()
    
    present_days = sum(1 for a in attendances if not a.is_absent)
    late_days = sum(1 for a in attendances if a.is_late_morning or a.is_late_afternoon)
    absent_days = sum(1 for a in attendances if a.is_absent)
    
    worked_hours = sum(
        (a.morning_departure - a.morning_arrival).total_seconds() / 3600 +
        (a.afternoon_departure - a.afternoon_arrival).total_seconds() / 3600
        for a in attendances 
        if a.morning_arrival and a.morning_departure and a.afternoon_arrival and a.afternoon_departure
    )
    
    return {
        "present_days": present_days,
        "late_days": late_days,
        "absent_days": absent_days,
        "worked_hours": round(worked_hours, 2)
    }
def calculate_worked_hours(attendances: list) -> float:
    total = 0
    for a in attendances:
        if a.morning_arrival and a.morning_departure:
            total += (a.morning_departure - a.morning_arrival).total_seconds() / 3600
        if a.afternoon_arrival and a.afternoon_departure:
            total += (a.afternoon_departure - a.afternoon_arrival).total_seconds() / 3600
    return round(total, 2)