import httpx

import pytest
from fastapi.testclient import TestClient

from src.main import app
from .utils import generate_register_credentials
from .config import TEST_AGENT_EMAIL, TEST_AGENT_PASS


client = TestClient(app)
email, password = generate_register_credentials()

@pytest.mark.asyncio
async def test_change_password():
    global email, password
    response = httpx.post("http://localhost:8000/api/v1/auth/register", json={
        "name": "testname",
        "email": email,
        "password": password,
        "role": "buyer",
    })

    assert response.status_code == 200

    cookies = response.cookies

    response = httpx.patch("http://localhost:8000/api/v1/user/change-password", json={
        "email": email,
        "old_password": password,
        "new_password": "newpassword"
    }, cookies=cookies)

    assert response.status_code == 200

    response = httpx.post("http://localhost:8000/api/v1/auth/login", json={
        "email": email,
        "password": "newpassword"
    })

    assert response.status_code == 200
    password = "newpassword"

@pytest.mark.asyncio
async def test_forgot_password():
    global email, password
    response = httpx.post("http://localhost:8000/api/v1/user/forgot-password", json={
        "email": email
    })

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_forgot_password():
    response = httpx.post("http://localhost:8000/api/v1/user/forgot-password", json={
        "email": "userdoesnotexist@doesntexist.com"
    })

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_user_update():
    email, password = generate_register_credentials()
    response = httpx.post("http://localhost:8000/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "role": "buyer",
        "name": "testname"
    })

    assert response.status_code == 200

    cookies = response.cookies

    response = httpx.patch("http://localhost:8000/api/v1/user/update/user", json={
        "name": "newname",
        "phone": "1234567890",
        "bio": "newbio"
    }, cookies=cookies)

    assert response.status_code == 200

    response = httpx.post("http://localhost:8000/api/v1/auth/logout", cookies=cookies)

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_agent_update():
    response = httpx.post("http://localhost:8000/api/v1/auth/login", json={
        "email": TEST_AGENT_EMAIL,
        "password": TEST_AGENT_PASS
    })

    assert response.status_code == 200

    cookies = response.cookies

    response = httpx.patch("http://localhost:8000/api/v1/user/update/agent", json={
        "company": "newcompany",
    }, cookies=cookies)

@pytest.mark.asyncio
async def test_user_deletion():
    email, password = generate_register_credentials()
    response = httpx.post("http://localhost:8000/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "role": "buyer",
        "name": "testdelete"
    })

    assert response.status_code == 200

    cookies = response.cookies

    response = httpx.delete("http://localhost:8000/api/v1/user/delete", cookies=cookies)

    assert response.status_code == 200

    response = httpx.post("http://localhost:8000/api/v1/auth/login", json={
        "email": email,
        "password": password
    })

    assert response.status_code == 401 or response.status_code == 400
