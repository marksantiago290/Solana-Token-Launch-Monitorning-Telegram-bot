from datetime import datetime
from typing import Dict, Any, TypeVar, Type, ClassVar

T = TypeVar('T', bound='BaseModel')

class BaseModel:
    """Base model with common functionality for all models"""
    
    # Fields that should be included in to_dict
    _fields: ClassVar[list] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model object to dictionary for database storage"""
        result = {}
        for field in self._fields:
            value = getattr(self, field, None)
            result[field] = value
        return result
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create model object from dictionary"""
        kwargs = {}
        for field in cls._fields:
            if field in data:
                kwargs[field] = data[field]
        return cls(**kwargs)
