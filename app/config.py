from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Pointage API"
    admin_email: str = "admin@pointage.com"
    secret_key: str = "votre_secret_key_tres_secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()