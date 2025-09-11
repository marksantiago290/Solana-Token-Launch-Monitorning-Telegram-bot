from datetime import datetime
from typing import Dict, Optional, Any

from .base_model import BaseModel

class TokenData(BaseModel):
    """Model for cached token data"""
    
    _fields = [
        "address", "name", "symbol", "deployer", "deployment_date",
        "current_price", "current_market_cap", "ath_market_cap", 
        "ath_date", "last_updated"
    ]
    
    def __init__(
        self,
        address: str,
        name: Optional[str] = None,
        symbol: Optional[str] = None,
        deployer: Optional[str] = None,
        deployment_date: Optional[datetime] = None,
        current_price: Optional[float] = None,
        current_market_cap: Optional[float] = None,
        ath_market_cap: Optional[float] = None,
        ath_date: Optional[datetime] = None,
        last_updated: Optional[datetime] = None
    ):
        self.address = address
        self.name = name
        self.symbol = symbol
        self.deployer = deployer
        self.deployment_date = deployment_date
        self.current_price = current_price
        self.current_market_cap = current_market_cap
        self.ath_market_cap = ath_market_cap
        self.ath_date = ath_date
        self.last_updated = last_updated or datetime.now()

class PumpFunToken(BaseModel):
    """Model for PumpFun token notifications"""
    
    _fields = [
        "token_address", "symbol", "name", "logo", "thumbnail", "decimals",
        "usd_price", "usd_market_cap", "usd_price_24hr_percent_change", 
        "usd_price_5m_percent_change", "volume_1h", "volume_24h", 
        "swaps_1h", "swaps_24h", "total_supply", "holder_count", 
        "progress", "creator", "creator_balance_rate", "creator_token_status",
        "created_timestamp", "last_trade_timestamp", "twitter", "website", 
        "telegram", "is_wash_trading", "top_10_holder_rate", "sniper_count",
        "smart_degen_count", "possible_spam", "verified_contract", 
        "native_token", "first_seen", "notification_sent"
    ]
    
    def __init__(
        self,
        token_address: str,
        symbol: Optional[str] = None,
        name: Optional[str] = None,
        logo: Optional[str] = None,
        thumbnail: Optional[str] = None,
        decimals: Optional[int] = None,
        usd_price: Optional[float] = None,
        usd_market_cap: Optional[float] = None,
        usd_price_24hr_percent_change: Optional[float] = None,
        usd_price_5m_percent_change: Optional[float] = None,
        volume_1h: Optional[float] = None,
        volume_24h: Optional[float] = None,
        swaps_1h: Optional[int] = None,
        swaps_24h: Optional[int] = None,
        total_supply: Optional[int] = None,
        holder_count: Optional[int] = None,
        progress: Optional[float] = None,
        creator: Optional[str] = None,
        creator_balance_rate: Optional[float] = None,
        creator_token_status: Optional[str] = None,
        created_timestamp: Optional[int] = None,
        last_trade_timestamp: Optional[int] = None,
        twitter: Optional[str] = None,
        website: Optional[str] = None,
        telegram: Optional[str] = None,
        is_wash_trading: Optional[bool] = None,
        top_10_holder_rate: Optional[float] = None,
        sniper_count: Optional[int] = None,
        smart_degen_count: Optional[int] = None,
        possible_spam: Optional[bool] = None,
        verified_contract: Optional[bool] = None,
        native_token: Optional[bool] = None,
        first_seen: Optional[datetime] = None,
        notification_sent: Optional[bool] = None
    ):
        self.token_address = token_address
        self.symbol = symbol
        self.name = name
        self.logo = logo
        self.thumbnail = thumbnail
        self.decimals = decimals
        self.usd_price = usd_price
        self.usd_market_cap = usd_market_cap
        self.usd_price_24hr_percent_change = usd_price_24hr_percent_change
        self.usd_price_5m_percent_change = usd_price_5m_percent_change
        self.volume_1h = volume_1h
        self.volume_24h = volume_24h
        self.swaps_1h = swaps_1h
        self.swaps_24h = swaps_24h
        self.total_supply = total_supply
        self.holder_count = holder_count
        self.progress = progress
        self.creator = creator
        self.creator_balance_rate = creator_balance_rate
        self.creator_token_status = creator_token_status
        self.created_timestamp = created_timestamp
        self.last_trade_timestamp = last_trade_timestamp
        self.twitter = twitter
        self.website = website
        self.telegram = telegram
        self.is_wash_trading = is_wash_trading
        self.top_10_holder_rate = top_10_holder_rate
        self.sniper_count = sniper_count
        self.smart_degen_count = smart_degen_count
        self.possible_spam = possible_spam
        self.verified_contract = verified_contract
        self.native_token = native_token
        self.first_seen = first_seen or datetime.now()
        self.notification_sent = notification_sent or False