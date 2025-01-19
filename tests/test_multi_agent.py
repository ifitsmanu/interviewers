"""Test suite for multi-agent interactions and metrics."""

import pytest
import pytest_asyncio
from typing import Dict, Any, AsyncGenerator
from datetime import datetime

from interviewers.core.session_manager import SessionManager
from interviewers.core.agent_manager import AgentManager
from interviewers.core.metrics_manager import MetricsManager
from interviewers.core.phase_manager import PhaseManager
from interviewers.services.database import get_client, get_sessions_collection

pytestmark = pytest.mark.asyncio

@pytest_asyncio.fixture
async def session_manager():
    """Create a session manager instance."""
    manager = SessionManager()
    yield manager
    # Clean up test data
    collection = await get_sessions_collection()
    await collection.delete_many({})

@pytest_asyncio.fixture
async def agent_manager(session_manager):
    """Create an agent manager instance."""
    return AgentManager(session_manager)

@pytest_asyncio.fixture
async def metrics_manager(session_manager):
    """Create a metrics manager instance."""
    return MetricsManager(session_manager)

@pytest_asyncio.fixture
async def phase_manager(session_manager):
    """Create a phase manager instance."""
    return PhaseManager(session_manager)

async def test_multi_agent_activation(
    session_manager, agent_manager, metrics_manager, phase_manager
):
    """Test coordinated activation of multiple agents."""
    # Create session
    session_id = await session_manager.create_session("test_candidate")
    
    # Start pre-interview phase
    assert await phase_manager.start_phase(session_id, "pre_interview")
    
    # Activate consent agent
    assert await agent_manager.activate_agent(session_id, "consent_compliance")
    active_agents = await agent_manager.get_active_agents(session_id)
    assert "consent_compliance" in active_agents
    
    # Record consent agent action
    assert await agent_manager.record_agent_action(
        session_id,
        "consent_compliance",
        "Obtained candidate consent"
    )
    
    # Update consent metrics
    assert await metrics_manager.update_response_quality(
        session_id,
        "pre_interview",
        0.95
    )
    
    # Verify agent status
    session_data = await session_manager.get_session_data(session_id)
    assert session_data["agents"]["consent_compliance"]["status"] == "active"
    assert "last_action" in session_data["agents"]["consent_compliance"]

async def test_technical_evaluation_flow(
    session_manager, agent_manager, metrics_manager, phase_manager
):
    """Test technical evaluation agent workflow."""
    session_id = await session_manager.create_session("test_candidate")
    
    # Start technical phase
    assert await phase_manager.start_phase(session_id, "technical")
    
    # Activate technical agent
    assert await agent_manager.activate_agent(session_id, "technical_evaluation")
    
    # Update technical metrics
    technical_metrics = {
        "system_design": 0.85,
        "coding": 0.9,
        "architecture": 0.8,
        "overall": 0.85
    }
    assert await metrics_manager.update_technical_depth(
        session_id,
        technical_metrics
    )
    
    # Verify metrics
    session_data = await session_manager.get_session_data(session_id)
    assert session_data["metrics"]["technical_depth"] == 0.85
    assert session_data["metrics"]["system_design_depth"] == 0.85
    assert session_data["metrics"]["coding_depth"] == 0.9

async def test_behavioral_assessment_flow(
    session_manager, agent_manager, metrics_manager, phase_manager
):
    """Test behavioral assessment agent workflow."""
    session_id = await session_manager.create_session("test_candidate")
    
    # Start behavioral phase
    assert await phase_manager.start_phase(session_id, "behavioral")
    
    # Activate behavioral agent
    assert await agent_manager.activate_agent(session_id, "behavioral_assessment")
    
    # Update behavioral metrics
    behavioral_metrics = {
        "leadership": 0.8,
        "problem_solving": 0.9,
        "collaboration": 0.85,
        "overall": 0.85
    }
    assert await metrics_manager.update_behavioral_indicators(
        session_id,
        behavioral_metrics
    )
    
    # Verify metrics
    session_data = await session_manager.get_session_data(session_id)
    assert session_data["metrics"]["behavioral_indicators"] == 0.85
    assert session_data["metrics"]["leadership_indicators"] == 0.8
    assert session_data["metrics"]["problem_solving_indicators"] == 0.9

