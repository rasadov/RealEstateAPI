import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_forgot_password():
    pass

@pytest.mark.asyncio
async def test_reset_password():
    pass

@pytest.mark.asyncio
async def test_user_update():
    pass

@pytest.mark.asyncio
async def test_user_deletion():
    pass

@pytest.mark.asyncio
async def test_user_search():
    pass
