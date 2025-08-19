from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AttendanceCreate(BaseModel):
    employee_id: int
    attendance_type: str  # "morning_arrival", "morning_departure", etc.
    qr_data: str

class AttendanceResponse(BaseModel):
    message: str
    attendance: dict
    is_late: bool

class TimePeriod(BaseModel):
    start_date: str
    end_date: str

class AttendanceStats(BaseModel):
    total_hours: float
    late_minutes: int
    absent_days: int
    penalty_hours: float
    effective_hours: float