async def test_exit_criteria_immediate(session_manager):
    """Test immediate exit criteria."""
    session_id = await session_manager.create_session("test_candidate")
    
    # Update metrics to trigger immediate exit
    await session_manager.update_metrics(
        session_id,
        {
            "behavioral_score": 0.1,  # Below 0.2 threshold
            "technical_score": 0.05   # Below 0.1 threshold
        }
    )
    
    # Check exit criteria
    exit_status = await session_manager.check_exit_criteria(session_id)
    assert exit_status is not None
    assert exit_status["exit_type"] == "immediate"
    assert "behavioral concerns" in exit_status["reason"].lower()
    assert "technical capability" in exit_status["reason"].lower()
    
    # End session with immediate exit
    assert await session_manager.end_session(
        session_id,
        exit_type="immediate",
        reason=exit_status["reason"]
    )
    
    # Verify session status
    session_data = await session_manager.get_session_data(session_id)
    assert session_data["exit_criteria"]["exit_type"] == "immediate"
    assert session_data["end_time"] is not None

async def test_exit_criteria_mid_interview(session_manager):
    """Test mid-interview exit criteria."""
    session_id = await session_manager.create_session("test_candidate")
    
    # Set current phase to technical
    await session_manager.update_session_data(
        session_id,
        {"current_phase": "technical"}
    )
    
    # Update metrics to trigger mid-interview exit
    await session_manager.update_metrics(
        session_id,
        {
            "technical_score": 0.35,  # Below 0.4 threshold
            "behavioral_score": 0.25,  # Below 0.3 threshold
            "overall_score": 0.3      # Below 0.35 threshold
        }
    )
    
    # Check exit criteria
    exit_status = await session_manager.check_exit_criteria(session_id)
    assert exit_status is not None
    assert exit_status["exit_type"] == "mid_interview"
    assert "technical evaluation below" in exit_status["reason"].lower()
    assert "behavioral assessment below" in exit_status["reason"].lower()
    
    # End session with mid-interview exit
    assert await session_manager.end_session(
        session_id,
        exit_type="mid_interview",
        reason=exit_status["reason"]
    )
    
    # Verify session status
    session_data = await session_manager.get_session_data(session_id)
    assert session_data["exit_criteria"]["exit_type"] == "mid_interview"
    assert session_data["end_time"] is not None

async def test_normal_completion(
    session_manager, agent_manager, metrics_manager, phase_manager
):
    """Test normal interview completion flow."""
    session_id = await session_manager.create_session("test_candidate")
    
    # Complete all phases successfully
    phases = ["pre_interview", "introduction", "technical", "behavioral", "wrap_up"]
    
    for phase in phases:
        # Start phase
        assert await phase_manager.start_phase(session_id, phase)
        
        # Update phase metrics
        await metrics_manager.update_response_quality(session_id, phase, 0.9)
        
        if phase == "technical":
            await metrics_manager.update_technical_depth(
                session_id,
                {
                    "system_design": 0.9,
                    "coding": 0.95,
                    "architecture": 0.85,
                    "overall": 0.9
                }
            )
        elif phase == "behavioral":
            await metrics_manager.update_behavioral_indicators(
                session_id,
                {
                    "leadership": 0.85,
                    "problem_solving": 0.9,
                    "collaboration": 0.95,
                    "overall": 0.9
                }
            )
        
        # End phase
        assert await phase_manager.end_phase(session_id, phase)
    
    # Update final metrics
    await session_manager.update_metrics(
        session_id,
        {
            "technical_score": 0.9,
            "behavioral_score": 0.9,
            "cultural_score": 0.9
        }
    )
    
    # Check exit criteria
    exit_status = await session_manager.check_exit_criteria(session_id)
    assert exit_status is None  # No early exit criteria met
    
    # End session normally
    assert await session_manager.end_session(session_id)
    
    # Verify final session state
    session_data = await session_manager.get_session_data(session_id)
    assert session_data["exit_criteria"]["exit_type"] == "normal"
    assert session_data["end_time"] is not None
    assert session_data["metrics"]["overall_score"] == 0.9  # (0.9 * 0.5 + 0.9 * 0.3 + 0.9 * 0.2)
