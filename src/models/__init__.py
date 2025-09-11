# Export all models for easy imports
from .base_model import BaseModel
from .user_models import User, UserScan
from .token_models import TokenData, PumpFunToken
from .wallet_models import WalletData, KOLWallet
from .watchlist_models import WalletWatchlist, TokenWatchlist, ApprovalWatchlist

# For backward compatibility
__all__ = [
    'BaseModel',
    'User', 
    'UserScan',
    'TokenData',
    'PumpFunToken',
    'WalletData',
    'KOLWallet',
    'WalletWatchlist',
    'TokenWatchlist',
    'ApprovalWatchlist'
]
