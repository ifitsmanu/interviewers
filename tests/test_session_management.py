"""Test suite for MongoDB-backed session management."""

import pytest
import pytest_asyncio
import asyncio
from typing import Dict, Any, AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient
from interviewers.core.pipeline import InterviewPipeline
from interviewers.core.session_manager import SessionManager
from interviewers.models.interview import InterviewContext, InterviewContextManager
from interviewers.services.database import get_client, get_sessions_collection

pytestmark = pytest.mark.asyncio

@pytest_asyncio.fixture(autouse=True)
async def cleanup():
    """Clean up test data after each test."""
    yield
    collection = await get_sessions_collection()
    await collection.delete_many({})

@pytest_asyncio.fixture
async def mongodb_client() -> AsyncGenerator[AsyncIOMotorClient, None]:
    """Create a MongoDB client for each test."""
    client = await get_client()
    yield client

@pytest_asyncio.fixture
async def pipeline(mongodb_client):
    """Create a pipeline instance with MongoDB connection."""
    return InterviewPipeline({})

@pytest_asyncio.fixture
async def session_manager(mongodb_client):
    """Create a session manager instance with MongoDB connection."""
    manager = SessionManager()
    yield manager
    # Clean up test data after each test
    await get_sessions_collection().delete_many({})

async def test_session_creation(pipeline):
    """Test basic session creation and retrieval."""
    session_id = await pipeline.create_interview_session("test_candidate")
    assert session_id is not None
    
    session_data = await pipeline.get_session_data(session_id)
    assert session_data is not None
    assert session_data["candidate_id"] == "test_candidate"
    assert session_data["current_phase"] == "introduction"

async def test_session_data_updates(pipeline):
    """Test updating session data with responses and metrics."""
    session_id = await pipeline.create_interview_session("test_candidate")
    
    # Test response addition
    await pipeline.session_manager.add_response(
        session_id,
        "introduction",
        "Hello, I'm interested in the position"
    )
    
    session_data = await pipeline.get_session_data(session_id)
    assert "responses" in session_data
    assert "introduction" in session_data["responses"]
    assert len(session_data["responses"]["introduction"]) == 1
    
    # Test metrics updates
    test_metrics = {
        "technical_score": 0.8,
        "behavioral_score": 0.7,
        "cultural_score": 0.9
    }
    await pipeline.session_manager.update_metrics(session_id, test_metrics)
    
    updated_data = await pipeline.get_session_data(session_id)
    assert updated_data["metrics"]["technical_score"] == 0.8
    assert updated_data["metrics"]["behavioral_score"] == 0.7
    assert updated_data["metrics"]["cultural_score"] == 0.9
    # Technical (0.5) * 0.8 + Behavioral (0.3) * 0.7 + Cultural (0.2) * 0.9 = 0.79
    assert updated_data["metrics"]["overall_score"] == pytest.approx(0.79)  # weighted average

async def test_context_manager_session_integration(pipeline):
    """Test integration between InterviewContextManager and SessionManager."""
    context_manager = InterviewContextManager("user")
    
    # Simulate pipeline process with context
    test_response = "I have 5 years of experience"
    await context_manager.process(
        test_response,
        {
            "_pipeline": pipeline,
            "candidate_id": "test_candidate",
            "metrics": {
                "technical_score": 0.75
            }
        }
    )
    
    # Verify session was created and data was stored
    assert context_manager.session_id is not None
    session_data = await pipeline.get_session_data(context_manager.session_id)
    assert session_data is not None
    assert "responses" in session_data
    assert session_data["metrics"]["technical_score"] == 0.75

async def test_session_phase_transitions(pipeline):
    """Test handling of interview phase transitions."""
    context_manager = InterviewContextManager("assistant")
    
    # Initialize session through process
    await context_manager.process(
        {"response": "Let's begin"},
        {
            "_pipeline": pipeline,
            "candidate_id": "test_candidate",
            "next_phase": "technical"
        }
    )
    
    # Verify phase transition
    session_data = await pipeline.get_session_data(context_manager.session_id)
    assert session_data["current_phase"] == "technical"
    assert "assistant_response" in session_data
    assert session_data["assistant_response"] == "Let's begin"

async def test_session_completion(pipeline):
    """Test session completion functionality."""
    session_id = await pipeline.create_interview_session("test_candidate")
    
    # Add some interview data
    await pipeline.session_manager.add_response(
        session_id,
        "technical",
        "Here's my solution..."
    )
    await pipeline.session_manager.update_metrics(
        session_id,
        {"technical_score": 0.9}
    )
    
    # End session
    assert await pipeline.end_interview_session(session_id)
    
    # Verify session is marked as ended
    session_data = await pipeline.get_session_data(session_id)
    assert session_data["end_time"] is not None
