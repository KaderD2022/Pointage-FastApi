# create_admin.py
from app.database import SessionLocal
from app.models.employee import Employee
from app.utils.auth import get_password_hash

db = SessionLocal()

admin = Employee(
    first_name="Admin",
    last_name="System",
    email="admin@pointage.com",
    hashed_password=get_password_hash("admin123"),
    is_active=True,
    qr_code_data="initial"
)

db.add(admin)
db.commit()
print("Admin créé avec succès!")
db.close()