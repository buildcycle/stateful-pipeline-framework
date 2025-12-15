"""Shared context passed between pipeline steps."""


class Context:
    """Mutable context object shared across all steps in a pipeline."""
    
    def __init__(self, initial_data: dict = None):
        self._data = initial_data.copy() if initial_data else {}
    
    def get(self, key: str, default=None):
        """Get a value from the context."""
        return self._data.get(key, default)
    
    def set(self, key: str, value):
        """Set a value in the context."""
        self._data[key] = value
    
    def update(self, data: dict):
        """Update context with multiple key-value pairs."""
        self._data.update(data)
    
    def has(self, key: str) -> bool:
        """Check if a key exists in the context."""
        return key in self._data
    
    def to_dict(self) -> dict:
        """Return a copy of the context as a dictionary."""
        return self._data.copy()
    
    def clear(self):
        """Clear all data from the context."""
        self._data.clear()

