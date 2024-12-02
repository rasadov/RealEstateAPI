import io
import pytest
from fastapi.testclient import TestClient
from fastapi import UploadFile
import httpx

from src.main import app
from .utils import login_or_register_user, login_or_register_agent, generate_images_as_bytes
from .config import (TEST_CLIENT_EMAIL, TEST_CLIENT_PASS,
                     TEST_AGENT_EMAIL, TEST_AGENT_PASS,
                     TEST_MODERATOR_EMAIL, TEST_MODERATOR_PASS)


client = TestClient(app)

client_response = login_or_register_user(TEST_CLIENT_EMAIL, TEST_CLIENT_PASS)
agent_response = login_or_register_agent(TEST_AGENT_EMAIL, TEST_AGENT_PASS)
moderator_response = login_or_register_user(TEST_MODERATOR_EMAIL, TEST_MODERATOR_PASS)

@pytest.mark.asyncio
async def test_property_creation():
    images = generate_images_as_bytes(5)
    files = [("files", (f"image_{i}.png", image, "image/png")) for i, image in enumerate(images)]

    # Assuming you have a way to get the access token
    access_token = agent_response.cookies["access_token"]
    refresh_token = agent_response.cookies["refresh_token"]
    
    data = {
        "name": "test_property",
        "description": "test_description",
        "price": "1000.0",  # Ensure all values are strings for form data
        "latitude": "0.0",
        "longitude": "0.0",
        "category": "apartment",
        "total_area": "100.0",
        "living_area": "50.0",
        "bedrooms": "2",
        "living_rooms": "1",
        "floor": "1",
        "floors": "5",
        "district": "test_district",
        "address": "test_address"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/property/create",
            data=data,
            files=files,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            },
            cookies={
                "refresh_token": refresh_token,
                "access_token": access_token
            },
            timeout=30
        )

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_property_update():
    access_token = agent_response.cookies["access_token"]
    refresh_token = agent_response.cookies["refresh_token"]
    
    response = httpx.put(
        "http://localhost:8000/api/v1/property/19",
        json={
            "name": "test_property_2",
            "description": "test_description_2",
            "price": 100000.0,
            "location" : {
            "latitude": 0.0,
            "longitude": 0.0,
            },
            "info": {
            "category": "house",
            "total_area": 200.0,
            "living_area": 60.0,
            "bedrooms": 4,
            "living_rooms": 3,
            "floors": 1,
            "district": "test_district_2",
            "address": "test_address_2"
            }
        },
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        },
        cookies={
            "refresh_token": refresh_token,
            "access_token": access_token
        }
    )

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_adding_image_to_property():
    access_token = agent_response.cookies["access_token"]
    refresh_token = agent_response.cookies["refresh_token"]

    # Generate images
    images = generate_images_as_bytes(1)
    files = [("files", (f"image_{i}.png", image, "image/png")) for i, image in enumerate(images)]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/property/image/19",
            files=files,
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            cookies={
                "refresh_token": refresh_token,
                "access_token": access_token
            }
        )

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_adding_image_to_property_2():
    access_token = agent_response.cookies["access_token"]
    refresh_token = agent_response.cookies["refresh_token"]

    # Generate images
    images = generate_images_as_bytes(5)
    files = [("files", (f"image_{i}.png", image, "image/png")) for i, image in enumerate(images)]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/property/image/19",
            files=files,
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            cookies={
                "refresh_token": refresh_token,
                "access_token": access_token
            }
        )

    assert response.status_code == 400

# @pytest.mark.asyncio
# async def test_property_deletion():
#     property_id = 2

#     access_token = agent_response.cookies["access_token"]
#     refresh_token = agent_response.cookies["refresh_token"]

#     async with httpx.AsyncClient() as client:
#         response = await client.delete(
#             f"http://localhost:8000/api/v1/property/{property_id}",
#             headers={
#                 "Authorization": f"Bearer {access_token}",
#             },
#             cookies={
#                 "refresh_token": refresh_token,
#                 "access_token": access_token
#             }
#         )

#     assert response.status_code == 200

@pytest.mark.asyncio
async def test_property_search():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/property/",
            params={
            "page": "1",
            "elements": "10"
            },
            headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
            }
        )

    print("TEST PROPERTY SEARCH")
    print(response.json())
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_property_search_2():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/property/",
        )

    print("TEST PROPERTY SEARCH")
    print(response.json())
    assert response.status_code == 200

# @pytest.mark.asyncio
# async def test_property_search_by_id():
#     property_id = 19

#     async with httpx.AsyncClient() as client:
#         response = await client.get(
#             f"http://localhost:8000/api/v1/property/{property_id}",
#         )
    
#     print("TEST PROPERTY SEARCH BY ID")
#     print(response.json())
#     assert response.status_code == 200

# @pytest.mark.asyncio
# async def test_property_search_by_agent():
#     agent_id = 1

#     async with httpx.AsyncClient() as client:
#         response = await client.get(
#             f"http://localhost:8000/api/v1/property/agent/{agent_id}/page",
#         )

#     print("TEST PROPERTY SEARCH BY AGENT")
#     # print(response.json())
#     assert response.status_code == 200

# @pytest.mark.asyncio
# async def test_property_search_by_agent_2():
#     agent_id = 1

#     async with httpx.AsyncClient() as client:
#         response = await client.get(
#             f"http://localhost:8000/api/v1/property/agent/{agent_id}/page",
#             params={
#             "page": "1",
#             "elements": "10"
#             }
#         )

#     print("TEST PROPERTY SEARCH BY AGENT")
#     # print(response.json())
#     assert response.status_code == 200
