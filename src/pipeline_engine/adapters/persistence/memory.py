"""In-memory implementation of state repository."""

from typing import Dict
from ...core.state import PipelineState
from ...ports.state_repository import StateRepository


class MemoryStateRepository(StateRepository):
    """In-memory state repository implementation."""
    
    def __init__(self):
        self._storage: Dict[str, PipelineState] = {}
    
    def save(self, pipeline_id: str, state: PipelineState):
        """Save pipeline state to memory."""
        self._storage[pipeline_id] = state
    
    def load(self, pipeline_id: str) -> PipelineState:
        """Load pipeline state from memory."""
        if pipeline_id not in self._storage:
            raise KeyError(f"Pipeline state not found: {pipeline_id}")
        return self._storage[pipeline_id]
    
    def exists(self, pipeline_id: str) -> bool:
        """Check if pipeline state exists in memory."""
        return pipeline_id in self._storage
    
    def clear(self):
        """Clear all stored states (useful for testing)."""
        self._storage.clear()

