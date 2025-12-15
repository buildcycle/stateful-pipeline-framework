"""Unit tests for retry mechanism."""

import unittest
from unittest.mock import Mock, patch
from pipeline_engine.core.retry import RetryConfig, retry_step
from pipeline_engine.core.errors import RetryExhaustedError


class TestRetryConfig(unittest.TestCase):
    """Test cases for RetryConfig."""
    
    def test_init_defaults(self):
        """Test RetryConfig initialization with defaults."""
        config = RetryConfig()
        self.assertEqual(config.max_attempts, 3)
        self.assertEqual(config.delay, 1.0)
        self.assertEqual(config.backoff_multiplier, 2.0)
        self.assertIsNotNone(config.retry_on)
    
    def test_init_custom(self):
        """Test RetryConfig initialization with custom values."""
        def custom_retry(e):
            return isinstance(e, ValueError)
        
        config = RetryConfig(
            max_attempts=5,
            delay=2.0,
            backoff_multiplier=1.5,
            retry_on=custom_retry
        )
        self.assertEqual(config.max_attempts, 5)
        self.assertEqual(config.delay, 2.0)
        self.assertEqual(config.backoff_multiplier, 1.5)
        self.assertEqual(config.retry_on, custom_retry)
    
    def test_should_retry_within_limit(self):
        """Test should_retry returns True within attempt limit."""
        config = RetryConfig(max_attempts=3)
        error = ValueError("test")
        self.assertTrue(config.should_retry(error, 0))
        self.assertTrue(config.should_retry(error, 1))
        self.assertTrue(config.should_retry(error, 2))
    
    def test_should_retry_exceeds_limit(self):
        """Test should_retry returns False when exceeds limit."""
        config = RetryConfig(max_attempts=3)
        error = ValueError("test")
        self.assertFalse(config.should_retry(error, 3))
        self.assertFalse(config.should_retry(error, 4))
    
    def test_should_retry_with_custom_function(self):
        """Test should_retry with custom retry function."""
        def only_retry_value_error(e):
            return isinstance(e, ValueError)
        
        config = RetryConfig(retry_on=only_retry_value_error)
        value_error = ValueError("test")
        type_error = TypeError("test")
        
        self.assertTrue(config.should_retry(value_error, 0))
        self.assertFalse(config.should_retry(type_error, 0))


class TestRetryStep(unittest.TestCase):
    """Test cases for retry_step function."""
    
    @patch('time.sleep')
    def test_retry_success_first_attempt(self, mock_sleep):
        """Test retry succeeds on first attempt."""
        execute_fn = Mock(return_value="success")
        config = RetryConfig(max_attempts=3)
        
        result, attempts = retry_step("test_step", execute_fn, config)
        
        self.assertEqual(result, "success")
        self.assertEqual(attempts, 1)
        execute_fn.assert_called_once()
        mock_sleep.assert_not_called()
    
    @patch('time.sleep')
    def test_retry_success_after_failures(self, mock_sleep):
        """Test retry succeeds after some failures."""
        execute_fn = Mock(side_effect=[ValueError("fail"), ValueError("fail"), "success"])
        config = RetryConfig(max_attempts=3, delay=0.01)
        
        result, attempts = retry_step("test_step", execute_fn, config)
        
        self.assertEqual(result, "success")
        self.assertEqual(attempts, 3)
        self.assertEqual(execute_fn.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)
    
    @patch('time.sleep')
    def test_retry_exhausted(self, mock_sleep):
        """Test retry raises RetryExhaustedError when attempts exhausted."""
        execute_fn = Mock(side_effect=ValueError("always fails"))
        config = RetryConfig(max_attempts=2, delay=0.01)
        
        with self.assertRaises(RetryExhaustedError) as context:
            retry_step("test_step", execute_fn, config)
        
        self.assertEqual(context.exception.step_name, "test_step")
        # With max_attempts=2, we try attempts 0, 1, 2 (3 total) before exhausting
        self.assertEqual(context.exception.attempts, 3)
        self.assertEqual(execute_fn.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)
    
    @patch('time.sleep')
    def test_retry_backoff_calculation(self, mock_sleep):
        """Test retry uses exponential backoff."""
        execute_fn = Mock(side_effect=[ValueError("fail"), ValueError("fail"), "success"])
        config = RetryConfig(max_attempts=3, delay=1.0, backoff_multiplier=2.0)
        
        retry_step("test_step", execute_fn, config)
        
        # First retry: delay * (multiplier ^ 0) = 1.0
        # Second retry: delay * (multiplier ^ 1) = 2.0
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_any_call(1.0)
        mock_sleep.assert_any_call(2.0)


if __name__ == "__main__":
    unittest.main()

