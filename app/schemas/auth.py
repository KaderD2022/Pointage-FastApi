from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    email: str | None = None

class UserLogin(BaseModel):
    email: str
    password: str