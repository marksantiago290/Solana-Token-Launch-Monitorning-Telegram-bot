"""
Services package for business logic.

This package contains service modules that implement the core business logic
of the application, separated from the database and API layers.
"""

# Import key functions for easier access
from .blockchain_service import (
    get_web3_provider,
    is_valid_address,
    is_valid_token_contract,
    is_valid_wallet_address,
    check_wallet_balance
)

from .wallet_service import (
    create_wallet,
    create_user_wallet,
    check_user_wallet_balance
)

from .user_service import (
    get_or_create_user,
    extend_premium_subscription,
    check_rate_limit,
    increment_scan_count,
    get_user_premium_info,
    get_user_usage_stats,
    cleanup_expired_premium_subscriptions,
    set_user_admin_status,
    get_user_count_stats
)
