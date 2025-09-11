import html
import json
import logging
import traceback
from typing import Optional

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import (
    BadRequest, ChatMigrated, Conflict, Forbidden, InvalidToken, NetworkError,
    RetryAfter, TelegramError, TimedOut
)
from telegram.ext import ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

DEVELOPER_CHAT_ID = None  # Replace with your Telegram ID for error reporting

async def error_handler(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors raised during updates processing."""
    # Log the error
    logger.error("Exception while handling an update:", exc_info=context.error)

    # Get the error traceback
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the error message
    error_message = (
        f"An exception occurred while processing an update:\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Extract update data for error reporting
    update_str = update.to_dict() if update else "No update"
    
    # Truncate the update string if it's too long
    if isinstance(update_str, str):
        if len(update_str) > 1000:
            update_str = update_str[:1000] + "..."
    else:
        update_str = json.dumps(update_str, indent=2, ensure_ascii=False)
        if len(update_str) > 1000:
            update_str = json.dumps(update_str, ensure_ascii=False)[:1000] + "..."

    # Add update data to error message
    error_message += f"\n\nUpdate: <pre>{html.escape(str(update_str))}</pre>"

    # Handle specific errors
    if isinstance(context.error, BadRequest):
        await handle_bad_request_error(update, context)
    elif isinstance(context.error, TimedOut):
        await handle_timeout_error(update, context)
    elif isinstance(context.error, NetworkError):
        await handle_network_error(update, context)
    elif isinstance(context.error, Forbidden):
        await handle_forbidden_error(update, context)
    elif isinstance(context.error, RetryAfter):
        await handle_retry_after_error(update, context)
    elif isinstance(context.error, Conflict):
        await handle_conflict_error(update, context)
    elif isinstance(context.error, ChatMigrated):
        await handle_chat_migrated_error(update, context)
    elif isinstance(context.error, InvalidToken):
        await handle_invalid_token_error(update, context)
    elif isinstance(context.error, TelegramError):
        await handle_telegram_error(update, context)
    
    # Send error message to developer if developer chat ID is set
    if DEVELOPER_CHAT_ID:
        # Split the message if it's too long
        if len(error_message) > 4000:
            parts = [error_message[i:i+4000] for i in range(0, len(error_message), 4000)]
            for part in parts:
                await context.bot.send_message(
                    chat_id=DEVELOPER_CHAT_ID,
                    text=part,
                    parse_mode=ParseMode.HTML
                )
        else:
            await context.bot.send_message(
                chat_id=DEVELOPER_CHAT_ID,
                text=error_message,
                parse_mode=ParseMode.HTML
            )

async def handle_bad_request_error(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle BadRequest errors."""
    if update and update.effective_message:
        error_message = "Sorry, I couldn't process that request. Please try again."
        
        try:
            await update.effective_message.reply_text(error_message)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

async def handle_timeout_error(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle TimedOut errors."""
    if update and update.effective_message:
        error_message = "The request timed out. Please try again later."
        
        try:
            await update.effective_message.reply_text(error_message)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

async def handle_network_error(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle NetworkError errors."""
    if update and update.effective_message:
        error_message = "A network error occurred. Please try again later."
        
        try:
            await update.effective_message.reply_text(error_message)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

async def handle_forbidden_error(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Forbidden errors."""
    if update and update.effective_message:
        error_message = "I don't have permission to perform this action."
        
        try:
            await update.effective_message.reply_text(error_message)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

async def handle_retry_after_error(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle RetryAfter errors."""
    # Extract retry after time
    retry_after = context.error.retry_after if hasattr(context.error, 'retry_after') else 30
    
    if update and update.effective_message:
        error_message = f"Too many requests. Please try again after {retry_after} seconds."
        
        try:
            await update.effective_message.reply_text(error_message)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

async def handle_conflict_error(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Conflict errors."""
    if update and update.effective_message:
        error_message = "A conflict occurred. Please try again later."
        
        try:
            await update.effective_message.reply_text(error_message)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

async def handle_chat_migrated_error(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle ChatMigrated errors."""
    # This error occurs when a group is migrated to a supergroup
    # We can extract the new chat id from the error
    new_chat_id = context.error.new_chat_id if hasattr(context.error, 'new_chat_id') else None
    
    logger.info(f"Chat migrated to {new_chat_id}")
    
    # No user-facing message needed for this error

async def handle_invalid_token_error(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle InvalidToken errors."""
    logger.critical("Invalid bot token provided!")
    
    # This is a critical error, no user-facing message can be sent

async def handle_telegram_error(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle generic TelegramError errors."""
    if update and update.effective_message:
        error_message = "An error occurred while processing your request. Please try again later."
        
        try:
            await update.effective_message.reply_text(error_message)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")
