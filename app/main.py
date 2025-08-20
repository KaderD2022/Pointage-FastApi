from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, employees, attendance, leaves, reports, admin
from app.database import engine, Base
from app.routes import qrcodes  # Ajouter cette ligne
app = FastAPI(title="Pointage API", version="1.0.0")

# CORS
# Configuration CORS
origins = [
    "http://localhost:5173",  # Vite/React
    "http://localhost:3000",  # Create React App
    "http://localhost:8000",  # Create React App
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Créer les tables de la base de données
Base.metadata.create_all(bind=engine)

# Inclure les routes
app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(attendance.router)
app.include_router(leaves.router)
app.include_router(reports.router)
app.include_router(qrcodes.router) 
app.include_router(admin.router)# Ajouter cette ligne
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de pointage"}