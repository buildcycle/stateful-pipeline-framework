"""Unit tests for Pipeline class."""

import unittest
from unittest.mock import Mock, MagicMock
from pipeline_engine.core.pipeline import Pipeline
from pipeline_engine.core.step import Step
from pipeline_engine.core.context import Context
from pipeline_engine.core.state import StepStatus
from pipeline_engine.core.errors import PipelineExecutionError, StepError
from pipeline_engine.adapters.persistence.memory import MemoryStateRepository


class MockStep(Step):
    """Mock step for testing."""
    
    def __init__(self, name: str, output: dict = None, should_fail: bool = False):
        super().__init__(name)
        self.output = output or {}
        self.should_fail = should_fail
        self.executed = False
    
    def execute(self, context: Context):
        """Execute mock step."""
        self.executed = True
        if self.should_fail:
            raise ValueError(f"Step {self.name} failed")
        return self.output


class TestPipeline(unittest.TestCase):
    """Test cases for Pipeline class."""
    
    def test_init_with_steps(self):
        """Test pipeline initialization with steps."""
        step = MockStep("step1")
        pipeline = Pipeline([step])
        
        self.assertEqual(len(pipeline.steps), 1)
        self.assertEqual(pipeline.steps[0], step)
        self.assertIsNotNone(pipeline.pipeline_id)
    
    def test_init_with_custom_id(self):
        """Test pipeline initialization with custom ID."""
        step = MockStep("step1")
        pipeline = Pipeline([step], pipeline_id="custom-id")
        
        self.assertEqual(pipeline.pipeline_id, "custom-id")
    
    def test_init_empty_steps_raises_error(self):
        """Test pipeline initialization with no steps raises error."""
        with self.assertRaises(ValueError) as context:
            Pipeline([])
        
        self.assertIn("at least one step", str(context.exception))
    
    def test_run_single_step(self):
        """Test running pipeline with single step."""
        step = MockStep("step1", {"result": "success"})
        pipeline = Pipeline([step])
        
        inspector = pipeline.run()
        
        self.assertTrue(step.executed)
        self.assertEqual(pipeline.get_context().get("result"), "success")
        self.assertEqual(inspector.get_pipeline_status(), StepStatus.COMPLETED)
    
    def test_run_multiple_steps(self):
        """Test running pipeline with multiple steps."""
        step1 = MockStep("step1", {"data1": "value1"})
        step2 = MockStep("step2", {"data2": "value2"})
        pipeline = Pipeline([step1, step2])
        
        inspector = pipeline.run()
        
        self.assertTrue(step1.executed)
        self.assertTrue(step2.executed)
        context = pipeline.get_context()
        self.assertEqual(context.get("data1"), "value1")
        self.assertEqual(context.get("data2"), "value2")
        self.assertEqual(inspector.get_pipeline_status(), StepStatus.COMPLETED)
    
    def test_run_with_initial_context(self):
        """Test running pipeline with initial context."""
        step = MockStep("step1", {"new": "data"})
        pipeline = Pipeline([step])
        
        initial = {"existing": "value"}
        inspector = pipeline.run(initial_context=initial)
        
        context = pipeline.get_context()
        self.assertEqual(context.get("existing"), "value")
        self.assertEqual(context.get("new"), "data")
    
    def test_run_step_failure_propagates(self):
        """Test that step failure propagates and stops pipeline."""
        step1 = MockStep("step1", {"data": "value"})
        step2 = MockStep("step2", should_fail=True)
        step3 = MockStep("step3", {"data3": "value3"})
        pipeline = Pipeline([step1, step2, step3])
        
        with self.assertRaises(PipelineExecutionError):
            pipeline.run()
        
        self.assertTrue(step1.executed)
        self.assertTrue(step2.executed)
        self.assertFalse(step3.executed)
    
    def test_run_tracks_step_states(self):
        """Test that pipeline tracks step states during execution."""
        step1 = MockStep("step1", {"result": "ok"})
        step2 = MockStep("step2", {"result2": "ok2"})
        pipeline = Pipeline([step1, step2])
        
        inspector = pipeline.run()
        
        step1_state = inspector.get_step_state("step1")
        step2_state = inspector.get_step_state("step2")
        
        self.assertIsNotNone(step1_state)
        self.assertIsNotNone(step2_state)
        self.assertEqual(step1_state.status, StepStatus.COMPLETED)
        self.assertEqual(step2_state.status, StepStatus.COMPLETED)
        self.assertEqual(step1_state.output_data, {"result": "ok"})
    
    def test_run_with_state_repository(self):
        """Test that pipeline saves state to repository."""
        repository = MemoryStateRepository()
        step = MockStep("step1", {"result": "ok"})
        pipeline = Pipeline([step], state_repository=repository)
        
        pipeline.run()
        
        self.assertTrue(repository.exists(pipeline.pipeline_id))
        saved_state = repository.load(pipeline.pipeline_id)
        self.assertEqual(saved_state.status, StepStatus.COMPLETED)
    
    def test_retry_step_success(self):
        """Test retrying a step successfully."""
        step = MockStep("step1", {"result": "ok"})
        pipeline = Pipeline([step])
        
        # First run fails
        step.should_fail = True
        with self.assertRaises(PipelineExecutionError):
            pipeline.run()
        
        # Retry with fixed step
        step.should_fail = False
        pipeline.retry_step("step1")
        
        inspector = pipeline.get_inspector()
        step_state = inspector.get_step_state("step1")
        self.assertEqual(step_state.status, StepStatus.COMPLETED)
    
    def test_retry_step_not_found(self):
        """Test retrying non-existent step raises error."""
        step = MockStep("step1")
        pipeline = Pipeline([step])
        
        with self.assertRaises(ValueError) as context:
            pipeline.retry_step("nonexistent")
        
        self.assertIn("not found", str(context.exception))
    
    def test_get_inspector(self):
        """Test getting pipeline inspector."""
        step = MockStep("step1")
        pipeline = Pipeline([step])
        
        inspector = pipeline.get_inspector()
        self.assertIsNotNone(inspector)
        self.assertEqual(inspector.get_pipeline_status(), StepStatus.PENDING)
    
    def test_get_context(self):
        """Test getting pipeline context."""
        step = MockStep("step1", {"data": "value"})
        pipeline = Pipeline([step])
        pipeline.run()
        
        context = pipeline.get_context()
        self.assertIsInstance(context, Context)
        self.assertEqual(context.get("data"), "value")


if __name__ == "__main__":
    unittest.main()

