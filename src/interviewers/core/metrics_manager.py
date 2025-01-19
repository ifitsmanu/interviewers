"""Real-time metrics management for interview system."""

from typing import Dict, Any, Optional, List
from datetime import datetime
from .session_manager import SessionManager

class MetricsManager:
    """Manages real-time metrics collection and aggregation."""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
    
    async def update_response_quality(
        self, session_id: str, phase: str, quality_score: float
    ) -> bool:
        """Update response quality metrics.
        
        Args:
            session_id: Unique session identifier
            phase: Current interview phase
            quality_score: Score for response quality
            
        Returns:
            bool: True if update successful
        """
        try:
            metrics = {
                "response_quality": quality_score,
                f"response_quality_{phase}": quality_score
            }
            return await self.session_manager.update_metrics(session_id, metrics)
        except:
            return False
    
    async def update_time_management(
        self, session_id: str, phase: str, time_metrics: Dict[str, float]
    ) -> bool:
        """Update time management metrics.
        
        Args:
            session_id: Unique session identifier
            phase: Current interview phase
            time_metrics: Dictionary of time-related metrics
            
        Returns:
            bool: True if update successful
        """
        try:
            metrics = {
                "time_management": time_metrics.get("overall", 0.0),
                f"time_management_{phase}": time_metrics
            }
            return await self.session_manager.update_metrics(session_id, metrics)
        except:
            return False
    
    async def update_technical_depth(
        self, session_id: str, depth_metrics: Dict[str, Any]
    ) -> bool:
        """Update technical depth evaluation metrics.
        
        Args:
            session_id: Unique session identifier
            depth_metrics: Dictionary of technical depth metrics
            
        Returns:
            bool: True if update successful
        """
        try:
            metrics = {
                "technical_depth": depth_metrics.get("overall", 0.0),
                "system_design_depth": depth_metrics.get("system_design", 0.0),
                "coding_depth": depth_metrics.get("coding", 0.0),
                "architecture_depth": depth_metrics.get("architecture", 0.0)
            }
            return await self.session_manager.update_metrics(session_id, metrics)
        except:
            return False
    
    async def update_behavioral_indicators(
        self, session_id: str, indicators: Dict[str, Any]
    ) -> bool:
        """Update behavioral assessment indicators.
        
        Args:
            session_id: Unique session identifier
            indicators: Dictionary of behavioral indicators
            
        Returns:
            bool: True if update successful
        """
        try:
            metrics = {
                "behavioral_indicators": indicators.get("overall", 0.0),
                "leadership_indicators": indicators.get("leadership", 0.0),
                "problem_solving_indicators": indicators.get("problem_solving", 0.0),
                "collaboration_indicators": indicators.get("collaboration", 0.0)
            }
            return await self.session_manager.update_metrics(session_id, metrics)
        except:
            return False
    
    async def get_agent_metrics(
        self, session_id: str, agent: str
    ) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific agent.
        
        Args:
            session_id: Unique session identifier
            agent: Name of the agent
            
        Returns:
            Optional[Dict[str, Any]]: Agent metrics if found
        """
        try:
            session_data = await self.session_manager.get_session_data(session_id)
            if not session_data or "agents" not in session_data:
                return None
            return session_data["agents"].get(agent, {}).get("metrics")
        except:
            return None
    
    async def get_phase_metrics(
        self, session_id: str, phase: str
    ) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific phase.
        
        Args:
            session_id: Unique session identifier
            phase: Interview phase
            
        Returns:
            Optional[Dict[str, Any]]: Phase metrics if found
        """
        try:
            session_data = await self.session_manager.get_session_data(session_id)
            if not session_data or "phases" not in session_data:
                return None
            
            metrics = {}
            if phase in session_data["phases"]:
                phase_data = session_data["phases"][phase]
                metrics.update({
                    "status": phase_data.get("status"),
                    "duration": None
                })
                
                # Calculate duration if phase has start and end times
                start = phase_data.get("start_time")
                end = phase_data.get("end_time")
                if start and end:
                    start_dt = datetime.fromisoformat(start)
                    end_dt = datetime.fromisoformat(end)
                    metrics["duration"] = (end_dt - start_dt).total_seconds()
                
                # Add phase-specific metrics
                for key in session_data["metrics"]:
                    if key.endswith(f"_{phase}"):
                        metrics[key] = session_data["metrics"][key]
            
            return metrics
        except:
            return None
