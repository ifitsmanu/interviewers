"""MongoDB database connection and configuration."""

import os
import asyncio
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None
_sessions: Optional[AsyncIOMotorCollection] = None

async def get_client() -> AsyncIOMotorClient:
    """Get MongoDB client using current event loop."""
    global _client
    if _client is None:
        try:
            loop = asyncio.get_event_loop()
            client = AsyncIOMotorClient(MONGO_URI, io_loop=loop)
            # Test connection
            await client.admin.command('ping')
            _client = client
        except Exception as e:
            print(f"Error initializing MongoDB client: {e}")
            raise
    assert _client is not None  # for mypy
    return _client

async def get_db() -> AsyncIOMotorDatabase:
    """Get database instance."""
    global _db
    if _db is None:
        client = await get_client()
        _db = client["interviewers"]
    return _db

async def get_sessions_collection() -> AsyncIOMotorCollection:
    """Get sessions collection."""
    global _sessions
    if _sessions is None:
        db = await get_db()
        _sessions = db["sessions"]
    return _sessions
