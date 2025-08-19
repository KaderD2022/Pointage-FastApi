# app/routes/leaves.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.employee import Employee
from app.models.leave import Leave
from app.schemas.leave import LeaveCreate, LeaveResponse
from app.utils.auth import oauth2_scheme, decode_token

router = APIRouter(prefix="/leaves", tags=["Leaves"])

@router.post("/", response_model=LeaveResponse)
async def create_leave(
    leave: LeaveCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Vérifier le token
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    # Vérifier que l'employé existe
    employee = db.query(Employee).filter(Employee.id == leave.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Créer le congé
    db_leave = Leave(
        employee_id=leave.employee_id,
        start_date=leave.start_date,
        end_date=leave.end_date,
        leave_type=leave.leave_type,
        reason=leave.reason,
        status="pending"
    )
    
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    
    return db_leave

# Ajoutez d'autres endpoints si nécessaire