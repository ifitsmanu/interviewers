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
        loop = asyncio.get_running_loop()
        _client = AsyncIOMotorClient(MONGO_URI, io_loop=loop)
        # Test connection
        await _client.admin.command('ping')
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
