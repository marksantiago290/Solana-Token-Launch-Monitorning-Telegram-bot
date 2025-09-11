from datetime import datetime
from typing import Dict, List, Optional, Any

from .base_model import BaseModel

class WalletData(BaseModel):
    """Model for cached wallet data"""
    
    _fields = [
        "address", "name", "is_kol", "is_deployer", "tokens_deployed",
        "avg_holding_time", "total_trades", "win_rate", "last_updated"
    ]
    
    def __init__(
        self,
        address: str,
        name: Optional[str] = None,  # For KOL wallets
        is_kol: bool = False,
        is_deployer: bool = False,
        tokens_deployed: Optional[List[str]] = None,
        avg_holding_time: Optional[int] = None,  # in seconds
        total_trades: Optional[int] = None,
        win_rate: Optional[float] = None,
        last_updated: Optional[datetime] = None
    ):
        self.address = address
        self.name = name
        self.is_kol = is_kol
        self.is_deployer = is_deployer
        self.tokens_deployed = tokens_deployed or []
        self.avg_holding_time = avg_holding_time
        self.total_trades = total_trades
        self.win_rate = win_rate
        self.last_updated = last_updated or datetime.now()


class KOLWallet(BaseModel):
    """Model for KOL (Key Opinion Leader) wallets"""
    
    _fields = ["address", "name", "description", "social_links", "added_at"]
    
    def __init__(
        self,
        address: str,
        name: str,
        description: Optional[str] = None,
        social_links: Optional[Dict[str, str]] = None,
        added_at: Optional[datetime] = None
    ):
        self.address = address
        self.name = name
        self.description = description
        self.social_links = social_links or {}
        self.added_at = added_at or datetime.now()
