# init_db.py
from app.database import Base, engine
from app.models import employee, attendance, leave, holiday

print("Création des tables de la base de données...")
Base.metadata.create_all(bind=engine)
print("Tables créées avec succès!")