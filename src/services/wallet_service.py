"""
Wallet service for creating and managing blockchain wallets.
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
from web3 import Web3

from services.blockchain_service import get_web3_provider, check_wallet_balance

def create_wallet(network: str) -> Dict[str, Any]:
    """
    Create a new wallet on the specified network.
    
    Args:
        network: The blockchain network (ETH, BSC, BASE)
        
    Returns:
        Dictionary with wallet information or error details
    """
    try:
        web3 = get_web3_provider(network)
        account = web3.eth.account.create()

        wallet_info = {
            "address": account.address,
            "private_key": account.key.hex(),
            "network": network
        }

        logging.info(f"Created new {network} wallet: {account.address}")
        return {
            "success": True,
            "data": wallet_info
        }
    except Exception as e:
        logging.error(f"Failed to create {network} wallet: {str(e)}")
        return {
            "success": False,
            "error": {
                "code": "WALLET_CREATION_FAILED",
                "message": f"Failed to create new {network} wallet",
                "details": str(e)
            }
        }

async def create_user_wallet(user_id: int, network: str) -> Dict[str, Any]:
    """
    Create a wallet for a user on the specified network
    
    Args:
        user_id: The user's ID
        network: The network to create the wallet on (ETH or BNB)
        
    Returns:
        Dictionary with wallet information or error details
    """
    from database import get_user, save_user

    try:
        # Get user from database
        user = get_user(user_id)
        if not user:
            return {
                "success": False,
                "error": "User not found"
            }
        
        # Check if user already has a wallet
        if user.wallet_address and user.wallet_private_key:
            return {
                "success": True,
                "data": {
                    "wallet_address": user.wallet_address,
                    "message": "User already has a wallet"
                }
            }
        
        # Create wallet
        wallet_result = create_wallet(network)
        
        if not wallet_result["success"]:
            return wallet_result
        
        wallet_info = wallet_result["data"]
        
        # Update user with wallet information
        user.wallet_address = wallet_info["address"]
        user.wallet_private_key = wallet_info["private_key"]
        user.payment_currency = network
        
        # Save updated user to database
        save_user(user)
        
        logging.info(f"Created {network} wallet for user {user_id}: {wallet_info['address']}")
        
        return {
            "success": True,
            "data": {
                "wallet_address": wallet_info["address"],
                "network": network
            }
        }
    except Exception as e:
        logging.error(f"Error creating wallet for user {user_id}: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to create wallet: {str(e)}"
        }

async def check_user_wallet_balance(user_id: int) -> Dict[str, Any]:
    """
    Check the balance of a user's wallet
    
    Args:
        user_id: The user's ID
        
    Returns:
        Dictionary with balance information or error details
    """
    from database import get_user

    try:
        # Get user from database
        user = get_user(user_id)
        if not user:
            return {
                "success": False,
                "error": "User not found"
            }
        
        # Check if user has a wallet
        if not user.wallet_address or not user.payment_currency:
            return {
                "success": False,
                "error": "User does not have a wallet"
            }
        
        # Check wallet balance
        return check_wallet_balance(
            user.wallet_address, 
            user.payment_currency
        )
    except Exception as e:
        logging.error(f"Error checking wallet balance for user {user_id}: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to check wallet balance: {str(e)}"
        }
