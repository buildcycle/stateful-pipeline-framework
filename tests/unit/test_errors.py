"""Unit tests for custom exceptions."""

import unittest
from pipeline_engine.core.errors import (
    PipelineError,
    StepError,
    PipelineExecutionError,
    RetryExhaustedError
)


class TestPipelineError(unittest.TestCase):
    """Test cases for PipelineError."""
    
    def test_inheritance(self):
        """Test PipelineError inherits from Exception."""
        error = PipelineError("test message")
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "test message")


class TestStepError(unittest.TestCase):
    """Test cases for StepError."""
    
    def test_step_error_creation(self):
        """Test StepError creation with step name and message."""
        error = StepError("test_step", "Something went wrong")
        self.assertEqual(error.step_name, "test_step")
        self.assertIn("test_step", str(error))
        self.assertIn("Something went wrong", str(error))
    
    def test_step_error_with_original(self):
        """Test StepError with original exception."""
        original = ValueError("Original error")
        error = StepError("test_step", "Wrapped error", original)
        self.assertEqual(error.original_error, original)


class TestPipelineExecutionError(unittest.TestCase):
    """Test cases for PipelineExecutionError."""
    
    def test_pipeline_execution_error(self):
        """Test PipelineExecutionError creation."""
        error = PipelineExecutionError("Pipeline failed")
        self.assertIsInstance(error, PipelineError)
        self.assertEqual(str(error), "Pipeline failed")


class TestRetryExhaustedError(unittest.TestCase):
    """Test cases for RetryExhaustedError."""
    
    def test_retry_exhausted_error(self):
        """Test RetryExhaustedError creation."""
        error = RetryExhaustedError("test_step", 3)
        self.assertEqual(error.step_name, "test_step")
        self.assertEqual(error.attempts, 3)
        self.assertIn("test_step", str(error))
        self.assertIn("3", str(error))


if __name__ == "__main__":
    unittest.main()

