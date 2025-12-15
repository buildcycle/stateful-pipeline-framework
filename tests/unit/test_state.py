"""Unit tests for State classes."""

import unittest
from datetime import datetime
from pipeline_engine.core.state import StepStatus, StepState, PipelineState


class TestStepStatus(unittest.TestCase):
    """Test cases for StepStatus enum."""
    
    def test_status_values(self):
        """Test all status values exist."""
        self.assertEqual(StepStatus.PENDING.value, "pending")
        self.assertEqual(StepStatus.RUNNING.value, "running")
        self.assertEqual(StepStatus.COMPLETED.value, "completed")
        self.assertEqual(StepStatus.FAILED.value, "failed")
        self.assertEqual(StepStatus.SKIPPED.value, "skipped")


class TestStepState(unittest.TestCase):
    """Test cases for StepState class."""
    
    def test_init_default(self):
        """Test step state initialization with defaults."""
        state = StepState(step_name="test_step")
        self.assertEqual(state.step_name, "test_step")
        self.assertEqual(state.status, StepStatus.PENDING)
        self.assertIsNone(state.input_data)
        self.assertIsNone(state.output_data)
        self.assertIsNone(state.error)
        self.assertEqual(state.attempts, 0)
    
    def test_to_dict(self):
        """Test converting step state to dictionary."""
        state = StepState(step_name="test_step")
        state.status = StepStatus.COMPLETED
        state.input_data = {"input": "data"}
        state.output_data = {"output": "result"}
        state.attempts = 2
        
        result = state.to_dict()
        self.assertEqual(result["step_name"], "test_step")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["input_data"], {"input": "data"})
        self.assertEqual(result["output_data"], {"output": "result"})
        self.assertEqual(result["attempts"], 2)


class TestPipelineState(unittest.TestCase):
    """Test cases for PipelineState class."""
    
    def test_init(self):
        """Test pipeline state initialization."""
        state = PipelineState(pipeline_id="test-123")
        self.assertEqual(state.pipeline_id, "test-123")
        self.assertEqual(state.status, StepStatus.PENDING)
        self.assertEqual(len(state.steps), 0)
        self.assertIsNone(state.started_at)
        self.assertIsNone(state.completed_at)
        self.assertIsNone(state.error)
    
    def test_add_step_state(self):
        """Test adding step state."""
        pipeline_state = PipelineState(pipeline_id="test-123")
        step_state = StepState(step_name="step1")
        pipeline_state.add_step_state(step_state)
        
        self.assertEqual(len(pipeline_state.steps), 1)
        self.assertEqual(pipeline_state.get_step_state("step1"), step_state)
    
    def test_get_step_state_existing(self):
        """Test getting existing step state."""
        pipeline_state = PipelineState(pipeline_id="test-123")
        step_state = StepState(step_name="step1")
        pipeline_state.add_step_state(step_state)
        
        result = pipeline_state.get_step_state("step1")
        self.assertEqual(result, step_state)
    
    def test_get_step_state_missing(self):
        """Test getting non-existent step state."""
        pipeline_state = PipelineState(pipeline_id="test-123")
        result = pipeline_state.get_step_state("missing")
        self.assertIsNone(result)
    
    def test_to_dict(self):
        """Test converting pipeline state to dictionary."""
        pipeline_state = PipelineState(pipeline_id="test-123")
        step_state = StepState(step_name="step1")
        step_state.status = StepStatus.COMPLETED
        pipeline_state.add_step_state(step_state)
        pipeline_state.status = StepStatus.RUNNING
        
        result = pipeline_state.to_dict()
        self.assertEqual(result["pipeline_id"], "test-123")
        self.assertEqual(result["status"], "running")
        self.assertEqual(len(result["steps"]), 1)
        self.assertIn("step1", result["steps"])


if __name__ == "__main__":
    unittest.main()

