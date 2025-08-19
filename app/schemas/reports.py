from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import date

class ReportPeriodType(str, Enum):
    day = "day"
    week = "week"
    month = "month"
    quarter = "quarter"
    year = "year"
    custom = "custom"

class ReportPeriod(BaseModel):
    period_type: ReportPeriodType
    start_date: Optional[date] = None
    end_date: Optional[date] = None