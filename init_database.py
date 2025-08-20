# init_database.py
import sys
import os

# Ajouter le répertoire courant au path
sys.path.append('.')

from app.database import engine, Base, SessionLocal
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.leave import Leave
from app.models.holiday import Holiday
from app.utils.auth import get_password_hash

def init_database():
    print("🔄 Initialisation de la base de données...")
    
    # 1. Créer les tables
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables créées avec succès!")
    except Exception as e:
        print(f"❌ Erreur création tables: {e}")
        return
    
    # 2. Créer l'admin
    db = SessionLocal()
    try:
        admin = db.query(Employee).filter(Employee.email == "admin@pointagepro.com").first()
        
        if not admin:
            print("🔄 Création de l'administrateur...")
            admin = Employee(
                email="admin@pointagepro.com",
                hashed_password=get_password_hash("admin123"),
                first_name="Admin",
                last_name="System",
                is_admin=True
            )
            db.add(admin)
            db.commit()
            print("✅ Admin créé avec succès!")
            print("📧 Email: admin@pointagepro.com")
            print("🔑 Mot de passe: admin123")
        else:
            print("ℹ️ Admin existe déjà")
            print(f"📧 Email: {admin.email}")
            
    except Exception as e:
        print(f"❌ Erreur création admin: {e}")
    finally:
        db.close()
    
    print("🎉 Initialisation terminée!")

if __name__ == "__main__":
    init_database()