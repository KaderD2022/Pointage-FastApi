# create_tables.py
import sys
import os

# Ajouter le répertoire courant au path
sys.path.append('.')

from app.database import engine, Base
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.leave import Leave
from app.models.holiday import Holiday

def create_database_tables():
    print("🔄 Création des tables de la base de données...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables créées avec succès!")
        print("📋 Tables créées: employees, attendance, leaves, holidays")
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")

if __name__ == "__main__":
    create_database_tables()