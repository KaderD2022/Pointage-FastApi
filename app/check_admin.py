# check_admin.py
import sys
import os

# Ajoutez le répertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.employee import Employee
from app.utils.auth import get_password_hash

def check_or_create_admin():
    db = SessionLocal()
    
    # Vérifier si l'admin existe
    admin = db.query(Employee).filter(Employee.email == "admin@pointagepro.com").first()
    
    if not admin:
        print("Création de l'admin...")
        admin = Employee(
            email="admin@pointagepro.com",
            hashed_password=get_password_hash("admin123"),
            first_name="Admin",
            last_name="System",
            is_admin=True
        )
        db.add(admin)
        db.commit()
        print("Admin créé avec succès!")
        print(f"Email: admin@pointagepro.com")
        print(f"Mot de passe: admin123")
    else:
        print("Admin existe déjà")
        print(f"Email: {admin.email}")
        print(f"Mot de passe hashé: {admin.hashed_password}")
        print("Vous pouvez utiliser: admin@pointagepro.com / admin123")
    
    db.close()

if __name__ == "__main__":
    check_or_create_admin()