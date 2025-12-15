"""Unit tests for MemoryStateRepository."""

import unittest
from pipeline_engine.adapters.persistence.memory import MemoryStateRepository
from pipeline_engine.core.state import PipelineState, StepStatus


class TestMemoryStateRepository(unittest.TestCase):
    """Test cases for MemoryStateRepository."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.repository = MemoryStateRepository()
    
    def test_save_and_load(self):
        """Test saving and loading pipeline state."""
        state = PipelineState(pipeline_id="test-123")
        state.status = StepStatus.COMPLETED
        
        self.repository.save("test-123", state)
        loaded = self.repository.load("test-123")
        
        self.assertEqual(loaded.pipeline_id, "test-123")
        self.assertEqual(loaded.status, StepStatus.COMPLETED)
    
    def test_load_nonexistent(self):
        """Test loading non-existent state raises KeyError."""
        with self.assertRaises(KeyError):
            self.repository.load("missing")
    
    def test_exists_true(self):
        """Test exists returns True for saved state."""
        state = PipelineState(pipeline_id="test-123")
        self.repository.save("test-123", state)
        
        self.assertTrue(self.repository.exists("test-123"))
    
    def test_exists_false(self):
        """Test exists returns False for non-existent state."""
        self.assertFalse(self.repository.exists("missing"))
    
    def test_clear(self):
        """Test clearing all stored states."""
        state1 = PipelineState(pipeline_id="test-1")
        state2 = PipelineState(pipeline_id="test-2")
        
        self.repository.save("test-1", state1)
        self.repository.save("test-2", state2)
        
        self.assertTrue(self.repository.exists("test-1"))
        self.assertTrue(self.repository.exists("test-2"))
        
        self.repository.clear()
        
        self.assertFalse(self.repository.exists("test-1"))
        self.assertFalse(self.repository.exists("test-2"))
    
    def test_save_overwrites(self):
        """Test saving overwrites existing state."""
        state1 = PipelineState(pipeline_id="test-123")
        state1.status = StepStatus.PENDING
        
        state2 = PipelineState(pipeline_id="test-123")
        state2.status = StepStatus.COMPLETED
        
        self.repository.save("test-123", state1)
        self.repository.save("test-123", state2)
        
        loaded = self.repository.load("test-123")
        self.assertEqual(loaded.status, StepStatus.COMPLETED)


if __name__ == "__main__":
    unittest.main()

