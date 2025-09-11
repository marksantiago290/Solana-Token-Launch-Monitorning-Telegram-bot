"""
Database package for handling MongoDB operations.
This package provides functions for interacting with the database.
"""

# Import core database functions
from .core import init_database, get_database

# Import user-related functions
from .user_operations import (
    get_user, save_user, update_user_activity
)

# Import token-related functions
from .token_operations import (
    get_tokendata, save_token_data, get_new_token_pumpfun
)

# Import maintenance functions
from .maintenance import (
    cleanup_old_data
)

# For backward compatibility, expose all functions at the package level
__all__ = [
    # Core
    'init_database', 'get_database',
    
    # User operations
    'get_user', 'save_user', 'update_user_activity',
    
    # Token operations
    'get_tokendata', 'save_token_data', 'get_new_token_pumpfun',
    
    # Maintenance
    'cleanup_old_data'
]
