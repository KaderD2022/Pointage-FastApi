# app/schemas/auth.py
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str  # Assurez-vous que ce champ existe

class TokenData(BaseModel):
    email: str | None = None
    role: str | None = None  # Ajoutez aussi role ici

class UserLogin(BaseModel):
    email: str
    password: str