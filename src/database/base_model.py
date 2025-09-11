"""
Base model class for all database models.
"""

from typing import Dict, Any, ClassVar, List

class BaseModel:
    """Base model class with common functionality for all models"""
    
    # Class variable to be overridden by subclasses
    _fields: ClassVar[List[str]] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model object to dictionary for database storage
        
        Returns:
            Dictionary representation of the model
        """
        return {field: getattr(self, field) for field in self._fields if hasattr(self, field)}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """
        Create model object from dictionary
        
        Args:
            data: Dictionary containing model data
            
        Returns:
            Model object
        """
        # Filter the data to only include fields defined in _fields
        filtered_data = {k: v for k, v in data.items() if k in cls._fields}
        return cls(**filtered_data)
