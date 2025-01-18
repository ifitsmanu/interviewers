"""Interview context and state management."""

from typing import Dict, Any, Optional, cast
from dataclasses import dataclass, field
from datetime import datetime
from ..core.pipeline import Pipeline
from ..core.session_manager import SessionManager
from ..core.pipeline import InterviewPipeline

@dataclass
class InterviewContext:
    candidate_id: str
    start_time: datetime = field(default_factory=datetime.now)
    current_phase: str = "introduction"
    responses: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    
    @classmethod
    def user(cls) -> 'InterviewContextManager':
        return InterviewContextManager(context_type="user")
    
    @classmethod
    def assistant(cls) -> 'InterviewContextManager':
        return InterviewContextManager(context_type="assistant")

class InterviewContextManager:
    def __init__(self, context_type: str, session_id: str = ""):
        self.context_type = context_type
        self.session_id = session_id
        self.context: Optional[InterviewContext] = None
        self._pipeline: Optional[InterviewPipeline] = None

    async def process(self, data: Any, context: Dict[str, Any]) -> Any:
        if '_pipeline' in context:
            self._pipeline = cast(InterviewPipeline, context['_pipeline'])
        
        if self.context is None:
            candidate_id = context.get('candidate_id', 'unknown')
            self.context = InterviewContext(candidate_id=candidate_id)
            if not self.session_id and self._pipeline:
                self.session_id = await self._pipeline.create_interview_session(candidate_id)
        
        if self.context_type == "user":
            return await self._process_user_context(data, context)
        else:
            return await self._process_assistant_context(data, context)

    async def _process_user_context(self, data: Any, context: Dict[str, Any]) -> Any:
        if self.context and self.session_id and self._pipeline:
            # Update session with user response
            phase = self.context.current_phase
            if isinstance(data, str):
                await self._pipeline.session_manager.add_response(
                    self.session_id, phase, data
                )
            # Update session metrics if available
            if 'metrics' in context:
                await self._pipeline.session_manager.update_metrics(
                    self.session_id, context['metrics']
                )
        return data

    async def _process_assistant_context(self, data: Any, context: Dict[str, Any]) -> Any:
        if self.context and self.session_id and self._pipeline:
            # Update session with phase transition if needed
            if 'next_phase' in context:
                await self._pipeline.session_manager.update_session_data(
                    self.session_id,
                    {'current_phase': context['next_phase']}
                )
                self.context.current_phase = context['next_phase']
            # Update session with assistant response if available
            if isinstance(data, dict) and 'response' in data:
                await self._pipeline.session_manager.update_session_data(
                    self.session_id,
                    {'assistant_response': data['response']}
                )
        return data
