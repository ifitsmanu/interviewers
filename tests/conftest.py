"""Test configuration and fixtures."""

import pytest
import pytest_asyncio
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from interviewers.services.database import get_client, get_sessions_collection

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()
    asyncio.set_event_loop(None)

@pytest_asyncio.fixture(scope="session")
async def mongodb_client(event_loop):
    """Create a MongoDB client for testing."""
    client = None
    try:
        client = await get_client()
        yield client
    finally:
        if client:
            try:
                await client.close()
            except Exception:
                pass

@pytest_asyncio.fixture(autouse=True)
async def clean_mongodb(mongodb_client, event_loop):
    """Clean up MongoDB collections before and after each test."""
    try:
        collection = await get_sessions_collection()
        if collection is not None:
            await collection.delete_many({})
        yield
    finally:
        try:
            collection = await get_sessions_collection()
            if collection is not None:
                await collection.delete_many({})
        except Exception:
            pass
