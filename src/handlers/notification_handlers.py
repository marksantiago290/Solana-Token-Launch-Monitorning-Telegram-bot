"""
Handlers for notification-related commands and callbacks.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode

from services.notification_service import notification_service
from services.scheduler_service import scheduler_service

logger = logging.getLogger(__name__)

async def handle_notifications_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /notifications command to manage notification subscriptions"""
    try:
        user_id = update.effective_user.id
        
        # Check if user is already subscribed
        is_subscribed = await notification_service.is_user_subscribed(user_id)
        
        if is_subscribed:
            # User is subscribed, show unsubscribe option
            keyboard = [
                [InlineKeyboardButton("🔕 Unsubscribe from PumpFun Alerts", callback_data="unsubscribe_pumpfun")],
                [InlineKeyboardButton("ℹ️ Notification Info", callback_data="notification_info")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = """
🔔 <b>Notification Settings</b>

✅ You are currently subscribed to PumpFun new token alerts.

You'll receive notifications when new tokens are launched on PumpFun with:
• Token details and pricing
• Trading activity metrics
• Risk assessment indicators
• Direct analysis links

Click below to manage your subscription:
            """.strip()
        else:
            # User is not subscribed, show subscribe option
            keyboard = [
                [InlineKeyboardButton("🔔 Subscribe to PumpFun Alerts", callback_data="subscribe_pumpfun")],
                [InlineKeyboardButton("ℹ️ Learn More", callback_data="notification_info")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = """
🔔 <b>Notification Settings</b>

❌ You are not currently subscribed to any notifications.

Get instant alerts for new PumpFun token launches with:
• Real-time price and market cap data
• Trading volume and holder statistics
• Risk indicators and security analysis
• Direct links to analyze tokens

Click below to subscribe:
            """.strip()
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error handling notifications command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while processing your request. Please try again later."
        )

async def handle_subscribe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle subscribe callback"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        success = await notification_service.subscribe_user(user_id)
        
        if success:
            await query.edit_message_text(
                "✅ <b>Successfully subscribed!</b>\n\n"
                "You'll now receive notifications for new PumpFun token launches.\n\n"
                "Use /notifications to manage your subscription anytime.",
                parse_mode=ParseMode.HTML
            )
        else:
            await query.edit_message_text(
                "❌ Failed to subscribe. Please try again later.",
                parse_mode=ParseMode.HTML
            )
            
    except Exception as e:
        logger.error(f"Error handling subscribe callback: {e}")
        await query.edit_message_text(
            "❌ An error occurred. Please try again later.",
            parse_mode=ParseMode.HTML
        )

async def handle_unsubscribe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unsubscribe callback"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        success = await notification_service.unsubscribe_user(user_id)
        
        if success:
            await query.edit_message_text(
                "🔕 <b>Successfully unsubscribed!</b>\n\n"
                "You will no longer receive PumpFun token notifications.\n\n"
                "Use /notifications to subscribe again anytime.",
                parse_mode=ParseMode.HTML
            )
        else:
            await query.edit_message_text(
                "❌ Failed to unsubscribe. Please try again later.",
                parse_mode=ParseMode.HTML
            )
            
    except Exception as e:
        logger.error(f"Error handling unsubscribe callback: {e}")
        await query.edit_message_text(
            "❌ An error occurred. Please try again later.",
            parse_mode=ParseMode.HTML
        )

async def handle_notification_info_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle notification info callback"""
    try:
        query = update.callback_query
        await query.answer()
        
        info_message = """
ℹ️ <b>About PumpFun Notifications</b>

🚀 <b>What you'll receive:</b>
• Instant alerts for new token launches
• Real-time price and market cap data
• Trading volume and holder statistics
• Risk assessment indicators
• Direct analysis links

⏰ <b>Frequency:</b>
• Notifications are sent every minute when new tokens are detected
• Only truly new tokens (not seen before) trigger alerts
• No spam - each token is only notified once

🛡️ <b>Risk Indicators:</b>
• Wash trading detection
• Sniper bot activity
• Holder concentration analysis
• Creator balance monitoring

🔍 <b>Analysis Features:</b>
• Use /scan [token_address] to analyze any token
• Get detailed holder and trading information
• Track whale activity and market movements

💡 <b>Pro Tip:</b> Combine notifications with our analysis tools for the best trading insights!
        """.strip()
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Settings", callback_data="back_to_notifications")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            info_message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error handling notification info callback: {e}")
        await query.edit_message_text(
            "❌ An error occurred. Please try again later.",
            parse_mode=ParseMode.HTML
        )

async def handle_back_to_notifications_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle back to notifications callback"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        is_subscribed = await notification_service.is_user_subscribed(user_id)
        
        if is_subscribed:
            keyboard = [
                [InlineKeyboardButton("🔕 Unsubscribe from PumpFun Alerts", callback_data="unsubscribe_pumpfun")],
                [InlineKeyboardButton("ℹ️ Notification Info", callback_data="notification_info")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = """
🔔 <b>Notification Settings</b>

✅ You are currently subscribed to PumpFun new token alerts.

You'll receive notifications when new tokens are launched on PumpFun with:
• Token details and pricing
• Trading activity metrics
• Risk assessment indicators
• Direct analysis links

Click below to manage your subscription:
            """.strip()
        else:
            keyboard = [
                [InlineKeyboardButton("🔔 Subscribe to PumpFun Alerts", callback_data="subscribe_pumpfun")],
                [InlineKeyboardButton("ℹ️ Learn More", callback_data="notification_info")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = """
🔔 <b>Notification Settings</b>

❌ You are not currently subscribed to any notifications.

Get instant alerts for new PumpFun token launches with:
• Real-time price and market cap data
• Trading volume and holder statistics
• Risk indicators and security analysis
• Direct links to analyze tokens

Click below to subscribe:
            """.strip()
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error handling back to notifications callback: {e}")
        await query.edit_message_text(
            "❌ An error occurred. Please try again later.",
            parse_mode=ParseMode.HTML
        )

async def handle_start_notifications_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start_notifications command"""
    try:
        user_id = update.effective_user.id
        success = await notification_service.subscribe_user(user_id)
        
        if success:
            await update.message.reply_text(
                "✅ <b>Notifications Started!</b>\n\n"
                "You'll now receive real-time alerts for new PumpFun token launches.\n\n"
                "🔔 <b>What you'll get:</b>\n"
                "• Instant alerts for new token launches\n"
                "• Price, volume, and holder data\n"
                "• Risk indicators and security analysis\n"
                "• Direct analysis links\n\n"
                "Use /stop_notifications to stop receiving alerts anytime.",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                "❌ Failed to start notifications. Please try again later.",
                parse_mode=ParseMode.HTML
            )
            
    except Exception as e:
        logger.error(f"Error handling start notifications command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while starting notifications. Please try again later."
        )

async def handle_stop_notifications_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stop_notifications command"""
    try:
        user_id = update.effective_user.id
        success = await notification_service.unsubscribe_user(user_id)
        
        if success:
            await update.message.reply_text(
                "🔕 <b>Notifications Stopped!</b>\n\n"
                "You will no longer receive PumpFun token notifications.\n\n"
                "Use /start_notifications to begin receiving alerts again anytime.",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                "❌ Failed to stop notifications. Please try again later.",
                parse_mode=ParseMode.HTML
            )
            
    except Exception as e:
        logger.error(f"Error handling stop notifications command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while stopping notifications. Please try again later."
        )

async def handle_check_tokens_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /check_tokens command for manual testing"""
    try:
        # Check if user is admin (you can modify this logic as needed)
        user_id = update.effective_user.id
        # For now, allow any user to trigger a check for testing
        
        await update.message.reply_text("🔍 Checking for new PumpFun tokens...")
        
        # Run a single check
        result = await scheduler_service.run_single_check()
        
        if result["success"]:
            message = f"""
✅ <b>Token Check Completed</b>

📊 <b>Results:</b>
• New tokens found: {result['new_tokens_found']}
• Execution time: {result['execution_time']:.2f}s
• Timestamp: {result['timestamp']}

{'🎉 New tokens detected and notifications sent!' if result['new_tokens_found'] > 0 else 'ℹ️ No new tokens found this time.'}
            """.strip()
        else:
            message = f"""
❌ <b>Token Check Failed</b>

Error: {result.get('error', 'Unknown error')}
Timestamp: {result['timestamp']}
            """.strip()
        
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)
        
    except Exception as e:
        logger.error(f"Error handling check tokens command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while checking for tokens. Please try again later."
        )

async def handle_clear_cache_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /clear_cache command for testing"""
    try:
        user_id = update.effective_user.id
        
        # Get current counts
        memory_count = notification_service.get_seen_tokens_count()
        db_count = notification_service.get_database_tokens_count()
        notified_count = notification_service.get_notified_tokens_count()
        
        # Clear everything
        cleared_count = notification_service.clear_all_tokens()
        
        await update.message.reply_text(
            f"🧹 <b>All Tokens Cleared!</b>\n\n"
            f"📊 <b>Before clearing:</b>\n"
            f"• Memory cache: {memory_count} tokens\n"
            f"• Database: {db_count} tokens\n"
            f"• Notified: {notified_count} tokens\n\n"
            f"✅ <b>Cleared:</b> {cleared_count} tokens from database\n"
            f"✅ Memory cache cleared\n\n"
            f"The next token check will treat all tokens as completely new.\n\n"
            f"Use /check_tokens to test the system.",
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Error handling clear cache command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while clearing the cache. Please try again later."
        )

async def handle_reset_time_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /reset_time command for testing"""
    try:
        user_id = update.effective_user.id
        
        # Reset notification time
        notification_service.reset_notification_time()
        
        await update.message.reply_text(
            f"⏰ <b>Notification Time Reset!</b>\n\n"
            f"🔄 Reset notification time to 1 hour ago\n"
            f"✅ Next check will find recent tokens for notification",
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Error handling reset time command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while resetting time. Please try again later."
        )

async def handle_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command to show system status"""
    try:
        user_id = update.effective_user.id
        
        # Get current counts
        memory_count = notification_service.get_seen_tokens_count()
        db_count = notification_service.get_database_tokens_count()
        notified_count = notification_service.get_notified_tokens_count()
        
        # Check if user is subscribed
        is_subscribed = await notification_service.is_user_subscribed(user_id)
        
        # Get scheduler status
        scheduler_status = scheduler_service.get_status()
        
        await update.message.reply_text(
            f"📊 <b>System Status</b>\n\n"
            f"🔔 <b>Your Notifications:</b>\n"
            f"• Status: {'✅ Subscribed' if is_subscribed else '❌ Not subscribed'}\n\n"
            f"📈 <b>Token Tracking:</b>\n"
            f"• Memory cache: {memory_count} tokens\n"
            f"• Database: {db_count} tokens\n"
            f"• Notified: {notified_count} tokens\n\n"
            f"⚙️ <b>Monitoring:</b>\n"
            f"• Status: {'🟢 Running' if scheduler_status['is_running'] else '🔴 Stopped'}\n"
            f"• Check interval: {scheduler_status['check_interval']}s\n"
            f"• Task running: {'✅ Yes' if scheduler_status['task_running'] else '❌ No'}\n\n"
            f"💡 <b>Commands:</b>\n"
            f"• /start_notifications - Subscribe to alerts\n"
            f"• /stop_notifications - Unsubscribe\n"
            f"• /check_tokens - Manual check\n"
            f"• /clear_cache - Reset all tokens\n"
            f"• /reset_time - Reset notification time",
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Error handling status command: {e}")
        await update.message.reply_text(
            "❌ An error occurred while getting status. Please try again later."
        )

def register_notification_handlers(application):
    """Register all notification-related handlers"""
    # Command handlers
    application.add_handler(CommandHandler("notifications", handle_notifications_command))
    application.add_handler(CommandHandler("start_notifications", handle_start_notifications_command))
    application.add_handler(CommandHandler("stop_notifications", handle_stop_notifications_command))
    application.add_handler(CommandHandler("check_tokens", handle_check_tokens_command))
    application.add_handler(CommandHandler("clear_cache", handle_clear_cache_command))
    application.add_handler(CommandHandler("reset_time", handle_reset_time_command))
    application.add_handler(CommandHandler("status", handle_status_command))
    
    # Callback handlers
    from telegram.ext import CallbackQueryHandler
    
    application.add_handler(CallbackQueryHandler(
        handle_subscribe_callback,
        pattern='^subscribe_pumpfun$'
    ))
    
    application.add_handler(CallbackQueryHandler(
        handle_unsubscribe_callback,
        pattern='^unsubscribe_pumpfun$'
    ))
    
    application.add_handler(CallbackQueryHandler(
        handle_notification_info_callback,
        pattern='^notification_info$'
    ))
    
    application.add_handler(CallbackQueryHandler(
        handle_back_to_notifications_callback,
        pattern='^back_to_notifications$'
    ))
