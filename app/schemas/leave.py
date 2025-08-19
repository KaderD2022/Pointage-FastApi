# app/schemas/leave.py
from pydantic import BaseModel
from datetime import date, datetime

class LeaveCreate(BaseModel):
    employee_id: int
    start_date: date
    end_date: date
    leave_type: str
    reason: str | None = None

class LeaveResponse(BaseModel):
    id: int
    employee_id: int
    start_date: date
    end_date: date
    leave_type: str
    status: str
    reason: str | None
    created_at: datetime