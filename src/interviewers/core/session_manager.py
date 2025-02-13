"""Session management implementation using MongoDB."""

from typing import Dict, Any, Optional
from datetime import datetime
from bson.objectid import ObjectId
from ..services.database import get_sessions_collection

class SessionManager:
    """Manages interview sessions using MongoDB storage."""
    
    def __init__(self):
        pass
    
    def _to_db_doc(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert session data to MongoDB document format.
        
        Args:
            data: Session data dictionary
            
        Returns:
            Dict[str, Any]: MongoDB document
        """
        doc = data.copy()
        if "_id" in doc:
            doc["_id"] = ObjectId(doc["_id"])
        return doc
    
    def _from_db_doc(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Convert MongoDB document to session data format.
        
        Args:
            doc: MongoDB document
            
        Returns:
            Optional[Dict[str, Any]]: Session data if document exists
        """
        if not doc:
            return None
        result = doc.copy()
        if "_id" in result:
            result["_id"] = str(result["_id"])
        return result
    
    async def create_session(self, candidate_id: str) -> str:
        """Create a new interview session.
        
        Args:
            candidate_id: Identifier for the interview candidate
            
        Returns:
            str: Unique session identifier
        """
        doc = {
            "candidate_id": candidate_id,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "current_phase": "pre_interview",
            "phases": {
                "pre_interview": {
                    "status": "pending",
                    "start_time": None,
                    "end_time": None,
                    "room_created": False,
                    "system_initialized": False,
                    "metrics_prepared": False
                },
                "introduction": {
                    "status": "pending",
                    "start_time": None,
                    "end_time": None,
                    "consent_obtained": False,
                    "background_verified": False
                },
                "technical": {
                    "status": "pending",
                    "start_time": None,
                    "end_time": None,
                    "system_design_complete": False,
                    "coding_challenge_complete": False,
                    "architecture_assessment_complete": False
                },
                "behavioral": {
                    "status": "pending",
                    "start_time": None,
                    "end_time": None,
                    "leadership_assessed": False,
                    "problem_solving_assessed": False,
                    "collaboration_assessed": False
                },
                "wrap_up": {
                    "status": "pending",
                    "start_time": None,
                    "end_time": None,
                    "questions_addressed": False,
                    "next_steps_provided": False
                }
            },
            "agents": {
                "consent_compliance": {
                    "status": "inactive",
                    "metrics": {},
                    "last_action": None
                },
                "technical_evaluation": {
                    "status": "inactive",
                    "metrics": {},
                    "last_action": None
                },
                "behavioral_assessment": {
                    "status": "inactive",
                    "metrics": {},
                    "last_action": None
                },
                "time_management": {
                    "status": "inactive",
                    "metrics": {},
                    "last_action": None
                },
                "orchestrator": {
                    "status": "inactive",
                    "metrics": {},
                    "last_action": None
                },
                "feedback_compilation": {
                    "status": "inactive",
                    "metrics": {},
                    "last_action": None
                },
                "question_management": {
                    "status": "inactive",
                    "metrics": {},
                    "last_action": None
                },
                "transition_coordinator": {
                    "status": "inactive",
                    "metrics": {},
                    "last_action": None
                },
                "emergency_handler": {
                    "status": "inactive",
                    "metrics": {},
                    "last_action": None
                },
                "metrics_collection": {
                    "status": "inactive",
                    "metrics": {},
                    "last_action": None
                }
            },
            "responses": {},
            "metrics": {
                "technical_score": 0.0,
                "behavioral_score": 0.0,
                "cultural_score": 0.0,
                "overall_score": 0.0,
                "response_quality": 0.0,
                "time_management": 0.0,
                "technical_depth": 0.0,
                "behavioral_indicators": 0.0
            },
            "eligibility_checks": {
                "work_authorization": False,
                "remote_work": False,
                "relocation": False,
                "travel": False
            },
            "exit_criteria": {
                "immediate_flags": [],
                "performance_threshold": None,
                "completion_status": "pending"
            }
        }
        collection = await get_sessions_collection()
        result = await collection.insert_one(doc)
        return str(result.inserted_id)
    
    async def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data by session ID.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Optional[Dict[str, Any]]: Session data if found, None otherwise
        """
        try:
            collection = await get_sessions_collection()
            doc = await collection.find_one({"_id": ObjectId(session_id)})
            return self._from_db_doc(doc)
        except:
            return None
    
    async def update_session_data(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Update session data for a given session ID.
        
        Args:
            session_id: Unique session identifier
            data: Dictionary containing data to update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            collection = await get_sessions_collection()
            result = await collection.update_one(
                {"_id": ObjectId(session_id)},
                {"$set": data}
            )
            return result.modified_count > 0
        except:
            return False
    
    async def start_phase(self, session_id: str, phase: str) -> bool:
        """Start a specific interview phase.
        
        Args:
            session_id: Unique session identifier
            phase: Phase to start
            
        Returns:
            bool: True if phase started successfully
        """
        try:
            now = datetime.now().isoformat()
            return await self.update_session_data(
                session_id,
                {
                    f"phases.{phase}.status": "active",
                    f"phases.{phase}.start_time": now,
                    "current_phase": phase
                }
            )
        except:
            return False

    async def end_phase(self, session_id: str, phase: str) -> bool:
        """End a specific interview phase.
        
        Args:
            session_id: Unique session identifier
            phase: Phase to end
            
        Returns:
            bool: True if phase ended successfully
        """
        try:
            now = datetime.now().isoformat()
            return await self.update_session_data(
                session_id,
                {
                    f"phases.{phase}.status": "completed",
                    f"phases.{phase}.end_time": now
                }
            )
        except:
            return False

    async def update_phase_status(
        self, session_id: str, phase: str, status_updates: Dict[str, bool]
    ) -> bool:
        """Update status flags for a specific phase.
        
        Args:
            session_id: Unique session identifier
            phase: Interview phase
            status_updates: Dictionary of status flags to update
            
        Returns:
            bool: True if status updated successfully
        """
        try:
            updates = {
                f"phases.{phase}.{key}": value
                for key, value in status_updates.items()
            }
            return await self.update_session_data(session_id, updates)
        except:
            return False

    async def update_exit_criteria(
        self, session_id: str, criteria_updates: Dict[str, Any]
    ) -> bool:
        """Update exit criteria for a session.
        
        Args:
            session_id: Unique session identifier
            criteria_updates: Dictionary containing exit criteria updates
            
        Returns:
            bool: True if criteria updated successfully
        """
        try:
            updates = {
                f"exit_criteria.{key}": value
                for key, value in criteria_updates.items()
            }
            return await self.update_session_data(session_id, updates)
        except:
            return False

    async def end_session(self, session_id: str, completion_status: str = "completed") -> bool:
        """Mark a session as completed.
        
        Args:
            session_id: Unique session identifier
            completion_status: Final status (completed/terminated/failed)
            
        Returns:
            bool: True if session ended successfully, False otherwise
        """
        try:
            now = datetime.now().isoformat()
            updates = {
                "end_time": now,
                "exit_criteria.completion_status": completion_status
            }
            
            # End current phase if any is active
            session_data = await self.get_session_data(session_id)
            if session_data and session_data.get("current_phase"):
                current_phase = session_data["current_phase"]
                if session_data["phases"][current_phase]["status"] == "active":
                    await self.end_phase(session_id, current_phase)
            
            return await self.update_session_data(session_id, updates)
        except:
            return False
    
    async def add_response(self, session_id: str, phase: str, response: str) -> bool:
        """Add a candidate response to a specific phase.
        
        Args:
            session_id: Unique session identifier
            phase: Interview phase (e.g., 'introduction', 'technical')
            response: Candidate's response
            
        Returns:
            bool: True if response added successfully, False otherwise
        """
        try:
            collection = await get_sessions_collection()
            result = await collection.update_one(
                {"_id": ObjectId(session_id)},
                {
                    "$push": {
                        f"responses.{phase}": response
                    }
                }
            )
            return result.modified_count > 0
        except:
            return False
    
    async def update_metrics(
        self, session_id: str, metrics: Dict[str, Any], agent: Optional[str] = None
    ) -> bool:
        """Update evaluation metrics for a session.
        
        Args:
            session_id: Unique session identifier
            metrics: Dictionary containing updated metrics
            agent: Optional agent name if metrics are agent-specific
            
        Returns:
            bool: True if metrics updated successfully, False otherwise
        """
        try:
            collection = await get_sessions_collection()
            
            if agent:
                # Update agent-specific metrics
                await collection.update_one(
                    {"_id": ObjectId(session_id)},
                    {"$set": {f"agents.{agent}.metrics": metrics}}
                )
                return True
            
            # Update session-level metrics
            metric_updates = {}
            
            # Core evaluation metrics
            core_metrics = {
                k: v for k, v in metrics.items()
                if k in ["technical_score", "behavioral_score", "cultural_score"]
            }
            if core_metrics:
                for k, v in core_metrics.items():
                    metric_updates[f"metrics.{k}"] = v
                
                # Calculate and update overall score
                weights = {
                    "technical_score": 0.5,
                    "behavioral_score": 0.3,
                    "cultural_score": 0.2
                }
                doc = await self.get_session_data(session_id)
                if doc:
                    overall_score = sum(
                        doc["metrics"].get(key, 0.0) * weight
                        for key, weight in weights.items()
                    )
                    metric_updates["metrics.overall_score"] = overall_score
            
            # Real-time assessment metrics
            realtime_metrics = {
                k: v for k, v in metrics.items()
                if k in [
                    "response_quality",
                    "time_management",
                    "technical_depth",
                    "behavioral_indicators"
                ]
            }
            for k, v in realtime_metrics.items():
                metric_updates[f"metrics.{k}"] = v
            
            if metric_updates:
                result = await collection.update_one(
                    {"_id": ObjectId(session_id)},
                    {"$set": metric_updates}
                )
                return result.modified_count > 0
            return True
            
        except Exception as e:
            print(f"Error updating metrics: {str(e)}")
            return False
    
    async def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active (non-ended) sessions.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of active sessions
        """
        collection = await get_sessions_collection()
        cursor = collection.find({"end_time": None})
        sessions = {}
        async for doc in cursor:
            converted_doc = self._from_db_doc(doc)
            if converted_doc:
                sessions[converted_doc["_id"]] = converted_doc
        return sessions
