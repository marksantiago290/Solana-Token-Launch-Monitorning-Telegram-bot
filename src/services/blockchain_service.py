"""
Core blockchain interaction service.
Provides low-level functions for interacting with various blockchains.
"""

import logging
import base58
import re
import time
import random
from datetime import datetime
from typing import Dict, Optional, Any, List
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from solana.rpc.api import Client as SolanaClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair

from config.settings import SOL_PROVIDER_URL, SOLANA_TOKEN_PROGRAM_ID

# Configure web3 connections for different networks
w3_sol = SolanaClient(SOL_PROVIDER_URL)

# ERC20 ABI for basic token operations
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

def get_web3_provider(chain: str) -> Web3:
    """
    Get the appropriate Web3 provider for the specified chain
    
    Args:
        chain: The blockchain network (eth, base, bsc)
    
    Returns:
        Web3: The Web3 provider for the specified chain
    """
    if chain.lower() == "eth":
        return w3_eth
    elif chain.lower() == "base":
        return w3_base
    elif chain.lower() == "bsc" or chain.lower() == "bnb":
        return w3_bsc
    elif chain.lower() == "sol":
        return w3_sol
    else:
        logging.warning(f"Unknown chain '{chain}', defaulting to Ethereum")
        return w3_eth

async def is_valid_address(address:str, chain:str) -> bool:
    """
    Validates if the given string is a valid EVM address.
    
    Args:
        address: The address to validate
        
    Returns:
        bool: True if the address is valid, False otherwise
    """
    if not address:
        return False
    
    # Check if address matches the format (0x followed by 40 hex characters)
    if re.match(r'^0x[0-9a-fA-F]{40}$', address):
        return True
    
    if chain and chain.lower() == 'sol':
        return is_valid_solana_address(address)
    
    return False

def is_valid_solana_address(address):
    try:
        # Solana addresses are base58 encoded and 32 bytes (after decoding)
        decoded = base58.b58decode(address)
        return len(decoded) == 32
    except Exception:
        return False

async def is_valid_token_contract(address: str, chain: str) -> bool:
    """
    Check if an address is a valid token contract
    
    Args:
        address: The address to check
        chain: The blockchain network
        
    Returns:
        bool: True if the address is a valid token contract, False otherwise
    """
    if not await is_valid_address(address, chain):
        logging.warning(f"Invalid address format for checking is_valid_token_contract: {address} on {chain}")
        return False

    w3 = get_web3_provider(chain)

    if chain.lower() == "sol":
        max_retries = 5
        retry_count = 0
        retry_delay = 1  # Start with 1 second delay
        
        while retry_count < max_retries:
            try:
                try:
                    pubkey = Pubkey.from_string(address)
                except Exception as e:
                    logging.warning(f"Invalid Solana pubkey format: {e}")
                    return False
                
                account_info = w3.get_account_info(pubkey)

                if not account_info.value:
                    logging.info(f"No account found for Solana address: {address}")
                    return False

                if str(account_info.value.owner) != SOLANA_TOKEN_PROGRAM_ID:
                    logging.info(f"Solana address is not owned by Token program: {address}")
                    return False
                
                return True
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logging.error(f"Error validating Solana token after {max_retries} retries: {e}")
                    return False
                
                # Log the retry attempt
                logging.warning(f"Rate limit hit when validating Solana token. Retrying {retry_count}/{max_retries} in {retry_delay}s: {e}")
                
                # Exponential backoff with jitter
                time.sleep(retry_delay + (random.random() * 0.5))
                retry_delay = min(retry_delay * 2, 10)  # Double the delay up to a maximum of 10 seconds
    else:
        try:
            checksum_address = w3.to_checksum_address(address.lower())
            code = w3.eth.get_code(checksum_address)

            if code == b'' or code == b'0x':
                logging.info("Address has no contract code.")
                return False

            contract = w3.eth.contract(address=checksum_address, abi=ERC20_ABI)

            # Try to call basic ERC20 functions to verify it's a token
            try:
                symbol = contract.functions.symbol().call()
                logging.info(f"Token symbol: {symbol}")
            except Exception as e:
                logging.warning(f"Couldn't get token symbol: {e}")

            try:
                name = contract.functions.name().call()
                logging.info(f"Token name: {name}")
                return True
            except Exception as e:
                logging.warning(f"Couldn't get token name: {e}")

            try:
                decimals = contract.functions.decimals().call()
                logging.info(f"Token decimals: {decimals}")
                return True
            except Exception as e:
                logging.warning(f"Couldn't get token decimals: {e}")

            logging.warning("Address has code but no ERC-20 behavior.")
            return False

        except Exception as e:
            logging.error(f"Error validating token contract: {e}")
            return False
    
