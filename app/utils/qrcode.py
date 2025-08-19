# app/utils/qrcode.py
import qrcode
from io import BytesIO
import base64
import secrets
from datetime import datetime, timedelta

# Fonctions pour QR codes par employé (ancienne version)
def generate_qr_code_data(employee_id: int) -> str:
    """Génère des données uniques pour le QR code avec expiration"""
    token = secrets.token_urlsafe(32)
    expiration = (datetime.now() + timedelta(minutes=30)).isoformat()
    return f"{employee_id}:{token}:{expiration}"

def verify_qr_code(qr_data: str, employee_id: int) -> bool:
    """Vérifie si le QR code est valide pour un employé spécifique"""
    try:
        parts = qr_data.split(":")
        if len(parts) != 3:
            return False
            
        stored_id, token, expiration = parts
        if int(stored_id) != employee_id:
            return False
            
        expiration_time = datetime.fromisoformat(expiration)
        if datetime.now() > expiration_time:
            return False
            
        return True
    except:
        return False

# Fonctions pour QR codes globaux (nouvelle version)
def generate_global_qr_code_data(qr_type: str) -> str:
    """Génère des données pour le QR code partagé"""
    token = secrets.token_urlsafe(32)
    valid_from = datetime.now()
    
    if qr_type == "morning":
        valid_to = datetime.now().replace(hour=12, minute=0, second=0)
    else:  # evening
        valid_to = datetime.now().replace(hour=18, minute=0, second=0)
    
    return f"{qr_type}:{token}:{valid_from.isoformat()}:{valid_to.isoformat()}"

def verify_global_qr_code(qr_data: str, qr_type: str) -> bool:
    """Vérifie si le QR code partagé est valide"""
    try:
        parts = qr_data.split(":")
        if len(parts) != 4:
            return False
            
        stored_type, token, valid_from_str, valid_to_str = parts
        if stored_type != qr_type:
            return False
            
        valid_from = datetime.fromisoformat(valid_from_str)
        valid_to = datetime.fromisoformat(valid_to_str)
        now = datetime.now()
        
        if now < valid_from or now > valid_to:
            return False
            
        return True
    except:
        return False

def create_qr_code_image(qr_data: str) -> str:
    """Crée une image QR code et retourne en base64"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")