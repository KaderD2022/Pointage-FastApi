from sqlalchemy import Boolean, Column, Integer, String
from app.database import Base

class Holiday(Base):
    __tablename__ = "holidays"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), unique=True, nullable=False)  # Format: YYYY-MM-DD
    name = Column(String(100), nullable=False)
    is_recurring = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Holiday {self.name} {self.date}>"