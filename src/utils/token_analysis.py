import asyncio
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta

from solana.rpc.api import Client as SolanaClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from models import User
from services.blockchain_service import is_valid_token_contract, get_web3_provider
from services.user_service import get_user, increment_scan_count
from utils.formatting import format_number

async def handle_token_analysis_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    analysis_type: str,
    get_data_func,
    format_response_func,
    scan_count_type: str,
    processing_message_text: str,
    error_message_text: str,
    no_data_message_text: str
) -> None:
    """
    Generic handler for token analysis inputs
    
    Args:
        update: The update object
        context: The context object
        analysis_type: Type of analysis being performed (for logging)
        get_data_func: Function to get the data (takes token_address and chain)
        format_response_func: Function to format the response (takes data and token_data)
        scan_count_type: Type of scan to increment count for
        processing_message_text: Text to show while processing
        error_message_text: Text to show on error
        no_data_message_text: Text to show when no data is found
    """
    token_address = update.message.text.strip()
    selected_chain = context.user_data.get("default_network")
    
    # Validate address
    if not await is_valid_token_contract(token_address, selected_chain):
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="token_analysis")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"⚠️ Something went wrong.⚠️ Please provide a valid token contract address for {selected_chain}.",
            reply_markup=reply_markup
        )
        return
    
    # Send processing message
    processing_message = await update.message.reply_text(processing_message_text)
    
    try:
        # Get data
        token_info = await get_token_info(token_address, selected_chain)
        data = await get_data_func(token_address, selected_chain)
        
        if not data or not token_info:
            # Add back button when no data is found
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="token_analysis")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await processing_message.edit_text(
                no_data_message_text,
                reply_markup=reply_markup
            )
            return
        
        # Format the response
        response, keyboard = format_response_func(data, token_info, token_address)

        if analysis_type == "top_holders":
            keyboard.insert(0,[InlineKeyboardButton("🔔 Track Whale & Top Holder Sells", callback_data=f"setup_tracking_{token_address}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        success = False
        try:
            # Try to edit the current message
            await processing_message.edit_text(
                response,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
            success = True
        except Exception as e:
            logging.error(f"Error in handle_{analysis_type}: {e}")
            # If editing fails, send a new message
            await update.message.reply_text(
                response,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
            success = True
            # Delete the original message if possible
            try:
                await processing_message.delete()
            except:
                pass
        
        # Only increment scan count if we successfully displayed data
        if success:
            # Get the user directly from the message update
            user_id = update.effective_user.id
            user = get_user(user_id)
            if not user:
                # Create user if not exists
                user = User(user_id=user_id, username=update.effective_user.username)
                # Save user to database if needed
            
            await increment_scan_count(user_id, scan_count_type)
    
    except Exception as e:
        logging.error(f"Error in handle_expected_input ({analysis_type}): {e}")
        
        # Add back button to exception error message
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="token_analysis")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await processing_message.edit_text(
            error_message_text,
            reply_markup=reply_markup
        )


async def get_token_info(token_address: str, chain: str = "eth") -> Optional[Dict[str, Any]]:
    """Get detailed information about a token"""
    if not await is_valid_token_contract(token_address, chain):
        return None
    
    try:
        # Get the appropriate web3 provider based on chain
        w3 = get_web3_provider(chain)
        
        # Handle Solana tokens differently
        if chain.lower() == "sol":
            try:
                pubkey = Pubkey.from_string(token_address)
                # For Solana, we need to fetch token info differently
                account_info = w3.get_account_info(pubkey)
                
                if not account_info.value:
                    return None
                
                # In a real implementation, you would parse the account data
                # to extract token metadata. For now, we'll return placeholder data
                return {
                    "address": token_address,
                    "name": f"Solana Token {token_address[:6]}",  # Placeholder
                    "symbol": f"SOL{token_address[:3]}",  # Placeholder
                    "decimals": 9,  # Common for Solana tokens
                    "total_supply": 0  # Placeholder
                }
            except Exception as e:
                logging.error(f"Error getting Solana token info: {e}")
                return None
        else:
            # ERC20 ABI for basic token information
            abi = [
                {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
            ]
            
            # Create contract instance
            checksum_address = w3.to_checksum_address(token_address)
            contract = w3.eth.contract(address=checksum_address, abi=abi)
            
            # Get basic token information
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            decimals = contract.functions.decimals().call()
            total_supply = contract.functions.totalSupply().call() / (10 ** decimals)
            
            # Return token info
            return {
                "address": token_address,
                "name": name,
                "symbol": symbol,
                "decimals": decimals,
                "total_supply": total_supply
            }
    except Exception as e:
        logging.error(f"Error getting token info on {chain}: {e}")
        return None

import asyncio

async def get_token_info_v2(token_address: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a token by checking multiple chains in parallel
    
    Args:
        token_address: The token contract address
        
    Returns:
        Dictionary with token information including the chain, or None if not found
    """
    # List of chains to try
    chains = ["eth", "base", "bsc", "sol"]
    
    # Create tasks for all chains to check in parallel
    tasks = [check_token_on_chain(token_address, chain) for chain in chains]
    
    # Run all tasks concurrently and get the first valid result
    results = await asyncio.gather(*tasks)
    
    # Return the first non-None result (if any)
    for result in results:
        if result:
            return result
    
    # If we reach here, the token wasn't found on any chain
    return None

async def check_token_on_chain(token_address: str, chain: str) -> Optional[Dict[str, Any]]:
    """Helper function to check a token on a specific chain"""
    try:
        # Check if it's a valid token contract on this chain
        if not await is_valid_token_contract(token_address, chain):
            return None
        
        # Get the appropriate web3 provider based on chain
        w3 = get_web3_provider(chain)
        
        # Handle Solana tokens differently
        if chain.lower() == "sol":
            try:
                pubkey = Pubkey.from_string(token_address)
                # For Solana, we need to fetch token info differently
                # This is a simplified version - in a real implementation, 
                # you would use the Solana token program to get metadata
                account_info = w3.get_account_info(pubkey)
                
                if not account_info.value:
                    return None
                
                # In a real implementation, you would parse the account data
                # to extract token metadata. For now, we'll return placeholder data
                return {
                    "address": token_address,
                    "name": f"Solana Token {token_address[:6]}",  # Placeholder
                    "symbol": f"SOL{token_address[:3]}",  # Placeholder
                    "decimals": 9,  # Common for Solana tokens
                    "total_supply": 0,  # Placeholder
                    "chain": chain
                }
            except Exception as e:
                logging.error(f"Error getting Solana token info: {e}")
                return None
        else:
            # ERC20 ABI for basic token information
            abi = [
                {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
            ]
            
            # Create contract instance
            checksum_address = w3.to_checksum_address(token_address)
            contract = w3.eth.contract(address=checksum_address, abi=abi)
            
            # Get basic token information
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            decimals = contract.functions.decimals().call()
            total_supply = contract.functions.totalSupply().call() / (10 ** decimals)
            
            # Return token info with chain information
            return {
                "address": token_address,
                "name": name,
                "symbol": symbol,
                "decimals": decimals,
                "total_supply": total_supply,
                "chain": chain
            }
    except Exception as e:
        logging.error(f"Error getting token info on {chain}: {e}")
        return None
    
def format_first_buyers_response(data: Tuple[Dict[str, Any], List[Dict[str, Any]]], 
                                token_data: Dict[str, Any], 
                                token_address: str) -> Tuple[str, List[List[InlineKeyboardButton]]]:
    """
    Format the response for first buyers analysis
    
    Args:
        data: Tuple of (deployer_info, first_buyers)
        token_data: Token information
        token_address: The token address
        
    Returns:
        Tuple of (formatted response text, keyboard buttons)
    """
    # Unpack the data tuple
    deployer_info, first_buyers = data
    
    # Format the deployer information
    deployer_address = deployer_info.get('address', 'Unknown')
    deployment_time = deployer_info.get('time_readable', 'Unknown')
    deployment_tx = deployer_info.get('tx_hash', 'Unknown')
    deployment_tx_display = f"<a href='{get_explorer_url('eth', deployment_tx)}'>{deployment_tx[:10]}...{deployment_tx[-10:]}</a>" if deployment_tx != 'Unknown' else 'Unknown'
    
    response = (
        f"🛒 <b>First Buyers Analysis for {token_data.get('name', 'Unknown Token')} ({token_data.get('symbol', 'N/A')})</b>\n\n"
        f"📝 <code>{token_address}</code>\n\n"
        f"👨‍💻 <b>Deployer:</b>\n"
        f"• 💼 <code>{deployer_address}</code>\n"
        f"• 📅 {deployment_time}\n"
        f"• 📡 {deployment_tx_display}\n\n"
        f"🔍 <b>First Buyers:</b>\n\n"
    )
    
    for i, buyer in enumerate(first_buyers[:10], 1):
        # Format wallet address
        address = buyer.get('address', 'Unknown')
        
        # Format buy amount and value
        base_amount = buyer.get('base_amount', 'N/A')
        amount_usd = buyer.get('amount_usd', 'N/A')
        
        # Format buy time
        buy_time = buyer.get('time_readable', 'N/A')
        
        # Format profit metrics
        total_profit = buyer.get('total_profit', 0)
        realized_profit = buyer.get('realized_profit', 0)
        unrealized_profit = buyer.get('unrealized_profit', 0)
        
        # Format trade statistics
        buy_trades = buyer.get('buy', 0)
        sell_trades = buyer.get('sell', 0)
        total_trades = buyer.get('total_trades', 0)
        
        # Format win rate
        win_rate = buyer.get('winrate', 0)
        win_rate_percent = f"{win_rate * 100:.1f}%" if isinstance(win_rate, (int, float)) else "N/A"
        
        # Format last active time
        last_active = buyer.get('last_active_timestamp', 0)
        last_active_display = "N/A"
        if last_active > 0:
            try:
                last_active_date = datetime.fromtimestamp(last_active)
                last_active_display = last_active_date.strftime("%Y-%m-%d %H:%M:%S")
            except:
                last_active_display = "N/A"
        
        response += (
            f"{i}. <code>{address}</code>\n"
            f"   🛒 Buy Amount: {base_amount} | {amount_usd}\n"
            f"   🕒 Buy Time: {buy_time}\n"
            f"   📊 Trades: {total_trades} (B: {buy_trades} / S: {sell_trades})\n"
            f"   📈 Profit: {total_profit} (R: {realized_profit} / U: {unrealized_profit})\n"
            f"   🏆 Win Rate: {win_rate_percent}\n"
            f"   ⏱️ Last Active: {last_active_display}\n\n"
        )
    
    # Create action buttons similar to token scan
    keyboard = [
        [
            InlineKeyboardButton("Profitable Wallets", callback_data=f"profitable_wallets_{token_address}"),
            InlineKeyboardButton("Deployer", callback_data=f"deployer_wallet_{token_address}")
        ],
        [
            InlineKeyboardButton("Top Holders", callback_data=f"top_holders_{token_address}"),
            InlineKeyboardButton("High Net Worth Wallets", callback_data=f"high_net_worth_{token_address}"),
        ]
    ]
    
    return response, keyboard

def format_new_token_pumpfun_response(data: Tuple[Dict[str, Any], List[Dict[str, Any]]]) -> Tuple[str, List[List[InlineKeyboardButton]]]:
    """
    Format the response for new token pumpfun analysis
    """
    return response, keyboard


# Helper function to get explorer URL based on chain and token address
def get_explorer_url(chain: str, token_address: str) -> str:
    """Get explorer URL for a token based on chain"""
    explorers = {
        'eth': 'https://etherscan.io/token/',
        'bsc': 'https://bscscan.com/token/',
        'base': 'https://basescan.org/token/',
        'sol': 'https://solscan.io/token/'
        # Add more chains as needed
    }
    
    base_url = explorers.get(chain.lower(), 'https://etherscan.io/token/')
    return f"{base_url}{token_address}"
