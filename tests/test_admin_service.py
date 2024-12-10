import httpx

import pytest
from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)

# OPERATIONS ON USERS

# GET METHODS

@pytest.mark.asyncio
async def test_get_users():
    pass

@pytest.mark.asyncio
async def test_get_user_by_id():
    pass

@pytest.mark.asyncio
async def test_get_user_by_email():
    pass

@pytest.mark.asyncio
async def test_get_user_by_email_2():
    pass

# PUT METHODS

@pytest.mark.asyncio
async def test_update_user():
    pass

@pytest.mark.asyncio
async def test_reset_user_password():
    pass

@pytest.mark.asyncio
async def test_update_user_2():
    pass

# DELETE METHODS

@pytest.mark.asyncio
async def test_delete_user():
    pass

# OPERATIONS ON PROPERTIES

# GET METHODS

@pytest.mark.asyncio
async def test_property_search():
    pass

@pytest.mark.asyncio
async def test_property_search_2():
    pass

@pytest.mark.asyncio
async def test_property_search_by_id():
    pass

@pytest.mark.asyncio
async def test_property_search_by_agent():
    pass

# PUT METHODS

@pytest.mark.asyncio
async def test_update_property():
    pass

# PATCH METHODS

@pytest.mark.asyncio
async def test_approve_property():
    pass

@pytest.mark.asyncio
async def test_approve_property_2():
    pass

@pytest.mark.asyncio
async def test_deactivate_property():
    pass

# DELETE METHODS

@pytest.mark.asyncio
async def test_delete_property():
    pass
