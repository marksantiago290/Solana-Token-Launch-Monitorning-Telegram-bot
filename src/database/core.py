"""
Core database functionality for MongoDB connection and management.
"""

import logging
from typing import Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.database import Database

from config.settings import MONGODB_URI, DB_NAME

# Global database instance
_db: Optional[Database] = None

def init_database() -> bool:
    """
    Initialize the database connection and set up indexes
    
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    global _db
    
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI) 
        _db = client[DB_NAME]
        
        # Set up indexes for collections
        # Users collection
        _db.users.create_index([("user_id", ASCENDING)], unique=True)
        
        # User scans collection
        _db.user_scans.create_index([
            ("user_id", ASCENDING),
            ("scan_type", ASCENDING),
            ("date", ASCENDING)
        ], unique=True)
        
        # Token data collection
        _db.token_data.create_index([("address", ASCENDING)], unique=True)
        _db.token_data.create_index([("deployer", ASCENDING)])
        
        # Wallet data collection
        _db.wallet_data.create_index([("address", ASCENDING)], unique=True)
        _db.wallet_data.create_index([("is_kol", ASCENDING)])
        _db.wallet_data.create_index([("is_deployer", ASCENDING)])
        
        # Tracking subscriptions collection
        _db.wallet_watchlist.create_index([
            ("user_id", ASCENDING),
            ("address", ASCENDING),
            ("network", ASCENDING)
        ], unique=True)
        
        _db.token_watchlist.create_index([
            ("user_id", ASCENDING),
            ("address", ASCENDING),
            ("network", ASCENDING)
        ], unique=True)
        
        _db.approval_watchlist.create_index([
            ("user_id", ASCENDING),
            ("address", ASCENDING),
            ("network", ASCENDING)
        ], unique=True)
        
        # KOL wallets collection
        _db.kol_wallets.create_index([("address", ASCENDING)], unique=True)
        _db.kol_wallets.create_index([("name", ASCENDING)])
        
        # PumpFun tokens collection
        _db.pumpfun_tokens.create_index([("token_address", ASCENDING)], unique=True)
        _db.pumpfun_tokens.create_index([("first_seen", ASCENDING)])
        _db.pumpfun_tokens.create_index([("notification_sent", ASCENDING)])
        _db.pumpfun_tokens.create_index([("created_timestamp", ASCENDING)])
        
        # Notification subscriptions collection
        _db.notification_subscriptions.create_index([
            ("user_id", ASCENDING),
            ("subscription_type", ASCENDING)
        ], unique=True)
        _db.notification_subscriptions.create_index([("is_active", ASCENDING)])
        
        server_info = client.server_info()
        logging.info(f"Successfully connected to MongoDB version: {server_info.get('version')}")
        logging.info(f"Using database: {DB_NAME}")
        return True
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        return False

def get_database() -> Database:
    """
    Get the database instance
    
    Returns:
        Database: The MongoDB database instance
    """
    global _db
    if _db is None:
        init_database()
    return _db
