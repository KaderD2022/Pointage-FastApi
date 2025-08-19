# app/models/qrcode.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.database import Base

class GlobalQRCode(Base):
    __tablename__ = "global_qrcodes"
    
    id = Column(Integer, primary_key=True, index=True)
    qr_type = Column(String(10), nullable=False)  # "morning" ou "evening"
    qr_data = Column(String(255), unique=True, nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<GlobalQRCode {self.qr_type} {self.valid_from}-{self.valid_to}>"