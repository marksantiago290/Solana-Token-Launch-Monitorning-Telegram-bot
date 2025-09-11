"""
Database maintenance operations.
"""

from datetime import datetime, timedelta
from .core import get_database

def cleanup_old_data(days: int = 30) -> None:
    """
    Clean up old data that hasn't been updated in a while
    
    Args:
        days: Number of days to keep data for
    """
    db = get_database()
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Remove old token data
    db.token_data.delete_many({"last_updated": {"$lt": cutoff_date}})
    
    # Remove old wallet data
    db.wallet_data.delete_many({"last_updated": {"$lt": cutoff_date}})
