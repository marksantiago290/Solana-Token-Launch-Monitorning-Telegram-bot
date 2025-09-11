"""
Database operations related to users.
"""

import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta

from models import User, UserScan
from .core import get_database

def get_user(user_id: int) -> Optional[User]:
    """
    Get a user by ID
    
    Args:
        user_id: The user's ID
        
    Returns:
        User object if found, None otherwise
    """
    db = get_database()
    user_data = db.users.find_one({"user_id": user_id})
    if user_data:
        return User.from_dict(user_data)
    return None

def save_user(user: User) -> None:
    """
    Save or update a user
    
    Args:
        user: The user object to save
    """
    db = get_database()
    user_dict = user.to_dict()
    db.users.update_one(
        {"user_id": user.user_id},
        {"$set": user_dict},
        upsert=True
    )

def update_user_activity(user_id: int) -> None:
    """
    Update user's last active timestamp
    
    Args:
        user_id: The user's ID
    """
    db = get_database()
    db.users.update_one(
        {"user_id": user_id},
        {"$set": {"last_active": datetime.now()}}
    )
