from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.routes import qrcodes  # Ajouter cette ligne
from app.database import get_db
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeResponse
from app.utils.auth import get_password_hash, oauth2_scheme, decode_token
from app.utils.qrcode import generate_global_qr_code_data, create_qr_code_image, generate_qr_code_data

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.post("/", response_model=EmployeeResponse)
async def create_employee(
    employee: EmployeeCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Vérifier que l'utilisateur est admin
    payload = decode_token(token)
    if not payload or not payload.get("is_admin"):
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    # Vérifier si l'email existe déjà
    existing_employee = db.query(Employee).filter(Employee.email == employee.email).first()
    if existing_employee:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    # Générer le QR code
    qr_data = generate_qr_code_data(employee.id)
    qr_image = create_qr_code_image(qr_data)
    
    # Créer l'employé
    db_employee = Employee(
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        service=employee.service,
        fonction=employee.email,
        matricule=employee.matricule,
        hashed_password=get_password_hash(employee.password),
        qr_code_data=qr_data
    )
    
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    
    return {
        **db_employee.__dict__,
        "qr_code_image": qr_image
    }

@router.get("/{employee_id}/qr-code")
async def get_employee_qr_code(
    employee_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Vérifier le token
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    # Vérifier que l'utilisateur demande son propre QR code ou est admin
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    if payload["sub"] != employee.email and not payload.get("is_admin"):
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    # Générer un nouveau QR code
    qr_data = generate_qr_code_data(employee_id)
    qr_image = create_qr_code_image(qr_data)
    
    # Mettre à jour le QR code dans la base de données
    employee.qr_code_data = qr_data
    db.commit()
    
    return {"qr_code_image": qr_image}