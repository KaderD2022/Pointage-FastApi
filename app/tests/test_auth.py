# tests/test_auth.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login():
    response = client.post("/token", data={"username": "admin@pointage.com", "password": "admin123"})
    assert response.status_code == 200
    assert "access_token" in response.json()