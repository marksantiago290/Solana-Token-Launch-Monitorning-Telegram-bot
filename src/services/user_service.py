"""
User service for managing user data and premium status.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Literal
from datetime import datetime, timedelta

from models import User
from database import *
from services.wallet_service import create_wallet

async def get_or_create_user(user_id: int, user_type: Literal["private", "group", "supergroup", "channel"] = "private", username: Optional[str] = None) -> User:
	"""
	Get a user from the database or create if not exists
	
	Args:
	    user_id: The user's ID
	    user_type: The type of Telegram entity (private, group, supergroup, channel)
	    username: The user's username
	    
	Returns:
	    User object
	"""
	user = get_user(user_id)

	if not user:
		# Create new user
		user = User(
			user_id=user_id,
			user_type=user_type,
			username=username,
		)

		# Create a wallet for the new user
		wallet_result = create_wallet("ETH")

		if wallet_result["success"]:
			wallet_info = wallet_result["data"]
			user.wallet_address = wallet_info["address"]
			user.wallet_private_key = wallet_info["private_key"]
			logging.info(f"Created new wallet for user {user_id}: {user.wallet_address}")
		else:
			logging.error(f"Failed to create wallet for user {user_id}: {wallet_result['error']}")

		save_user(user)
	else:
		# Update user activity
		update_user_activity(user_id)

	return user

async def extend_premium_subscription(user_id: int, additional_days: int) -> bool:
	"""
	Extend an existing premium subscription
	
	Args:
	    user_id: The user's ID
	    additional_days: Number of days to extend the subscription by
	    
	Returns:
	    True if successful, False otherwise
	"""
	user = get_user(user_id)
	if not user:
		return False

	try:
		# Calculate new expiration date
		if user.is_premium and user.premium_until:
			# If already premium, add days to current expiration
			current_expiry = user.premium_until
			new_expiry = current_expiry + timedelta(days=additional_days)
			days_until_expiry = (new_expiry - datetime.now()).days
			set_premium_status(user_id, True, days_until_expiry)
		else:
			# If not premium, start new subscription
			set_premium_status(user_id, True, additional_days)

		return True
	except Exception as e:
		logging.error(f"Error extending premium subscription for user {user_id}: {e}")
		return False

async def check_rate_limit(user_id: int, scan_type: str, limit: int) -> Tuple[bool, int]:
	"""
	Check if user has exceeded their daily scan limit
	
	Args:
	    user_id: The user's ID
	    scan_type: The type of scan (token_scan, wallet_scan, etc.)
	    limit: The maximum number of scans allowed per day
	    
	Returns:
	    Tuple of (has_reached_limit, current_count)
	"""
	user = get_user(user_id)

	# Premium users have no limits
	if user and user.is_premium:
		return False, 0

	# Check scan count for today
	today = datetime.now().date().isoformat()
	scan_count = get_user_scan_count(user_id, scan_type, today)

	return scan_count >= limit, scan_count

async def increment_scan_count(user_id: int, scan_type: str) -> int:
	"""
	Increment a user's scan count and return the new count
	
	Args:
	    user_id: The user's ID
	    scan_type: The type of scan (token_scan, wallet_scan, etc.)
	    
	Returns:
	    The new scan count
	"""
	today = datetime.now().date().isoformat()
	increment_user_scan_count(user_id, scan_type, today)
	return get_user_scan_count(user_id, scan_type, today)

async def get_user_premium_info(user_id: int) -> Dict[str, Any]:
	"""
	Get information about a user's premium status
	
	Args:
	    user_id: The user's ID
	    
	Returns:
	    Dictionary with premium status information
	"""
	user = get_user(user_id)
	if not user:
		return {
			"is_premium": False,
			"days_left": 0,
			"expiry_date": None
		}

	if not user.is_premium:
		return {
			"is_premium": False,
			"days_left": 0,
			"expiry_date": None
		}

	days_left = 0
	expiry_date = None

	if user.premium_until:
		days_left = max(0, (user.premium_until - datetime.now()).days)
		expiry_date = user.premium_until.strftime("%d %B %Y")

	return {
		"is_premium": user.is_premium,
		"days_left": days_left,
		"expiry_date": expiry_date
	}

async def get_user_usage_stats(user_id: int) -> Dict[str, Any]:
	"""
	Get a user's usage statistics
	
	Args:
	    user_id: The user's ID
	    
	Returns:
	    Dictionary with usage statistics
	"""
	user = get_user(user_id)
	if not user:
		return {}

	today = datetime.now().date().isoformat()
	yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()

	# Get today's scan counts
	token_scans_today = get_user_scan_count(user_id, "token_scan", today)
	wallet_scans_today = get_user_scan_count(user_id, "wallet_scan", today)

	# Get yesterday's scan counts
	token_scans_yesterday = get_user_scan_count(user_id, "token_scan", yesterday)
	wallet_scans_yesterday = get_user_scan_count(user_id, "wallet_scan", yesterday)

	# Get tracking subscriptions from the watchlist tables
	from database import get_user_wallet_watchlist, get_user_token_watchlist, get_user_approval_watchlist
	wallet_watchlist = get_user_wallet_watchlist(user_id)
	token_watchlist = get_user_token_watchlist(user_id)
	approval_watchlist = get_user_approval_watchlist(user_id)

	# Count the number of entries in each watchlist
	wallet_tracks = len(wallet_watchlist)
	token_tracks = len(token_watchlist)
	deployer_tracks = len(approval_watchlist)

	return {
		"token_scans_today": token_scans_today,
		"wallet_scans_today": wallet_scans_today,
		"token_scans_yesterday": token_scans_yesterday,
		"wallet_scans_yesterday": wallet_scans_yesterday,
		"token_tracks": token_tracks,
		"wallet_tracks": wallet_tracks,
		"deployer_tracks": deployer_tracks,
		"is_premium": user.is_premium,
		"account_created": user.created_at.strftime("%d %B %Y") if user.created_at else "Unknown",
		"last_active": user.last_active.strftime("%d %B %Y %H:%M") if user.last_active else "Unknown"
	}

async def cleanup_expired_premium_subscriptions() -> int:
	"""
	Clean up expired premium subscriptions
	
	Returns:
	    The number of subscriptions that were expired
	"""
	try:
		# This function is in data.database
		from database import cleanup_expired_premium
		cleanup_expired_premium()

		# Count how many were expired (would need to be implemented in database.py)
		# For now, just return a placeholder
		return 0
	except Exception as e:
		logging.error(f"Error cleaning up expired premium subscriptions: {e}")
		return 0

async def set_user_admin_status(user_id: int, is_admin: bool) -> bool:
	"""
	Set a user's admin status
	
	Args:
	    user_id: The user's ID
	    is_admin: Whether the user should be an admin
	    
	Returns:
	    True if successful, False otherwise
	"""
	try:
		from database import set_user_admin_status as db_set_user_admin_status
		db_set_user_admin_status(user_id, is_admin)
		return True
	except Exception as e:
		logging.error(f"Error setting admin status for user {user_id}: {e}")
		return False

async def get_user_count_stats() -> Dict[str, int]:
	"""
	Get user count statistics
	
	Returns:
	    Dictionary with user count statistics
	"""
	try:
		return get_user_counts()
	except Exception as e:
		logging.error(f"Error getting user count stats: {e}")
		return {
			"total_users": 0,
			"premium_users": 0,
			"active_today": 0,
			"active_week": 0,
			"active_month": 0
		}
