"""Agent management and coordination for interview system."""

from typing import Dict, Any, Optional, List
from datetime import datetime
from .session_manager import SessionManager

class AgentManager:
    """Manages interview agents and their interactions."""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
    
    async def activate_agent(self, session_id: str, agent_name: str) -> bool:
        """Activate a specific agent for an interview session.
        
        Args:
            session_id: Unique session identifier
            agent_name: Name of the agent to activate
            
        Returns:
            bool: True if agent activated successfully
        """
        try:
            return await self.session_manager.update_session_data(
                session_id,
                {
                    f"agents.{agent_name}.status": "active",
                    f"agents.{agent_name}.last_action": datetime.now().isoformat()
                }
            )
        except:
            return False
    
    async def deactivate_agent(self, session_id: str, agent_name: str) -> bool:
        """Deactivate a specific agent.
        
        Args:
            session_id: Unique session identifier
            agent_name: Name of the agent to deactivate
            
        Returns:
            bool: True if agent deactivated successfully
        """
        try:
            return await self.session_manager.update_session_data(
                session_id,
                {
                    f"agents.{agent_name}.status": "inactive",
                    f"agents.{agent_name}.last_action": datetime.now().isoformat()
                }
            )
        except:
            return False
    
    async def update_agent_metrics(
        self, session_id: str, agent_name: str, metrics: Dict[str, Any]
    ) -> bool:
        """Update metrics for a specific agent.
        
        Args:
            session_id: Unique session identifier
            agent_name: Name of the agent
            metrics: Dictionary of metrics to update
            
        Returns:
            bool: True if metrics updated successfully
        """
        try:
            return await self.session_manager.update_session_data(
                session_id,
                {f"agents.{agent_name}.metrics": metrics}
            )
        except:
            return False
    
    async def get_active_agents(self, session_id: str) -> List[str]:
        """Get list of currently active agents.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            List[str]: List of active agent names
        """
        try:
            session_data = await self.session_manager.get_session_data(session_id)
            if not session_data or "agents" not in session_data:
                return []
            
            return [
                agent_name
                for agent_name, agent_data in session_data["agents"].items()
                if agent_data.get("status") == "active"
            ]
        except:
            return []
    
    async def record_agent_action(
        self, session_id: str, agent_name: str, action: str
    ) -> bool:
        """Record an action taken by an agent.
        
        Args:
            session_id: Unique session identifier
            agent_name: Name of the agent
            action: Description of the action taken
            
        Returns:
            bool: True if action recorded successfully
        """
        try:
            return await self.session_manager.update_session_data(
                session_id,
                {
                    f"agents.{agent_name}.last_action": action,
                    f"agents.{agent_name}.last_action_time": datetime.now().isoformat()
                }
            )
        except:
            return False
