from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    service: str
    fonction: str
    matricule: str
    date_embauche: date

class EmployeeCreate(EmployeeBase):
    password: str
    is_admin: Optional[bool] = False

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    service: Optional[str] = None
    fonction: Optional[str] = None
    matricule: Optional[str] = None
    date_embauche: Optional[date] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

class EmployeeResponse(EmployeeBase):
    id: int
    is_active: bool
    is_admin: bool
    
    class Config:
        from_attributes = True

class EmployeeStats(BaseModel):
    total_employees: int
    active_employees: int
    on_leave_employees: int
    total_hours_month: float
    total_penalties: float
    total_remaining_leaves: int

class EmployeeDetailedStats(BaseModel):
    employee_id: int
    period: str
    stats: dict