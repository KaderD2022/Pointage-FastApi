# recreate_admin.py
import sys
sys.path.append('.')
from app.database import SessionLocal
from app.models.employee import Employee
import bcrypt

def recreate_admin():
    db = SessionLocal()
    
    try:
        # Supprimer l'ancien admin s'il existe
        db.query(Employee).filter(Employee.email == "admin@pointagepro.com").delete()
        
        # Créer un nouvel admin avec bcrypt direct
        password = "admin123"
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        admin = Employee(
            first_name="Admin",
            last_name="System",
            matricule="ADM001",
            service="Administration",
            fonction="Administrateur",
            email="admin@pointagepro.com",
            hashed_password=hashed,
            is_admin=True
        )
        
        db.add(admin)
        db.commit()
        
        print("✅ Admin recréé avec succès!")
        print("📧 admin@pointagepro.com")
        print("🔑 admin123")
        print(f"Hash: {hashed}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    recreate_admin()