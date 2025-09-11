from datetime import datetime
from typing import Dict, Optional, Any

from .base_model import BaseModel

class WalletWatchlist(BaseModel):
    """Model for tracking wallet activities"""
    
    _fields = ["user_id", "address", "network", "created_at", "last_checked", "is_active", "metadata"]
    
    def __init__(
        self,
        user_id: int,
        address: str,
        network: str,  # 'eth', 'base', 'bsc'
        created_at: Optional[datetime] = None,
        last_checked: Optional[datetime] = None,
        is_active: bool = True,
        metadata=None
    ):
        self.user_id = user_id
        self.address = address
        self.network = network
        self.created_at = created_at or datetime.now()
        self.last_checked = last_checked or datetime.now()
        self.is_active = is_active
        self.metadata = metadata or {}


class TokenWatchlist(BaseModel):
    """Model for tracking token activities"""
    
    _fields = ["user_id", "address", "network", "created_at", "last_checked", "is_active", "metadata"]
    
    def __init__(
        self,
        user_id: int,
        address: str,
        network: str,  # 'eth', 'base', 'bsc'
        created_at: Optional[datetime] = None,
        last_checked: Optional[datetime] = None,
        is_active: bool = True,
        metadata=None
    ):
        self.user_id = user_id
        self.address = address
        self.network = network
        self.created_at = created_at or datetime.now()
        self.last_checked = last_checked or datetime.now()
        self.is_active = is_active
        self.metadata = metadata or {}


class ApprovalWatchlist(BaseModel):
    """Model for tracking new token deployments by a wallet"""
    
    _fields = ["user_id", "address", "network", "created_at", "last_checked", "is_active", "metadata"]
    
    def __init__(
        self,
        user_id: int,
        address: str,
        network: str,  # 'eth', 'base', 'bsc'
        created_at: Optional[datetime] = None,
        last_checked: Optional[datetime] = None,
        is_active: bool = True,
        metadata=None
    ):
        self.user_id = user_id
        self.address = address
        self.network = network
        self.created_at = created_at or datetime.now()
        self.last_checked = last_checked or datetime.now()
        self.is_active = is_active
        self.metadata = metadata or {}
