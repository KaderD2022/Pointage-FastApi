from sqlalchemy import Column, Integer, String, Boolean, Date
from app.database import Base

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    service = Column(String(50), nullable=True)
    fonction = Column(String(50), nullable=True)
    matricule = Column(String(20), unique=True, nullable=True)
    date_embauche = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    qr_code_data = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<Employee {self.email}>"