"""Main pipeline orchestrator."""

import uuid
from datetime import datetime
from typing import List, Optional
from .context import Context
from .step import Step
from .state import PipelineState, StepState, StepStatus
from .errors import StepError, PipelineExecutionError
from .retry import RetryConfig
from .inspector import PipelineInspector
from ..ports.state_repository import StateRepository


class Pipeline:
    """Orchestrates sequential execution of pipeline steps."""
    
    def __init__(
        self,
        steps: List[Step],
        state_repository: Optional[StateRepository] = None,
        pipeline_id: Optional[str] = None
    ):
        if not steps:
            raise ValueError("Pipeline must have at least one step")
        
        self.steps = steps
        self.state_repository = state_repository
        self.pipeline_id = pipeline_id or str(uuid.uuid4())
        self._state = PipelineState(pipeline_id=self.pipeline_id)
        self._context = Context()
    
    def run(self, initial_context: Optional[dict] = None) -> PipelineInspector:
        """
        Execute the pipeline sequentially.
        
        Args:
            initial_context: Optional initial context data
            
        Returns:
            PipelineInspector for inspecting execution state
        """
        self._context = Context(initial_context or {})
        self._state.status = StepStatus.RUNNING
        self._state.started_at = datetime.now()
        
        self._save_state()
        
        try:
            for step in self.steps:
                self._execute_step(step)
            
            self._state.status = StepStatus.COMPLETED
            self._state.completed_at = datetime.now()
        except Exception as e:
            self._state.status = StepStatus.FAILED
            self._state.error = str(e)
            self._state.completed_at = datetime.now()
            self._save_state()
            raise PipelineExecutionError(f"Pipeline execution failed: {e}") from e
        
        self._save_state()
        return PipelineInspector(self._state)
    
    def _execute_step(self, step: Step, retry_config: Optional[RetryConfig] = None):
        """Execute a single step with error handling and state tracking."""
        step_state = StepState(step_name=step.name)
        step_state.status = StepStatus.RUNNING
        step_state.started_at = datetime.now()
        step_state.input_data = self._context.to_dict()
        
        self._state.add_step_state(step_state)
        self._save_state()
        
        try:
            def execute():
                return step.execute(self._context)
            
            if retry_config:
                from .retry import retry_step
                output, attempts = retry_step(step.name, execute, retry_config)
                step_state.attempts = attempts
            else:
                output = execute()
                step_state.attempts = 1
            
            if output:
                self._context.update(output)
            
            step_state.status = StepStatus.COMPLETED
            step_state.output_data = output
            step_state.completed_at = datetime.now()
            
        except Exception as e:
            step_state.status = StepStatus.FAILED
            step_state.error = str(e)
            step_state.completed_at = datetime.now()
            self._state.add_step_state(step_state)
            self._save_state()
            
            raise StepError(step.name, str(e), e) from e
        
        self._state.add_step_state(step_state)
        self._save_state()
    
    def retry_step(self, step_name: str, retry_config: Optional[RetryConfig] = None):
        """
        Retry a specific step that has failed.
        
        Args:
            step_name: Name of the step to retry
            retry_config: Optional retry configuration
        """
        step = next((s for s in self.steps if s.name == step_name), None)
        if not step:
            raise ValueError(f"Step '{step_name}' not found in pipeline")
        
        if retry_config is None:
            retry_config = RetryConfig(max_attempts=3)
        
        self._execute_step(step, retry_config)
    
    def get_inspector(self) -> PipelineInspector:
        """Get inspector for current pipeline state."""
        return PipelineInspector(self._state)
    
    def get_context(self) -> Context:
        """Get the current pipeline context."""
        return self._context
    
    def _save_state(self):
        """Save pipeline state to repository if available."""
        if self.state_repository:
            self.state_repository.save(self.pipeline_id, self._state)

