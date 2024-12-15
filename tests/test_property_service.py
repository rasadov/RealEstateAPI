import httpx

import pytest
from fastapi.testclient import TestClient

from src.main import app
from .utils import login_or_register_user, login_or_register_agent, generate_images_as_bytes
from .config import (TEST_CLIENT_EMAIL, TEST_CLIENT_PASS,
                     TEST_AGENT_EMAIL, TEST_AGENT_PASS,
                     TEST_MODERATOR_EMAIL, TEST_MODERATOR_PASS)


client = TestClient(app)

client_response = login_or_register_user(TEST_CLIENT_EMAIL, TEST_CLIENT_PASS)
agent_response = login_or_register_agent(TEST_AGENT_EMAIL, TEST_AGENT_PASS)
moderator_response = login_or_register_user(TEST_MODERATOR_EMAIL, TEST_MODERATOR_PASS)


# GET METHODS

@pytest.mark.asyncio
async def test_property_search():
    params = {
        "page": "1",
        "elements": "10"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/property/",
            params=params,
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

@pytest.mark.asyncio
async def test_property_search_by_id():
    property_id = 19

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8000/api/v1/property/record/{property_id}",
        )
    
    print("TEST PROPERTY SEARCH BY ID")
    print(response.json())
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_property_search_by_id():
    property_id = 15

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8000/api/v1/property/record/{property_id}",
        )
    
    print("TEST PROPERTY SEARCH BY ID")
    print(response.json())
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_property_search_by_agent():
    agent_id = 1

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8000/api/v1/property/agent/{agent_id}/page",
        )

    print("TEST PROPERTY SEARCH BY AGENT")
    # print(response.json())
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_property_search_by_agent_2():
    agent_id = 1

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8000/api/v1/property/agent/{agent_id}/page",
            params={
            "page": "1",
            "elements": "10"
            }
        )

    print("TEST PROPERTY SEARCH BY AGENT")
    # print(response.json())
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_filtering_properties():
    params = {
        "page": "1",
        "elements": "10",
        "max_price": "10000"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/property/",
            params=params
        )

    print("TEST FILTERING PROPERTIES")
    print(response.json())
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_filtering_properties_2():
    params = {
        "page": "1",
        "elements": "10",
        "min_area": "10000",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/property/",
            params=params
        )

    print("TEST FILTERING PROPERTIES")
    print(response.json())
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_map():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/property/map"
        )

    print("TEST MAP")
    print(response.json())
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_listings():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/property/listings/page",
            params={
                "offset": 0,
                "elements": 10
            }
        )

    print("TEST LISTINGS")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_listings_creation():
    files = generate_images_as_bytes(5)
    files = [("images", (f"image_{i}.png", image, "image/png")) for i, image in enumerate(files)]
    cookies = agent_response.cookies
    data = {
        "name": "name_of_listing",
        "description": "description_of_listing",
        "district": "district_of_listing",
        "address": "address_of_listing"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/property/listing",
            data=data,
            files=files,
            headers={
                "Authorization": f"Bearer {cookies['access_token']}",
                "Accept": "application/json"
            },
            cookies={
                "refresh_token": cookies["refresh_token"],
                "access_token": cookies["access_token"]
            },
            timeout=30
        )

    print("TEST LISTINGS CREATION")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_listing_by_id():
    listing_id = 1

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8000/api/v1/property/listing/{listing_id}"
        )

    print("TEST LISTING BY ID")
    assert response.status_code == 200


# # POST METHODS

# @pytest.mark.asyncio
# async def test_property_creation():
#     images = generate_images_as_bytes(5)
#     files = [("files", (f"image_{i}.png", image, "image/png")) for i, image in enumerate(images)]

#     # Assuming you have a way to get the access token
#     access_token = agent_response.cookies["access_token"]
#     refresh_token = agent_response.cookies["refresh_token"]
    
#     data = {
#         "name": "test_property",
#         "description": "test_description",
#         "price": "1000.0",  # Ensure all values are strings for form data
#         "latitude": "0.0",
#         "longitude": "0.0",
#         "category": "apartment",
#         "total_area": "100.0",
#         "living_area": "50.0",
#         "bedrooms": "2",
#         "living_rooms": "1",
#         "floor": "1",
#         "floors": "5",
#         "district": "test_district",
#         "address": "test_address"
#     }
    
