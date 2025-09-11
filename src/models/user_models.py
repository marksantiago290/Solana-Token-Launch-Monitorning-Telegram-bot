from datetime import datetime
from typing import Dict, Optional, Any, Literal

from .base_model import BaseModel

class User(BaseModel):
    """User model representing a bot user"""
    
    _fields = [
        "user_id", "user_type", "username",
        "is_premium", "premium_until", "created_at", "last_active",
        "wallet_address", "wallet_private_key", "premium_plan", "payment_currency"
    ]
    
    def __init__(
        self,
        user_id: int,
        user_type: Literal["private", "group", "supergroup", "channel"] = "private",
        username: Optional[str] = None,
        is_premium: bool = False,
        premium_until: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        last_active: Optional[datetime] = None,
        wallet_address: Optional[str] = None,
        wallet_private_key: Optional[str] = None,
        premium_plan: Optional[str] = None,
        payment_currency: Optional[str] = None
    ):
        self.user_id = user_id
        self.user_type = user_type
        self.username = username
        self.is_premium = is_premium
        self.premium_until = premium_until
        self.created_at = created_at or datetime.now()
        self.last_active = last_active or datetime.now()
        self.wallet_address = wallet_address
        self.wallet_private_key = wallet_private_key
        self.premium_plan = premium_plan
        self.payment_currency = payment_currency


class UserScan(BaseModel):
    """Model for tracking user scan usage"""
    
    _fields = ["user_id", "scan_type", "date", "count"]
    
    def __init__(
        self,
        user_id: int,
        scan_type: str,  # 'token_scan', 'wallet_scan', etc.
        date: str,  # ISO format date string
        count: int = 0
    ):
        self.user_id = user_id
        self.scan_type = scan_type
        self.date = date
        self.count = count
