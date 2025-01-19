"""Pipeline implementation for the interview system."""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import asyncio
from ..core.session_manager import SessionManager

class PipelineStage(ABC):
    @abstractmethod
    async def process(self, data: Any, context: Dict[str, Any]) -> Any:
        pass

class Pipeline:
    def __init__(self, stages: List[PipelineStage]):
        self.stages = stages
        self.context = {}

    async def process(self, input_data: Any) -> Any:
        result = input_data
        for stage in self.stages:
            result = await stage.process(result, self.context)
        return result

class InterviewPipeline(Pipeline):
    def __init__(self, interview_config: Dict[str, Any]):
        self.config = interview_config
        self.session_manager = SessionManager()
        from ..services.transport import TransportInput, TransportOutput
        from ..services.speech import STTService, TTSService
        from ..services.llm import LLMService
        from ..models.interview import InterviewContext
        
        super().__init__([
            TransportInput(),                # Voice/text input handling
            STTService(),                    # Speech-to-text conversion
            InterviewContext.user(),         # User context management
            LLMService(),                    # Interview logic processing
            TTSService(),                    # Text-to-speech conversion
            TransportOutput(),               # Response delivery
            InterviewContext.assistant(),    # Interview state tracking
        ])
        
    async def create_interview_session(self, candidate_id: str) -> str:
        """Create a new interview session.
        
        Args:
            candidate_id: Identifier for the interview candidate
            
        Returns:
            str: Unique session identifier
        """
        session_id = await self.session_manager.create_session(candidate_id)
        # Start with introduction phase
        await self.session_manager.update_session_data(
            session_id,
            {"current_phase": "introduction"}
        )
        return session_id
    
    async def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get data for an interview session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Optional[Dict[str, Any]]: Session data if found, None otherwise
        """
        return await self.session_manager.get_session_data(session_id)
    
    async def end_interview_session(self, session_id: str) -> bool:
        """End an interview session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            bool: True if session ended successfully, False otherwise
        """
        return await self.session_manager.end_session(session_id)
