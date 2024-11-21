import pytest
import httpx
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_buyer_registration():
    response = httpx.post("http://localhost:8000/api/v1/auth/register", json={
        "name": "testname",
        "email": "testemail@test.com",
        "password": "testpassword",
        "role": "buyer",
    })
    print(response)
    assert response.status_code == 200
    assert response.json().get("message") == "Login successful"
    assert response.json().get("level") == 0
    assert response.json().get("email") == "testemail@test.com"
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

@pytest.mark.asyncio
async def test_agent_registration():
    response = httpx.post("http://localhost:8000/api/v1/auth/register", json={
        "name": "testname",
        "email": "agent@test.com",
        "password": "testpassword",
        "role": "agent",
        "serial_number": "123456",
    })
    assert response.status_code == 200
    assert response.json().get("message") == "Login successful"
    assert response.json().get("level") == 0
    assert response.json().get("email") == "agent@test.com"
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

@pytest.mark.asyncio
async def test_invalid_registration():
    response = httpx.post("http://localhost:8000/api/v1/auth/register", json={
        "name": "testname",
        "email": "agent2@test.com",
        "password": "testpassword",
        "role": "agent",
    })
    assert response.status_code == 400
    assert response.json().get("message") == "Invalid serial number"

@pytest.mark.asyncio
async def test_duplicate_registration():
    response = httpx.post("http://localhost:8000/api/v1/auth/register", json={
        "email": "agent@test.com",
        "password": "testpassword",
        "role": "agent",
        "serial_number": "123456",
    })
    assert response.status_code == 400
    assert response.json().get("message") == "Email already taken"

@pytest.mark.asyncio
async def test_login():
    response = httpx.post("http://localhost:8000/api/v1/auth/login", json={
        "email": "testemail@test.com",
        "password": "testpassword",
    })
    assert response.status_code == 200
    assert response.json().get("message") == "Login successful"
    assert response.json().get("level") == 0
    assert response.json().get("email") == "testemail@test.com"
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

@pytest.mark.asyncio
async def test_invalid_login():
    response = httpx.post("http://localhost:8000/api/v1/auth/login", json={
        "email": "testemail@test.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401
    assert response.json().get("message") == "Invalid credentials"
