"""Unit tests for Context class."""

import unittest
from pipeline_engine.core.context import Context


class TestContext(unittest.TestCase):
    """Test cases for Context class."""
    
    def test_init_empty(self):
        """Test context initialization with no data."""
        context = Context()
        self.assertEqual(context.to_dict(), {})
    
    def test_init_with_data(self):
        """Test context initialization with initial data."""
        data = {"key1": "value1", "key2": 42}
        context = Context(data)
        self.assertEqual(context.get("key1"), "value1")
        self.assertEqual(context.get("key2"), 42)
    
    def test_get_existing_key(self):
        """Test getting an existing key."""
        context = Context({"name": "test"})
        self.assertEqual(context.get("name"), "test")
    
    def test_get_missing_key(self):
        """Test getting a missing key returns default."""
        context = Context()
        self.assertIsNone(context.get("missing"))
        self.assertEqual(context.get("missing", "default"), "default")
    
    def test_set_value(self):
        """Test setting a value."""
        context = Context()
        context.set("new_key", "new_value")
        self.assertEqual(context.get("new_key"), "new_value")
    
    def test_update_multiple(self):
        """Test updating with multiple key-value pairs."""
        context = Context({"key1": "value1"})
        context.update({"key2": "value2", "key3": "value3"})
        self.assertEqual(context.get("key1"), "value1")
        self.assertEqual(context.get("key2"), "value2")
        self.assertEqual(context.get("key3"), "value3")
    
    def test_has_key(self):
        """Test checking if key exists."""
        context = Context({"exists": True})
        self.assertTrue(context.has("exists"))
        self.assertFalse(context.has("missing"))
    
    def test_to_dict(self):
        """Test converting context to dictionary."""
        data = {"a": 1, "b": 2}
        context = Context(data)
        result = context.to_dict()
        self.assertEqual(result, data)
        self.assertIsNot(result, data)  # Should be a copy
    
    def test_clear(self):
        """Test clearing all data."""
        context = Context({"key": "value"})
        context.clear()
        self.assertEqual(context.to_dict(), {})


if __name__ == "__main__":
    unittest.main()

