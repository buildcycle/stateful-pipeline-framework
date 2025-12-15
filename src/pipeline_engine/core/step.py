"""Step interface and base implementation."""

from abc import ABC, abstractmethod
from typing import Any, Dict
from .context import Context


class Step(ABC):
    """Abstract base class for pipeline steps."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def execute(self, context: Context) -> Dict[str, Any]:
        """
        Execute the step logic.
        
        Args:
            context: Shared context object
            
        Returns:
            Dictionary of output data to be merged into context
            
        Raises:
            Exception: Any exception will be caught and wrapped in StepError
        """
        pass
    
    def __repr__(self):
        return f"<Step: {self.name}>"

