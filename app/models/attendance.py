from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime
from app.database import Base

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(String(10), nullable=False)  # Format: YYYY-MM-DD
    morning_arrival = Column(DateTime, nullable=True)
    morning_departure = Column(DateTime, nullable=True)
    afternoon_arrival = Column(DateTime, nullable=True)
    afternoon_departure = Column(DateTime, nullable=True)
    is_late_morning = Column(Boolean, default=False)
    is_late_afternoon = Column(Boolean, default=False)
    is_absent = Column(Boolean, default=False)
    is_holiday = Column(Boolean, default=False)
    is_on_leave = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Attendance {self.employee_id} {self.date}>"