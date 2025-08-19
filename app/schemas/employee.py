from pydantic import BaseModel

class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    matricule: str
    service: str
    fonction: str
    email: str
    password: str

class EmployeeResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    matricule: str
    service: str
    fonction: str
    email: str
    is_active: bool
    qr_code_image: str