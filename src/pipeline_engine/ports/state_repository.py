"""Interface for state persistence."""

from abc import ABC, abstractmethod
from ..core.state import PipelineState


class StateRepository(ABC):
    """Abstract interface for persisting pipeline state."""
    
    @abstractmethod
    def save(self, pipeline_id: str, state: PipelineState):
        """
        Save pipeline state.
        
        Args:
            pipeline_id: Unique identifier for the pipeline
            state: Pipeline state to persist
        """
        pass
    
    @abstractmethod
    def load(self, pipeline_id: str) -> PipelineState:
        """
        Load pipeline state.
        
        Args:
            pipeline_id: Unique identifier for the pipeline
            
        Returns:
            PipelineState object
            
        Raises:
            KeyError: If pipeline_id not found
        """
        pass
    
    @abstractmethod
    def exists(self, pipeline_id: str) -> bool:
        """
        Check if a pipeline state exists.
        
        Args:
            pipeline_id: Unique identifier for the pipeline
            
        Returns:
            True if state exists, False otherwise
        """
        pass

