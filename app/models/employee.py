from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    matricule = Column(String(50), nullable=False)
    service = Column(String(100), nullable=False)
    fonction = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
  
    
    def __repr__(self):
        return f"<Employee {self.email}>"