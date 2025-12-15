"""State tracking for pipeline and steps."""

from enum import Enum
from typing import Any, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime


class StepStatus(Enum):
    """Status of a step execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StepState:
    """State information for a single step."""
    step_name: str
    status: StepStatus = StepStatus.PENDING
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    attempts: int = 0
    
    def to_dict(self) -> dict:
        """Convert step state to dictionary."""
        return {
            "step_name": self.step_name,
            "status": self.status.value,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "attempts": self.attempts,
        }


@dataclass
class PipelineState:
    """State information for the entire pipeline."""
    pipeline_id: str
    status: StepStatus = StepStatus.PENDING
    steps: Dict[str, StepState] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    def get_step_state(self, step_name: str) -> Optional[StepState]:
        """Get state for a specific step."""
        return self.steps.get(step_name)
    
    def add_step_state(self, step_state: StepState):
        """Add or update step state."""
        self.steps[step_state.step_name] = step_state
    
    def to_dict(self) -> dict:
        """Convert pipeline state to dictionary."""
        return {
            "pipeline_id": self.pipeline_id,
            "status": self.status.value,
            "steps": {name: state.to_dict() for name, state in self.steps.items()},
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
        }

