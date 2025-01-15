import os

from dotenv import load_dotenv
import httpx

load_dotenv()

TEST_MODERATOR_EMAIL = os.getenv("MODERATOR_EMAIL")
TEST_MODERATOR_PASS = os.getenv("MODERATOR_PASSWORD")

TEST_AGENT_EMAIL = os.getenv("AGENT_EMAIL")
TEST_AGENT_PASS = os.getenv("AGENT_PASSWORD")

TEST_CLIENT_EMAIL = os.getenv("CLIENT_EMAIL")
TEST_CLIENT_PASS = os.getenv("CLIENT_PASSWORD")

with httpx.Client() as client:
    codes = []
    response = client.post("http://localhost:5001/api/v1/auth/login", json={
        "email": TEST_MODERATOR_EMAIL,
        "password": TEST_MODERATOR_PASS
    })

    codes.append(response.status_code)

    if response.status_code > 299:
        response = client.post("http://localhost:5001/api/v1/auth/register", json={
            "name": "testname",
            "email": TEST_MODERATOR_EMAIL,
            "password": TEST_MODERATOR_PASS,
            "role": "moderator",
        })

        codes.append(response.status_code)
    
    response = client.post("http://localhost:5001/api/v1/auth/login", json={
        "email": TEST_AGENT_EMAIL,
        "password": TEST_AGENT_PASS
    })
    codes.append(response.status_code)

    if response.status_code > 299:
        response = client.post("http://localhost:5001/api/v1/auth/register", json={
            "name": "testname",
            "email": TEST_AGENT_EMAIL,
            "password": TEST_AGENT_PASS,
            "role": "agent",
            "serial_number": "123456",
        })
        codes.append(response.status_code)

    response = client.post("http://localhost:5001/api/v1/auth/login", json={
        "email": TEST_CLIENT_EMAIL,
        "password": TEST_CLIENT_PASS
    })
    codes.append(response.status_code)

    if response.status_code > 299:
        response = client.post("http://localhost:5001/api/v1/auth/register", json={
            "name": "testname",
            "email": TEST_CLIENT_EMAIL,
            "password": TEST_CLIENT_PASS,
            "role": "buyer",
        })
        codes.append(response.status_code)

    with open("status_codes.txt", "w") as f:
        f.write("\n".join(map(str, codes)))
