"""Test MongoDB connection."""
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def test_mongo():
    """Test MongoDB connection."""
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    await client.admin.command('ping')
    print('MongoDB connection successful!')

if __name__ == '__main__':
    asyncio.run(test_mongo())
