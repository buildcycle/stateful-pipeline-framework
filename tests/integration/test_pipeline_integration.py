"""Integration tests for pipeline framework."""

import unittest
import sys
import os

# Add src to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from pipeline_engine.core.pipeline import Pipeline
from pipeline_engine.core.step import Step
from pipeline_engine.core.context import Context
from pipeline_engine.core.state import StepStatus
from pipeline_engine.core.errors import PipelineExecutionError
from pipeline_engine.core.retry import RetryConfig
from pipeline_engine.adapters.persistence.memory import MemoryStateRepository


class AddStep(Step):
    """Step that adds a number to context."""
    
    def __init__(self, value: int):
        super().__init__(f"add_{value}")
        self.value = value
    
    def execute(self, context: Context):
        current = context.get("total", 0)
        return {"total": current + self.value}


class MultiplyStep(Step):
    """Step that multiplies context value."""
    
    def __init__(self, factor: int):
        super().__init__(f"multiply_{factor}")
        self.factor = factor
    
    def execute(self, context: Context):
        current = context.get("total", 1)
        return {"total": current * self.factor}


class TestPipelineIntegration(unittest.TestCase):
    """Integration tests for pipeline framework."""
    
    def test_full_pipeline_execution(self):
        """Test complete pipeline execution with multiple steps."""
        steps = [
            AddStep(5),
            AddStep(10),
            MultiplyStep(2)
        ]
        repository = MemoryStateRepository()
        pipeline = Pipeline(steps, state_repository=repository)
        
        inspector = pipeline.run(initial_context={"total": 0})
        
        # Verify final result: (0 + 5 + 10) * 2 = 30
        self.assertEqual(pipeline.get_context().get("total"), 30)
        self.assertEqual(inspector.get_pipeline_status(), StepStatus.COMPLETED)
        
        # Verify all steps completed
        for step in steps:
            self.assertTrue(inspector.is_step_completed(step.name))
    
    def test_pipeline_with_state_persistence(self):
        """Test pipeline state persistence and retrieval."""
        steps = [AddStep(42)]
        repository = MemoryStateRepository()
        pipeline = Pipeline(steps, state_repository=repository)
        
        inspector = pipeline.run()
        pipeline_id = pipeline.pipeline_id
        
        # Verify state was saved
        self.assertTrue(repository.exists(pipeline_id))
        
        # Load and verify state
        saved_state = repository.load(pipeline_id)
        self.assertEqual(saved_state.status, StepStatus.COMPLETED)
        self.assertEqual(len(saved_state.steps), 1)
    
    def test_pipeline_with_retry(self):
        """Test pipeline with retry mechanism."""
        class FlakyStep(Step):
            """Step that fails first two times."""
            
            def __init__(self):
                super().__init__("flaky_step")
                self.call_count = 0
            
            def execute(self, context: Context):
                self.call_count += 1
                if self.call_count < 3:
                    raise ValueError("Temporary failure")
                return {"success": True}
        
        step = FlakyStep()
        pipeline = Pipeline([step])
        
        # First run should fail (1 attempt)
        with self.assertRaises(PipelineExecutionError):
            pipeline.run()
        
        # Retry with retry config (will retry until success, max 5 attempts)
        retry_config = RetryConfig(max_attempts=5, delay=0.01)
        pipeline.retry_step("flaky_step", retry_config)
        
        inspector = pipeline.get_inspector()
        step_state = inspector.get_step_state("flaky_step")
        self.assertEqual(step_state.status, StepStatus.COMPLETED)
        # Retry mechanism will make additional attempts until success
        # Total attempts = 1 (initial) + retry attempts (at least 2 more = 3 total)
        self.assertGreaterEqual(step_state.attempts, 2)
        # Verify step was called 3 times total (1 initial + 2 retries)
        self.assertEqual(step.call_count, 3)
    
    def test_pipeline_error_handling(self):
        """Test pipeline error handling and state tracking."""
        class FailingStep(Step):
            """Step that always fails."""
            
            def __init__(self):
                super().__init__("failing_step")
            
            def execute(self, context: Context):
                raise RuntimeError("Step failed")
        
        step = FailingStep()
        pipeline = Pipeline([step])
        
        with self.assertRaises(PipelineExecutionError):
            pipeline.run()
        
        inspector = pipeline.get_inspector()
        self.assertEqual(inspector.get_pipeline_status(), StepStatus.FAILED)
        self.assertIsNotNone(inspector.get_pipeline_error())
        
        step_state = inspector.get_step_state("failing_step")
        self.assertEqual(step_state.status, StepStatus.FAILED)
        self.assertIsNotNone(step_state.error)
    
    def test_pipeline_context_propagation(self):
        """Test context propagation through multiple steps."""
        class SetValueStep(Step):
            """Step that sets a value."""
            
            def __init__(self, key: str, value):
                super().__init__(f"set_{key}")
                self.key = key
                self.value = value
            
            def execute(self, context: Context):
                return {self.key: self.value}
        
        steps = [
            SetValueStep("a", 1),
            SetValueStep("b", 2),
            SetValueStep("c", 3)
        ]
        pipeline = Pipeline(steps)
        
        inspector = pipeline.run()
        
        context = pipeline.get_context()
        self.assertEqual(context.get("a"), 1)
        self.assertEqual(context.get("b"), 2)
        self.assertEqual(context.get("c"), 3)
        
        # Verify each step can see previous step outputs
        step2_input = inspector.get_step_input("set_b")
        self.assertIn("a", step2_input)
        self.assertEqual(step2_input["a"], 1)


if __name__ == "__main__":
    unittest.main()

