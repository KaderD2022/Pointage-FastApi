from pydantic import BaseModel
from datetime import date
from typing import Optional

class PeriodFilter(BaseModel):
    period: str = "month"
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class LeaveDecision(BaseModel):
    decision: str  # "approve" or "reject"
    reason: Optional[str] = None