#     async with httpx.AsyncClient() as client:
#         response = await client.post(
#             "http://localhost:8000/api/v1/property/create",
#             data=data,
#             files=files,
#             headers={
#                 "Authorization": f"Bearer {access_token}",
#                 "Accept": "application/json"
#             },
#             cookies={
#                 "refresh_token": refresh_token,
#                 "access_token": access_token
#             },
#             timeout=30
#         )

#     assert response.status_code == 200

# @pytest.mark.asyncio
# async def test_adding_image_to_property():
#     access_token = agent_response.cookies["access_token"]
#     refresh_token = agent_response.cookies["refresh_token"]

#     property_id = 19

#     # Generate images
#     images = generate_images_as_bytes(1)
#     files = [("files", (f"image_{i}.png", image, "image/png")) for i, image in enumerate(images)]

#     async with httpx.AsyncClient() as client:
#         response = await client.post(
#             f"http://localhost:8000/api/v1/property/image/{property_id}",
#             files=files,
#             headers={
#                 "Authorization": f"Bearer {access_token}",
#             },
#             cookies={
#                 "refresh_token": refresh_token,
#                 "access_token": access_token
#             }
#         )

#     assert response.status_code == 200

# @pytest.mark.asyncio
# async def test_adding_image_to_property_2():
#     access_token = agent_response.cookies["access_token"]
#     refresh_token = agent_response.cookies["refresh_token"]

#     property_id = 19

#     # Generate images
#     images = generate_images_as_bytes(5)
#     files = [("files", (f"image_{i}.png", image, "image/png")) for i, image in enumerate(images)]

#     async with httpx.AsyncClient() as client:
#         response = await client.post(
#             f"http://localhost:8000/api/v1/property/image/{property_id}",
#             files=files,
#             headers={
#                 "Authorization": f"Bearer {access_token}",
#             },
#             cookies={
#                 "refresh_token": refresh_token,
#                 "access_token": access_token
#             }
#         )

#     assert response.status_code == 400

# # PUT METHODS

# @pytest.mark.asyncio
# async def test_property_update():
#     access_token = agent_response.cookies["access_token"]
#     refresh_token = agent_response.cookies["refresh_token"]

#     property_id = 19

#     new_data = {
#             "name": "test_property_2",
#             "description": "test_description_2",
#             "price": 100000.0,
#             "location" : {
#             "latitude": 0.0,
#             "longitude": 0.0,
#             },
#             "info": {
#             "category": "house",
#             "total_area": 200.0,
#             "living_area": 60.0,
#             "bedrooms": 4,
#             "living_rooms": 3,
#             "floors": 1,
#             "district": "test_district_2",
#             "address": "test_address_2"
#             }
#         }

#     response = httpx.put(
#         f"http://localhost:8000/api/v1/property/{property_id}",
#         json=new_data,
#         headers={
#             "Authorization": f"Bearer {access_token}",
#             "Accept": "application/json"
#         },
#         cookies={
#             "refresh_token": refresh_token,
#             "access_token": access_token
#         }
#     )

#     assert response.status_code == 200

# # DELETE METHODS

# @pytest.mark.asyncio
# async def test_property_deletion():
    # property_id = 21

    # access_token = agent_response.cookies["access_token"]
    # refresh_token = agent_response.cookies["refresh_token"]

    # async with httpx.AsyncClient() as client:
    #     response = await client.delete(
    #         f"http://localhost:8000/api/v1/property/{property_id}",
    #         headers={
    #             "Authorization": f"Bearer {access_token}",
    #         },
    #         cookies={
    #             "refresh_token": refresh_token,
    #             "access_token": access_token
    #         }, params={"is_sold": "true"}
    #     )

    # assert response.status_code == 200

# @pytest.mark.asyncio
# async def test_property_deletion():
#     property_id = 22

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
#             }, params={"is_sold": "true"}
#         )

#     assert response.status_code == 200

# @pytest.mark.asyncio
# async def test_image_deletion():
#     image_id = 93
#     property_id = 19

#     access_token = agent_response.cookies["access_token"]
#     refresh_token = agent_response.cookies["refresh_token"]

#     async with httpx.AsyncClient() as client:
#         response = await client.delete(
#             f"http://localhost:8000/api/v1/property/{property_id}/image/{image_id}",
#             headers={
#                 "Authorization": f"Bearer {access_token}",
#             },
#             cookies={
#                 "refresh_token": refresh_token,
#                 "access_token": access_token
#             },
#         )

#     assert response.status_code == 200
