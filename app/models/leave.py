from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime
from app.database import Base

class Leave(Base):
    __tablename__ = "leaves"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    start_date = Column(String(10), nullable=False)  # Format: YYYY-MM-DD
    end_date = Column(String(10), nullable=False)    # Format: YYYY-MM-DD
    leave_type = Column(String(50), nullable=False)  # "congé" ou "permission"
    status = Column(String(20), default="pending")   # "pending", "approved", "rejected"
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Leave {self.employee_id} {self.start_date}-{self.end_date}>"