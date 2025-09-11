"""
Database operations related to tokens.
"""

import logging
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime

from models import TokenData
from api.token_api import (
    fetch_token_metadata, fetch_token_details, fetch_new_token_pumpfun
)
from .core import get_database

def get_tokendata(address: str) -> Optional[TokenData]:
    """
    Get token data by address
    
    Args:
        address: The token contract address
        
    Returns:
        TokenData object if found, None otherwise
    """
    db = get_database()
    token_data = db.token_data.find_one({"address": address.lower()})
    if token_data:
        return TokenData.from_dict(token_data)
    return None

def save_token_data(token: TokenData) -> None:
    """
    Save or update token data
    
    Args:
        token: The token data object to save
    """
    db = get_database()
    token_dict = token.to_dict()
    token_dict["address"] = token_dict["address"].lower()  # Normalize address
    token_dict["last_updated"] = datetime.now()
    
    db.token_data.update_one(
        {"address": token_dict["address"]},
        {"$set": token_dict},
        upsert=True
    )

async def get_token_metadata(token_address: str, chain: str) -> Dict[str, Any]:
    """
    Get detailed token metadata for a specific token
    
    Args:
        token_address: The token contract address
        chain: The blockchain network (eth, base, bsc)
    
    Returns:
        Dictionary containing token metadata including name, symbol, decimals, 
        total supply, logo, links, categories, etc.
    """
    logging.info(f"Getting token metadata for {token_address} on {chain}")
    
    try:
        # Fetch token metadata from API
        response = await fetch_token_metadata(chain, token_address)
        
        if not response:
            logging.warning(f"No metadata found for token {token_address} on {chain}")
            return None
        
        # Extract relevant data from response
        metadata = {
            "address": response.get("address"),
            "name": response.get("name"),
            "symbol": response.get("symbol"),
            "decimals": response.get("decimals"),
            "logo": response.get("logo"),
            "thumbnail": response.get("thumbnail"),
            "total_supply": response.get("total_supply"),
            "total_supply_formatted": response.get("total_supply_formatted"),
            "fully_diluted_valuation": response.get("fully_diluted_valuation"),
            "block_number": response.get("block_number"),
            "validated": response.get("validated"),
            "created_at": response.get("created_at"),
            "possible_spam": response.get("possible_spam", False),
            "verified_contract": response.get("verified_contract", False),
            "categories": response.get("categories", []),
            "links": response.get("links", {}),
            "security_score": response.get("security_score"),
            "description": response.get("description"),
            "circulating_supply": response.get("circulating_supply"),
            "market_cap": response.get("market_cap")
        }
        
        return metadata
        
    except Exception as e:
        logging.error(f"Error getting token metadata: {e}", exc_info=True)
        return None

async def get_token_details(token_address: str, chain: str) -> Dict[str, Any]:
    """
    Get detailed token details for a specific token
    
    Args:
        token_address: The token contract address
        chain: The blockchain network (eth, base, bsc)
    
    Returns:
        Dictionary containing token details including name, symbol, decimals, 
        total supply, logo, links, categories, etc.
    """
    logging.info(f"Getting token details for {token_address} on {chain}")
    
    try:
        # Fetch token details from API
        response = await fetch_token_details(chain, token_address)
        
        if not response:
            logging.warning(f"No details found for token {token_address} on {chain}")
            return None
        
        return response
        
    except Exception as e:
        logging.error(f"Error getting token details: {e}", exc_info=True)
        return None

async def get_new_token_pumpfun() -> List[Dict[str, Any]]:
    """
    Get new token pumpfun
    """

    logging.info("Getting new token pumpfun")
    response = await fetch_new_token_pumpfun()

    return response.get("new_token_pumpfun")