async def is_valid_wallet_address(address: str, chain: str) -> bool:
    """
    Validate if the provided address is a wallet (not a contract)
    
    Args:
        address: The address to validate
        chain: The blockchain network (eth, base, bsc)
    
    Returns:
        bool: True if the address is a valid wallet, False otherwise
    """
    # First check if it's a valid address
    if not await is_valid_address(address, chain):
        return False
    
    if chain.lower() == "sol":
        try:
            is_token = await is_valid_token_contract(address, chain)
            return not is_token
        except Exception as e:
            logging.error(f"Error validating Solana wallet address: {e}")
            return True
    
    w3 = get_web3_provider(chain)
    
    try:
        checksum_address = w3.to_checksum_address(address.lower())
        code = w3.eth.get_code(checksum_address)
        # If there's no code, it's a regular wallet address
        return code == b'' or code == '0x'
    except Exception as e:
        logging.error(f"Error validating wallet address on {chain}: {e}")
        # Return True if the format is correct but web3 validation fails
        # This is a fallback to prevent false negatives due to connection issues
        return True

def check_wallet_balance(address: str, network: str, token_address: Optional[str] = None) -> Dict[str, Any]:
    """
    Check the balance of a wallet on the specified network.
    
    Args:
        address: The wallet address to check
        network: The network (ETH, BSC, BASE)
        token_address: Optional ERC20/BEP20 token address to check balance for
        
    Returns:
        Dictionary with balance information or error details
    """
    retry_count = 0
    max_retries = 3
    
    logging.info(f"Checking balance for {address} on {network}")
    
    while retry_count < max_retries:
        try:
            w3 = get_web3_provider(network)
            
            # Validate address format
            if not w3.is_address(address):
                logging.error(f"Invalid {network} address format: {address}")
                return {
                    "success": False,
                    "error": {
                        "code": "INVALID_ADDRESS",
                        "message": f"Invalid {network} address format"
                    }
                }
            
            result = {
                "success": True,
                "data": {
                    "address": address,
                    "network": network,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Check native currency balance (ETH/BNB)
            native_balance = w3.eth.get_balance(address)
            result["data"]["native_balance"] = native_balance
            result["data"]["formatted_native_balance"] = w3.from_wei(native_balance, 'ether')
            result["data"]["native_currency"] = network
            
            # Check if balance is sufficient for gas fees
            gas_price = w3.eth.gas_price
            standard_gas_limit = 21000  # For a basic transfer
            estimated_gas_cost = gas_price * standard_gas_limit
            result["data"]["estimated_gas_cost"] = estimated_gas_cost
            result["data"]["formatted_gas_cost"] = w3.from_wei(estimated_gas_cost, 'ether')
            result["data"]["has_sufficient_gas"] = native_balance > estimated_gas_cost
            
            # Check token balance if token address is provided
            if token_address:
                if not w3.is_address(token_address):
                    result["data"]["token_error"] = "Invalid token address format"
                else:
                    try:
                        token_contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
                        token_balance = token_contract.functions.balanceOf(address).call()
                        token_decimals = 18  # Default for most tokens
                        
                        # Try to get token decimals if the function exists
                        try:
                            token_decimals = token_contract.functions.decimals().call()
                        except Exception:
                            pass  # Use default decimals if not available
                            
                        result["data"]["token_address"] = token_address
                        result["data"]["token_balance"] = token_balance
                        result["data"]["formatted_token_balance"] = token_balance / (10 ** token_decimals)
                    except Exception as token_error:
                        result["data"]["token_error"] = str(token_error)
            
            logging.info(f"Balance check for {address} on {network}: {result['data']['formatted_native_balance']} {network}")
            return result
                
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                logging.error(f"Failed to check {network} balance for {address} after {max_retries} attempts: {str(e)}")
                return {
                    "success": False,
                    "error": {
                        "code": "BALANCE_CHECK_FAILED",
                        "message": f"Failed to check {network} wallet balance",
                        "details": str(e)
                    }
                }
            else:
                logging.warning(f"Retry {retry_count}/{max_retries} checking balance for {address} on {network}")
                time.sleep(1)

def transfer_funds_to_admin(subscription: Dict[str, Any]) -> Dict[str, Any]:
    """Transfer funds from user wallet to admin wallet."""
    try:
        network = subscription["network"]
        web3 = get_web3_provider(network)

        user_address = subscription["wallet_address"]
        user_private_key = subscription["wallet_private_key"]
        admin_address = ADMIN_WALLET_ADDRESS
        
        if not web3.is_address(admin_address):
            return {
                "success": False,
                "error": {
                    "code": "INVALID_ADMIN_ADDRESS",
                    "message": f"Invalid admin address for {network}"
                }
            }

        # Get user balance
        balance = web3.eth.get_balance(user_address)

        # Calculate gas cost - BNB Chain often needs different gas settings
        if network == "BNB":
            gas_price = web3.eth.gas_price
            # BNB Chain sometimes needs a higher gas price
            gas_price = int(gas_price * 1.1)  # Add 10% to ensure it goes through
            gas_limit = 21000  # Standard gas limit
        else:
            gas_price = web3.eth.gas_price
            gas_limit = 21000  # Standard gas limit for ETH transfer
            
        gas_cost = gas_price * gas_limit

        # Get the required amount in Wei
        required_amount = subscription["require_amount"]
        
        # Check if the required_amount is already in Wei or needs conversion
        if isinstance(required_amount, float) or isinstance(required_amount, int) and required_amount < 1e18:
            # Convert from ETH to Wei if it's a small number (likely in ETH)
            required_amount_wei = web3.to_wei(required_amount, 'ether')
        else:
            # Already in Wei
            required_amount_wei = required_amount
            
        # Check if user has enough balance for amount + gas
        amount_to_send = required_amount_wei - gas_cost
        
        if balance < amount_to_send:
            return {
                "success": False,
                "error": {
                    "code": "INSUFFICIENT_BALANCE",
                    "message": f"Insufficient balance for transaction. Need {web3.from_wei(amount_to_send, 'ether'):.6f} {network} (including gas), but have {web3.from_wei(balance, 'ether'):.6f} {network}"
                }
            }

        # Get the actual chain ID from the connected network
        chain_id = web3.eth.chain_id

        # Build transaction
        tx = {
            'nonce': web3.eth.get_transaction_count(user_address),
            'to': admin_address,
            'value': amount_to_send,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': chain_id
        }

        # Sign and send transaction
        signed_tx = web3.eth.account.sign_transaction(tx, user_private_key)
        
        # Handle different web3.py versions
        if hasattr(signed_tx, 'rawTransaction'):
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        else:
            tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

        return {
            "success": True,
            "data": {
                "transaction_hash": tx_hash.hex(),
                "amount": web3.from_wei(amount_to_send, 'ether')
            }
        }
    except Exception as e:
        logging.error(f"Transfer funds error: {str(e)}")
        return {
            "success": False,
            "error": {
                "code": "TRANSFER_FAILED",
                "message": "Failed to transfer funds to admin wallet",
                "details": str(e)
            }
        }
