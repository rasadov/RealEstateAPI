import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_property_creation():
    pass

@pytest.mark.asyncio
async def test_property_update():
    pass

@pytest.mark.asyncio
async def test_property_deletion():
    pass

@pytest.mark.asyncio
async def test_property_search():
    pass

@pytest.mark.asyncio
async def test_property_search_by_id():
    pass

@pytest.mark.asyncio
async def test_property_search_by_agent():
    pass
