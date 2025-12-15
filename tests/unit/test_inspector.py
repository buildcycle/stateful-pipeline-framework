"""Unit tests for PipelineInspector."""

import unittest
from pipeline_engine.core.inspector import PipelineInspector
from pipeline_engine.core.state import PipelineState, StepState, StepStatus


class TestPipelineInspector(unittest.TestCase):
    """Test cases for PipelineInspector."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.pipeline_state = PipelineState(pipeline_id="test-123")
        self.inspector = PipelineInspector(self.pipeline_state)
    
    def test_get_step_state_existing(self):
        """Test getting existing step state."""
        step_state = StepState(step_name="step1")
        self.pipeline_state.add_step_state(step_state)
        
        result = self.inspector.get_step_state("step1")
        self.assertEqual(result, step_state)
    
    def test_get_step_state_missing(self):
        """Test getting non-existent step state."""
        result = self.inspector.get_step_state("missing")
        self.assertIsNone(result)
    
    def test_get_step_input(self):
        """Test getting step input data."""
        step_state = StepState(step_name="step1")
        step_state.input_data = {"input": "data"}
        self.pipeline_state.add_step_state(step_state)
        
        result = self.inspector.get_step_input("step1")
        self.assertEqual(result, {"input": "data"})
    
    def test_get_step_output(self):
        """Test getting step output data."""
        step_state = StepState(step_name="step1")
        step_state.output_data = {"output": "result"}
        self.pipeline_state.add_step_state(step_state)
        
        result = self.inspector.get_step_output("step1")
        self.assertEqual(result, {"output": "result"})
    
    def test_get_step_status(self):
        """Test getting step status."""
        step_state = StepState(step_name="step1")
        step_state.status = StepStatus.COMPLETED
        self.pipeline_state.add_step_state(step_state)
        
        result = self.inspector.get_step_status("step1")
        self.assertEqual(result, StepStatus.COMPLETED)
    
    def test_get_step_error(self):
        """Test getting step error."""
        step_state = StepState(step_name="step1")
        step_state.error = "Something went wrong"
        self.pipeline_state.add_step_state(step_state)
        
        result = self.inspector.get_step_error("step1")
        self.assertEqual(result, "Something went wrong")
    
    def test_get_step_attempts(self):
        """Test getting step attempts."""
        step_state = StepState(step_name="step1")
        step_state.attempts = 3
        self.pipeline_state.add_step_state(step_state)
        
        result = self.inspector.get_step_attempts("step1")
        self.assertEqual(result, 3)
    
    def test_get_step_attempts_missing(self):
        """Test getting attempts for missing step."""
        result = self.inspector.get_step_attempts("missing")
        self.assertEqual(result, 0)
    
    def test_is_step_completed(self):
        """Test checking if step is completed."""
        step_state = StepState(step_name="step1")
        step_state.status = StepStatus.COMPLETED
        self.pipeline_state.add_step_state(step_state)
        
        self.assertTrue(self.inspector.is_step_completed("step1"))
        self.assertFalse(self.inspector.is_step_completed("step2"))
    
    def test_is_step_failed(self):
        """Test checking if step failed."""
        step_state = StepState(step_name="step1")
        step_state.status = StepStatus.FAILED
        self.pipeline_state.add_step_state(step_state)
        
        self.assertTrue(self.inspector.is_step_failed("step1"))
        self.assertFalse(self.inspector.is_step_failed("step2"))
    
    def test_get_all_steps(self):
        """Test getting all step states."""
        step1 = StepState(step_name="step1")
        step2 = StepState(step_name="step2")
        self.pipeline_state.add_step_state(step1)
        self.pipeline_state.add_step_state(step2)
        
        result = self.inspector.get_all_steps()
        self.assertEqual(len(result), 2)
        self.assertIn("step1", result)
        self.assertIn("step2", result)
    
    def test_get_pipeline_status(self):
        """Test getting pipeline status."""
        self.pipeline_state.status = StepStatus.RUNNING
        result = self.inspector.get_pipeline_status()
        self.assertEqual(result, StepStatus.RUNNING)
    
    def test_get_pipeline_error(self):
        """Test getting pipeline error."""
        self.pipeline_state.error = "Pipeline error"
        result = self.inspector.get_pipeline_error()
        self.assertEqual(result, "Pipeline error")
    
    def test_to_dict(self):
        """Test converting inspector to dictionary."""
        step_state = StepState(step_name="step1")
        self.pipeline_state.add_step_state(step_state)
        
        result = self.inspector.to_dict()
        self.assertEqual(result["pipeline_id"], "test-123")
        self.assertIn("step1", result["steps"])


if __name__ == "__main__":
    unittest.main()

