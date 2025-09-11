import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from models import User

from utils import (
    format_number,
    format_currency,
    get_token_info,
    format_new_token_pumpfun_response
)

from services.blockchain_service import (
    is_valid_address,
    is_valid_token_contract,
    is_valid_wallet_address
)

from services.user_service import (
    get_or_create_user,
    check_rate_limit,
    increment_scan_count
)

from database import *


async def get_current_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> User:
    user = get_user(update.effective_chat.id)
    if not user:
        user = await get_or_create_user(
            user_id=update.effective_chat.id,
            user_type=update.effective_chat.type,
            username=update.effective_user.username if update.effective_chat.type == "private" else update.effective_chat.title,
        )
    return user

async def handle_expected_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text input based on the expected input state"""
    # This handler is kept for backward compatibility
    # It will be used less as we move to command-based interactions
    pass

async def handle_start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    await get_or_create_user(
        user_id=update.effective_chat.id,
        user_type=update.effective_chat.type,
        username=update.effective_user.username if update.effective_chat.type == "private" else update.effective_chat.title,
    )
    
    # Set default network if not set
    if "default_network" not in context.user_data:
        context.user_data["default_network"] = "eth"
    
    await update.message.reply_text(
        f"🚀 <b>Welcome to the DeFiScope Bot!</b>\n\n"
        f"👋 Hello {update.effective_user.first_name}! I'm your AI-powered assistant for blockchain analytics and DeFi research.\n\n"
        f"🔍 <b>What I can do for you:</b>\n"
        f"• 📊 Analyze token metrics and whale activity\n"
        f"• 💰 Track profitable wallets and trading patterns\n"
        f"• 🧠 Monitor deployer wallets and new token launches\n"
        f"• ⚠️ Alert you about suspicious token activity\n"
        f"• 🐳 Provide insights on high net worth holders\n\n"
        f"🔔 <b>PumpFun Token Notifications:</b>\n"
        f"• Use /start_notifications to begin receiving alerts\n"
        f"• Use /stop_notifications to stop receiving alerts\n"
        f"• Use /notifications to manage your subscription\n\n"
        f"🏁 <b>Getting Started:</b>\n"
        f"• 🔎 Try /scan [address] to get insight into a token\n"
        f"• 🔍 Use /check_tokens to manually check for new tokens\n"
        f"• 📱 Use /notifications to manage your alerts\n\n"
        f"✨ Start exploring the DeFi ecosystem with powerful on-chain analytics!",
        parse_mode=ParseMode.HTML
    )

