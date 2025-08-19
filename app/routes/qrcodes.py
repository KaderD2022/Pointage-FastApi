# app/routes/qrcodes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models.qrcode import GlobalQRCode
from app.utils.qrcode import generate_global_qr_code_data, create_qr_code_image
from app.utils.auth import oauth2_scheme, decode_token
from app.routes import qrcodes  # Ajouter cette ligne
from app.utils.auth import oauth2_scheme, decode_token
router = APIRouter(prefix="/qrcodes", tags=["QR Codes"])

@router.get("/{qr_type}")
async def get_global_qr_code(
    qr_type: str,  # "morning" ou "evening"
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Obtenir le QR code du matin ou du soir"""
    # Seul un admin peut générer les QR codes
    payload = decode_token(token)
    if not payload or not payload.get("is_admin"):
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    if qr_type not in ["morning", "evening"]:
        raise HTTPException(status_code=400, detail="Type de QR code invalide")
    
    # Désactiver les anciens QR codes du même type
    db.query(GlobalQRCode).filter(
        GlobalQRCode.qr_type == qr_type,
        GlobalQRCode.is_active == True
    ).update({"is_active": False})
    
    # Générer un nouveau QR code
    qr_data = generate_global_qr_code_data(qr_type)
    qr_image = create_qr_code_image(qr_data)
    
    # Déterminer la période de validité
    now = datetime.now()
    if qr_type == "morning":
        valid_to = now.replace(hour=12, minute=0, second=0)
    else:
        valid_to = now.replace(hour=18, minute=0, second=0)
    
    # Enregistrer en base de données
    qr_code = GlobalQRCode(
        qr_type=qr_type,
        qr_data=qr_data,
        valid_from=now,
        valid_to=valid_to,
        is_active=True
    )
    
    db.add(qr_code)
    db.commit()
    
    return {
        "qr_type": qr_type,
        "valid_from": now,
        "valid_to": valid_to,
        "qr_code_image": qr_image
    }