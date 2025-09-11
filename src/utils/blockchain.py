from typing import Dict, Optional

def get_explorer_url(chain: str, address: str, is_token: bool = True) -> str:
    """
    Get explorer URL for an address based on chain
    
    Args:
        chain: The blockchain network (eth, bsc, base, etc.)
        address: The address to view
        is_token: Whether the address is a token contract (True) or a wallet (False)
    
    Returns:
        URL to the blockchain explorer for the given address
    """
    explorers = {
        'eth': {
            'token': 'https://etherscan.io/token/',
            'address': 'https://etherscan.io/address/'
        },
        'bsc': {
            'token': 'https://bscscan.com/token/',
            'address': 'https://bscscan.com/address/'
        },
        'base': {
            'token': 'https://basescan.org/token/',
            'address': 'https://basescan.org/address/'
        },
        # Add more chains as needed
    }
    
    chain_explorers = explorers.get(chain.lower(), explorers['eth'])
    base_url = chain_explorers['token'] if is_token else chain_explorers['address']
    return f"{base_url}{address}"

def get_chain_display_name(chain_code: str) -> str:
    """
    Get a user-friendly display name for a chain code
    
    Args:
        chain_code: The blockchain network code (eth, bsc, base, etc.)
    
    Returns:
        User-friendly name for the chain
    """
    chain_names = {
        'eth': 'Ethereum',
        'bsc': 'Binance Smart Chain',
        'base': 'Base',
        'arb': 'Arbitrum',
        'op': 'Optimism',
        'poly': 'Polygon',
        'avax': 'Avalanche',
        'ftm': 'Fantom'
    }
    
    return chain_names.get(chain_code.lower(), chain_code.upper())
