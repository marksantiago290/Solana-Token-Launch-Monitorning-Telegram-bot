import logging
from api.client import api_client
from config.settings import API_BASE_URL

logger = logging.getLogger(__name__)

async def fetch_token_metadata(chain, token_address):
    """Fetch basic token metadata"""
    url = f"{API_BASE_URL}/api/v1/token_meta/{chain}/{token_address}"
    logger.info(f"Fetching token metadata for {chain}:{token_address}")
    return await api_client.get(url)

async def fetch_token_details(chain, token_address):
    """Fetch basic token details"""
    url = f"{API_BASE_URL}/api/v1/token_details/{chain}/{token_address}"
    logger.info(f"Fetching token details for {chain}:{token_address}")
    return await api_client.get(url)

async def fetch_new_token_pumpfun():
    """Fetch new token pumpfun"""
    url = f"{API_BASE_URL}/api/v1/new_token_pumpfun"
    logger.info(f"Fetching new token pumpfun")
    return await api_client.get(url)