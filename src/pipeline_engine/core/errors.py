"""Custom exceptions for the pipeline framework."""


class PipelineError(Exception):
    """Base exception for all pipeline-related errors."""
    pass


class StepError(PipelineError):
    """Exception raised when a step fails during execution."""
    
    def __init__(self, step_name: str, message: str, original_error: Exception = None):
        self.step_name = step_name
        self.original_error = original_error
        super().__init__(f"Step '{step_name}' failed: {message}")


class PipelineExecutionError(PipelineError):
    """Exception raised when pipeline execution fails."""
    pass


class RetryExhaustedError(PipelineError):
    """Exception raised when step retry attempts are exhausted."""
    
    def __init__(self, step_name: str, attempts: int):
        self.step_name = step_name
        self.attempts = attempts
        super().__init__(f"Step '{step_name}' failed after {attempts} attempts")

