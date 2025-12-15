"""State inspection utilities for pipelines and steps."""

from typing import Optional, Dict, Any
from .state import PipelineState, StepState, StepStatus


class PipelineInspector:
    """Utility class for inspecting pipeline and step states."""
    
    def __init__(self, pipeline_state: PipelineState):
        self.pipeline_state = pipeline_state
    
    def get_step_state(self, step_name: str) -> Optional[StepState]:
        """Get state for a specific step."""
        return self.pipeline_state.get_step_state(step_name)
    
    def get_step_input(self, step_name: str) -> Optional[Dict[str, Any]]:
        """Get input data for a specific step."""
        step_state = self.get_step_state(step_name)
        return step_state.input_data if step_state else None
    
    def get_step_output(self, step_name: str) -> Optional[Dict[str, Any]]:
        """Get output data for a specific step."""
        step_state = self.get_step_state(step_name)
        return step_state.output_data if step_state else None
    
    def get_step_status(self, step_name: str) -> Optional[StepStatus]:
        """Get status for a specific step."""
        step_state = self.get_step_state(step_name)
        return step_state.status if step_state else None
    
    def get_step_error(self, step_name: str) -> Optional[str]:
        """Get error message for a specific step."""
        step_state = self.get_step_state(step_name)
        return step_state.error if step_state else None
    
    def get_step_attempts(self, step_name: str) -> int:
        """Get number of attempts for a specific step."""
        step_state = self.get_step_state(step_name)
        return step_state.attempts if step_state else 0
    
    def is_step_completed(self, step_name: str) -> bool:
        """Check if a step has completed successfully."""
        return self.get_step_status(step_name) == StepStatus.COMPLETED
    
    def is_step_failed(self, step_name: str) -> bool:
        """Check if a step has failed."""
        return self.get_step_status(step_name) == StepStatus.FAILED
    
    def get_all_steps(self) -> Dict[str, StepState]:
        """Get all step states."""
        return self.pipeline_state.steps.copy()
    
    def get_pipeline_status(self) -> StepStatus:
        """Get overall pipeline status."""
        return self.pipeline_state.status
    
    def get_pipeline_error(self) -> Optional[str]:
        """Get pipeline-level error message."""
        return self.pipeline_state.error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert inspector state to dictionary."""
        return self.pipeline_state.to_dict()

