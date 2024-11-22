import os

import pytest
import httpx
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)
const_rand_1 = os.urandom(8).hex()


@pytest.mark.asyncio
async def test_buyer_registration():
    response = httpx.post("http://localhost:8000/api/v1/auth/register", json={
        "name": "testname" + const_rand_1,
        "email": f"testemail{const_rand_1}@test.com",
        "password": "testpassword",
        "role": "buyer",
    })
    assert response.status_code == 200
    assert response.json().get("detail") == "Login successful"
    assert response.json().get("level") == 0
    assert response.json().get("email") == f"testemail{const_rand_1}@test.com"
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

@pytest.mark.asyncio
async def test_agent_registration():
    rand = os.urandom(8).hex()
    response = httpx.post("http://localhost:8000/api/v1/auth/register", json={
        "name": "testname" + rand,
        "email": f"testagent{rand}@test.com",
        "password": "testpassword",
        "role": "agent",
        "serial_number": "123456",
    })
    assert response.status_code == 200
    assert response.json().get("detail") == "Login successful"
    assert response.json().get("level") == 0
    assert response.json().get("email") == f"testagent{rand}@test.com"
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

@pytest.mark.asyncio
async def test_invalid_registration():
    rand = os.urandom(8).hex()
    response = httpx.post("http://localhost:8000/api/v1/auth/register", json={
        "name": "testname" + rand,
        "email": f"testemail{rand}@test.com",
        "password": "testpassword",
        "role": "agent",
    })
    assert response.status_code == 400
    assert response.json().get("detail") == "Invalid serial number"

@pytest.mark.asyncio
async def test_duplicate_registration():
    response = httpx.post("http://localhost:8000/api/v1/auth/register", json={
        "name": "testname" + const_rand_1,
        "email": f"testemail{const_rand_1}@test.com",
        "password": "testpassword",
        "role": "agent",
    })
    assert response.status_code == 400
    assert response.json().get("detail") == "Email already taken"

@pytest.mark.asyncio
async def test_login():
    response = httpx.post("http://localhost:8000/api/v1/auth/login", json={
        "email": f"testemail{const_rand_1}@test.com",
        "password": "testpassword",
    })
    assert response.status_code == 200
    assert response.json().get("detail") == "Login successful"
    assert response.json().get("level") == 0
    assert response.json().get("email") == f"testemail{const_rand_1}@test.com"
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

@pytest.mark.asyncio
async def test_invalid_login():
    response = httpx.post("http://localhost:8000/api/v1/auth/login", json={
        "email": f"testemail{const_rand_1}@test.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401
    assert response.json().get("detail") == "Invalid credentials"

@pytest.mark.asyncio
async def test_log_out():
    response = httpx.post("http://localhost:8000/api/v1/auth/login", json={
        "email": f"testemail{const_rand_1}@test.com",
        "password": "testpassword",
    })

    assert response.status_code == 200
    assert response.json().get("detail") == "Login successful"

    response = httpx.post("http://localhost:8000/api/v1/auth/logout", cookies=response.cookies)
    assert response.status_code == 200
    assert response.json().get("detail") == "Logged out successfully"
    assert response.cookies.get("access_token") == None

@pytest.mark.asyncio
async def test_refresh():
    response = httpx.post("http://localhost:8000/api/v1/auth/login", json={
        "email": f"testemail{const_rand_1}@test.com",
        "password": "testpassword",
    })
    assert response.status_code == 200
    assert response.json().get("detail") == "Login successful"

    response = httpx.post("http://localhost:8000/api/v1/auth/refresh", cookies=response.cookies)

    assert response.status_code == 200
    assert response.json().get("detail") == "Token refreshed"
