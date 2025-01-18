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
            "current_phase": "introduction",
            "responses": {},
            "metrics": {
                "technical_score": 0.0,
                "behavioral_score": 0.0,
                "cultural_score": 0.0,
                "overall_score": 0.0
            },
            "phase_timings": {},
            "eligibility_checks": {
                "work_authorization": False,
                "remote_work": False,
                "relocation": False,
                "travel": False
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
    
    async def end_session(self, session_id: str) -> bool:
        """Mark a session as completed.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            bool: True if session ended successfully, False otherwise
        """
        try:
            collection = await get_sessions_collection()
            result = await collection.update_one(
                {"_id": ObjectId(session_id)},
                {"$set": {"end_time": datetime.now().isoformat()}}
            )
            return result.modified_count > 0
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
    
    async def update_metrics(self, session_id: str, metrics: Dict[str, float]) -> bool:
        """Update evaluation metrics for a session.
        
        Args:
            session_id: Unique session identifier
            metrics: Dictionary containing updated metrics
            
        Returns:
            bool: True if metrics updated successfully, False otherwise
        """
        try:
            # First update the individual metrics
            collection = await get_sessions_collection()
            await collection.update_one(
                {"_id": ObjectId(session_id)},
                {"$set": {f"metrics.{k}": v for k, v in metrics.items()}}
            )
            
            # Calculate and update overall score
            weights = {
                "technical_score": 0.5,
                "behavioral_score": 0.3,
                "cultural_score": 0.2
            }
            
            # Get current metrics
            doc = await self.get_session_data(session_id)
            if not doc:
                return False
                
            overall_score = sum(
                doc["metrics"].get(key, 0.0) * weight
                for key, weight in weights.items()
            )
            
            # Update overall score
            collection = await get_sessions_collection()
            result = await collection.update_one(
                {"_id": ObjectId(session_id)},
                {"$set": {"metrics.overall_score": overall_score}}
            )
            return result.modified_count > 0
        except:
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
