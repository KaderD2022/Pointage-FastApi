# app/utils/time_calculations.py
from datetime import datetime, time, timedelta, date
from dateutil import rrule
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session

WORK_HOURS_PER_DAY = 8
WORK_HOURS_PER_WEEK = 40
WORK_HOURS_PER_MONTH = 160
PENALTY_PERCENTAGE = 0.10
PENALTY_HOURS = 16

MORNING_START = time(8, 0)
AFTERNOON_START = time(14, 30)

def calculate_working_hours(attendance_records: List[Dict]) -> Dict:
    """Calcule les heures de travail avec les retards et absences"""
    total_seconds = 0
    late_minutes = 0
    absent_days = 0
    
    for record in attendance_records:
        if record["is_holiday"] or record["is_on_leave"]:
            continue
            
        if record["is_absent"]:
            absent_days += 1
            continue
            
        # Calcul du temps de travail le matin
        if record["morning_arrival"] and record["morning_departure"]:
            arrival = datetime.strptime(record["morning_arrival"], "%Y-%m-%d %H:%M:%S")
            departure = datetime.strptime(record["morning_departure"], "%Y-%m-%d %H:%M:%S")
            total_seconds += (departure - arrival).total_seconds()
            
            # Vérifier retard matin
            if arrival.time() > MORNING_START:
                late_minutes += (arrival.time().hour - MORNING_START.hour) * 60
                late_minutes += arrival.time().minute - MORNING_START.minute
                
        # Calcul du temps de travail l'après-midi
        if record["afternoon_arrival"] and record["afternoon_departure"]:
            arrival = datetime.strptime(record["afternoon_arrival"], "%Y-%m-%d %H:%M:%S")
            departure = datetime.strptime(record["afternoon_departure"], "%Y-%m-%d %H:%M:%S")
            total_seconds += (departure - arrival).total_seconds()
            
            # Vérifier retard après-midi
            if arrival.time() > AFTERNOON_START:
                late_minutes += (arrival.time().hour - AFTERNOON_START.hour) * 60
                late_minutes += arrival.time().minute - AFTERNOON_START.minute
                
    total_hours = total_seconds / 3600
    penalty_hours = calculate_penalty(absent_days, late_minutes)
    
    return {
        "total_hours": round(total_hours, 2),
        "late_minutes": late_minutes,
        "absent_days": absent_days,
        "penalty_hours": penalty_hours,
        "effective_hours": round(total_hours - penalty_hours, 2)
    }

def calculate_penalty(absent_days: int, late_minutes: int) -> float:
    """Calcule les heures de pénalité"""
    absent_hours = absent_days * WORK_HOURS_PER_DAY
    late_hours = late_minutes / 60
    return (absent_hours + late_hours) * PENALTY_PERCENTAGE

def get_time_periods(period_type: str, custom_start: date = None, custom_end: date = None) -> Tuple[date, date]:
    """Divise la période en jours, semaines, mois, trimestres, semestres et années"""
    today = date.today()
    
    if period_type == "day":
        return today, today
    elif period_type == "week":
        start = today - timedelta(days=today.weekday())
        return start, start + timedelta(days=6)
    elif period_type == "month":
        start = date(today.year, today.month, 1)
        end = date(today.year, today.month + 1, 1) - timedelta(days=1)
        return start, end
    elif period_type == "quarter":
        quarter = (today.month - 1) // 3 + 1
        start_month = 3 * quarter - 2
        end_month = 3 * quarter
        start = date(today.year, start_month, 1)
        end = date(today.year, end_month + 1, 1) - timedelta(days=1)
        return start, end
    elif period_type == "semester":
        semester = 1 if today.month <= 6 else 2
        start_month = 6 * semester - 5
        end_month = 6 * semester
        start = date(today.year, start_month, 1)
        end = date(today.year, end_month + 1, 1) - timedelta(days=1)
        return start, end
    elif period_type == "year":
        start = date(today.year, 1, 1)
        end = date(today.year, 12, 31)
        return start, end
    elif period_type == "custom" and custom_start and custom_end:
        return custom_start, custom_end
    else:
        raise ValueError("Période invalide")

def calculate_employee_stats(db: Session, employee_id: int, start_date: date, end_date: date) -> dict:
    """Calcule les statistiques pour un employé spécifique"""
    from app.models.attendance import Attendance
    
    attendances = db.query(Attendance).filter(
        Attendance.employee_id == employee_id,
        Attendance.date >= start_date.isoformat(),
        Attendance.date <= end_date.isoformat()
    ).all()
    
    present_days = sum(1 for a in attendances if not a.is_absent)
    late_days = sum(1 for a in attendances if a.is_late_morning or a.is_late_afternoon)
    absent_days = sum(1 for a in attendances if a.is_absent)
    
    worked_hours = 0
    for a in attendances:
        if a.morning_arrival and a.morning_departure:
            worked_hours += (a.morning_departure - a.morning_arrival).total_seconds() / 3600
        if a.afternoon_arrival and a.afternoon_departure:
            worked_hours += (a.afternoon_departure - a.afternoon_arrival).total_seconds() / 3600
    
    # Calcul simplifié des pénalités
    penalty_hours = absent_days * 8 + late_days * 0.5  # 8h par jour absent, 0.5h par retard
    
    return {
        "present_days": present_days,
        "late_days": late_days,
        "absent_days": absent_days,
        "worked_hours": round(worked_hours, 2),
        "penalty_hours": round(penalty_hours, 2)
    }