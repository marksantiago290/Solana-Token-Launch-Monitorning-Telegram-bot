"""
Notification service for monitoring new PumpFun tokens and sending alerts to users.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
from telegram import Bot
from telegram.error import TelegramError

from api.token_api import fetch_new_token_pumpfun
from models.token_models import PumpFunToken
from database import get_database
from config.settings import TELEGRAM_TOKEN
from utils.formatting import format_currency, format_number

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for handling PumpFun token notifications"""
    
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_TOKEN)
        self.db = get_database()
        self.last_check_time = datetime.now()
        # Initialize to 1 hour ago to catch recent tokens on first run
        self.last_notification_time = datetime.now() - timedelta(hours=1)
    
    async def check_for_new_tokens(self) -> List[Dict[str, Any]]:
        """
        Check for new PumpFun tokens and return new ones that need notifications.
        Time-based logic: only notify about tokens created since last notification time.
        
        Returns:
            List[Dict]: List of new tokens that need notifications
        """
        try:
            logger.info("Checking for new PumpFun tokens...")
            
            # Fetch latest tokens from API
            response = await fetch_new_token_pumpfun()
            
            if not response or "error" in response:
                logger.error(f"Error fetching new tokens: {response}")
                return []
            
            # Ensure response is a list
            if not isinstance(response, list):
                logger.error(f"Unexpected response format: {type(response)}")
                return []
            
            logger.info(f"Received {len(response)} tokens from API")
            logger.info(f"Last notification time: {self.last_notification_time.strftime('%H:%M:%S')}")
            
            new_tokens = []
            current_time = datetime.now()
            
            # Sort tokens by created_timestamp in descending order (newest first)
            sorted_tokens = sorted(response, key=lambda x: x.get("created_timestamp", 0), reverse=True)
            
            for token_data in sorted_tokens:
                token_address = token_data.get("token_address", "")
                
                if not token_address:
                    logger.warning("Token data missing token_address, skipping")
                    continue
                
                logger.info(f"Processing token: {token_data.get('symbol', 'Unknown')} ({token_address})")
                
                # Check if token was created after our last notification time
                created_timestamp = token_data.get("created_timestamp", 0)
                if created_timestamp:
                    try:
                        created_time = datetime.fromtimestamp(created_timestamp)
                        
                        # Debug logging
                        logger.info(f"Token {token_address} created: {created_time.strftime('%H:%M:%S')}, last notification: {self.last_notification_time.strftime('%H:%M:%S')}")
                        
                        # Only notify about tokens created after last notification time
                        if created_time <= self.last_notification_time:
                            logger.info(f"Token {token_address} was created before last notification time, skipping")
                            continue
                        
                        logger.info(f"Token {token_address} is NEW (created {created_time.strftime('%H:%M:%S')}), will notify")
                        
                    except (ValueError, OSError):
                        logger.warning(f"Invalid timestamp for token {token_address}, skipping")
                        continue
                else:
                    logger.warning(f"No timestamp for token {token_address}, skipping")
                    continue
                
                # Save token to database (for tracking purposes)
                pumpfun_token = PumpFunToken(
                    token_address=token_address,
                    symbol=token_data.get("symbol"),
                    name=token_data.get("name"),
                    logo=token_data.get("logo"),
                    thumbnail=token_data.get("thumbnail"),
                    decimals=token_data.get("decimals"),
                    usd_price=token_data.get("usd_price"),
                    usd_market_cap=token_data.get("usd_market_cap"),
                    usd_price_24hr_percent_change=token_data.get("usd_price_24hr_percent_change"),
                    usd_price_5m_percent_change=token_data.get("usd_price_5m_percent_change"),
                    volume_1h=token_data.get("volume_1h"),
                    volume_24h=token_data.get("volume_24h"),
                    swaps_1h=token_data.get("swaps_1h"),
                    swaps_24h=token_data.get("swaps_24h"),
                    total_supply=token_data.get("total_supply"),
                    holder_count=token_data.get("holder_count"),
                    progress=token_data.get("progress"),
                    creator=token_data.get("creator"),
                    creator_balance_rate=token_data.get("creator_balance_rate"),
                    creator_token_status=token_data.get("creator_token_status"),
                    created_timestamp=token_data.get("created_timestamp"),
                    last_trade_timestamp=token_data.get("last_trade_timestamp"),
                    twitter=token_data.get("twitter"),
                    website=token_data.get("website"),
                    telegram=token_data.get("telegram"),
                    is_wash_trading=token_data.get("is_wash_trading"),
                    top_10_holder_rate=token_data.get("top_10_holder_rate"),
                    sniper_count=token_data.get("sniper_count"),
                    smart_degen_count=token_data.get("smart_degen_count"),
                    possible_spam=token_data.get("possible_spam"),
                    verified_contract=token_data.get("verified_contract"),
                    native_token=token_data.get("native_token"),
                    first_seen=current_time,
                    notification_sent=True
                )
                
                # Save to database (upsert to avoid duplicates)
                await self._save_token_upsert(pumpfun_token)
                
                # Add to new tokens list for notification
                new_tokens.append(token_data)
                logger.info(f"New token for notification: {token_data.get('symbol', 'Unknown')} ({token_address})")
            
            # Update last notification time to current time
            self.last_notification_time = current_time
            
            self.last_check_time = current_time
            logger.info(f"Processing complete: {len(response)} total tokens, {len(new_tokens)} new tokens for notification")
            
            return new_tokens
            
        except Exception as e:
            logger.error(f"Error checking for new tokens: {e}")
            return []
    
    async def _save_token(self, token: PumpFunToken) -> bool:
        """Save a token to the database"""
        try:
            logger.info(f"Saving token {token.token_address} to database...")
            token_dict = token.to_dict()
            result = self.db.pumpfun_tokens.insert_one(token_dict)
            logger.info(f"Token {token.token_address} saved with ID: {result.inserted_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving token {token.token_address}: {e}")
            return False
    
    async def _save_token_upsert(self, token: PumpFunToken) -> bool:
        """Save or update a token in the database (upsert)"""
        try:
            logger.info(f"Upserting token {token.token_address} to database...")
            token_dict = token.to_dict()
            result = self.db.pumpfun_tokens.update_one(
                {"token_address": token.token_address},
                {"$set": token_dict},
                upsert=True
            )
            if result.upserted_id:
                logger.info(f"Token {token.token_address} inserted with ID: {result.upserted_id}")
            else:
                logger.info(f"Token {token.token_address} updated")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting token {token.token_address}: {e}")
            return False
    
    async def send_notifications(self, new_tokens: List[Dict[str, Any]]) -> None:
        """
        Send notifications to subscribed users about new tokens.
        
        Args:
            new_tokens: List of new token data to notify about
        """
        if not new_tokens:
            return
        
        try:
            # Get all active subscribers
            subscribers = self._get_active_subscribers()
            
            if not subscribers:
                logger.info("No active subscribers found")
                return
            
            logger.info(f"Sending notifications to {len(subscribers)} subscribers for {len(new_tokens)} new tokens")
            
            # Sort new tokens by created_timestamp in descending order (newest first) for notifications
            sorted_new_tokens = sorted(new_tokens, key=lambda x: x.get("created_timestamp", 0))
            
            for i, token_data in enumerate(sorted_new_tokens, 1):
                created_time = token_data.get("created_timestamp", 0)
                if created_time:
                    try:
                        created_dt = datetime.fromtimestamp(created_time)
                        time_str = created_dt.strftime('%H:%M:%S')
                    except (ValueError, OSError):
                        time_str = "Unknown"
                else:
                    time_str = "Unknown"
                logger.info(f"  {i}. {token_data.get('symbol', 'Unknown')} - Created: {time_str}")
            
            # Send notifications for each new token in chronological order
            for token_data in sorted_new_tokens:
                await self._send_token_notification(token_data, subscribers)
                
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
    
    def _get_active_subscribers(self) -> List[int]:
        """Get list of active notification subscribers"""
        try:
            subscribers = self.db.notification_subscriptions.find({
                "is_active": True,
                "subscription_type": "pumpfun_new_tokens"
            })
            
            return [sub["user_id"] for sub in subscribers]
            
        except Exception as e:
            logger.error(f"Error getting active subscribers: {e}")
            return []
    
    async def _send_token_notification(self, token_data: Dict[str, Any], subscribers: List[int]) -> None:
        """Send notification about a specific token to all subscribers"""
        try:
            message = self._format_token_notification(token_data)
            
            # Send to all subscribers
            for user_id in subscribers:
                try:
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='HTML',
                        disable_web_page_preview=True
                    )
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.1)
                    
                except TelegramError as e:
                    logger.error(f"Error sending notification to user {user_id}: {e}")
                    # If user blocked the bot, deactivate their subscription
                    if "blocked" in str(e).lower() or "forbidden" in str(e).lower():
                        await self._deactivate_subscription(user_id)
                        
        except Exception as e:
            logger.error(f"Error sending token notification: {e}")
    
    def _format_token_notification(self, token_data: Dict[str, Any]) -> str:
        """Format token data into a notification message"""
        try:
            symbol = token_data.get("symbol", "Unknown")
            name = token_data.get("name", "Unknown Token")
            token_address = token_data.get("token_address", "")
            price = token_data.get("usd_price", 0)
            market_cap = token_data.get("usd_market_cap", 0)
            price_change_5m = token_data.get("usd_price_5m_percent_change", 0)
            volume_1h = token_data.get("volume_1h", 0)
            holder_count = token_data.get("holder_count", 0)
            swaps_1h = token_data.get("swaps_1h", 0)
            progress = token_data.get("progress", 0)
            creator = token_data.get("creator", "") if token_data.get("creator") else "Unknown"
            is_wash_trading = token_data.get("is_wash_trading", False)
            sniper_count = token_data.get("sniper_count", 0)
            created_timestamp = token_data.get("created_timestamp", 0)
            
            # Format price change with color
            if price_change_5m > 0:
                price_change_text = f"🟢 +{price_change_5m:.2f}%"
            elif price_change_5m < 0:
                price_change_text = f"🔴 {price_change_5m:.2f}%"
            else:
                price_change_text = f"⚪ {price_change_5m:.2f}%"
            
            # Risk indicators
            risk_indicators = []
            if is_wash_trading:
                risk_indicators.append("⚠️ Wash Trading")
            if sniper_count > 10:
                risk_indicators.append(f"🎯 {sniper_count} Snipers")
            
            risk_text = " | ".join(risk_indicators) if risk_indicators else "✅ Low Risk"
            
            # Format created time
            if created_timestamp:
                try:
                    created_time = datetime.fromtimestamp(created_timestamp)
                    created_time_str = created_time.strftime('%Y-%m-%d %H:%M:%S UTC')
                except (ValueError, OSError):
                    created_time_str = "Unknown"
            else:
                created_time_str = "Unknown"
            
            message = f"""
🚀 <b>NEW PUMPFUN TOKEN DETECTED!</b>

💰 <b>{symbol}</b> ({name})
📍 Address: <code>{token_address}</code>

📊 <b>Price Info:</b>
• Price: ${price}
• Market Cap: {format_currency(market_cap)}
• 5m Change: {price_change_text}

📈 <b>Trading Activity:</b>
• 1h Volume: {format_currency(volume_1h)}
• 1h Swaps: {swaps_1h}
• Holders: {holder_count}
• Progress: {progress:.1f}%

👤 <b>Creator:</b> <code>{creator}</code>

🛡️ <b>Risk Assessment:</b> {risk_text}

⏰ <b>Created:</b> {created_time_str}
            """.strip()
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting token notification: {e}")
            return f"🚀 New PumpFun token detected: {token_data.get('symbol', 'Unknown')} - {token_data.get('token_address', '')}"
    
    async def _deactivate_subscription(self, user_id: int) -> None:
        """Deactivate a user's subscription"""
        try:
            self.db.notification_subscriptions.update_one(
                {"user_id": user_id, "subscription_type": "pumpfun_new_tokens"},
                {"$set": {"is_active": False}}
            )
            logger.info(f"Deactivated subscription for user {user_id}")
        except Exception as e:
            logger.error(f"Error deactivating subscription: {e}")
    
    async def subscribe_user(self, user_id: int) -> bool:
        """Subscribe a user to PumpFun token notifications"""
        try:
            self.db.notification_subscriptions.update_one(
                {"user_id": user_id, "subscription_type": "pumpfun_new_tokens"},
                {"$set": {
                    "user_id": user_id,
                    "subscription_type": "pumpfun_new_tokens",
                    "is_active": True,
                    "subscribed_at": datetime.now()
                }},
                upsert=True
            )
            logger.info(f"User {user_id} subscribed to PumpFun notifications")
            return True
        except Exception as e:
            logger.error(f"Error subscribing user: {e}")
            return False
    
    async def unsubscribe_user(self, user_id: int) -> bool:
        """Unsubscribe a user from PumpFun token notifications"""
        try:
            self.db.notification_subscriptions.update_one(
                {"user_id": user_id, "subscription_type": "pumpfun_new_tokens"},
                {"$set": {"is_active": False}}
            )
            logger.info(f"User {user_id} unsubscribed from PumpFun notifications")
            return True
        except Exception as e:
            logger.error(f"Error unsubscribing user: {e}")
            return False
    
    async def is_user_subscribed(self, user_id: int) -> bool:
        """Check if a user is subscribed to notifications"""
        try:
            subscription = self.db.notification_subscriptions.find_one({
                "user_id": user_id,
                "subscription_type": "pumpfun_new_tokens",
                "is_active": True
            })
            return subscription is not None
        except Exception as e:
            logger.error(f"Error checking subscription status: {e}")
            return False
    
    def clear_database_tokens(self) -> int:
        """Clear all tokens from database (for testing)"""
        try:
            result = self.db.pumpfun_tokens.delete_many({})
            logger.info(f"Cleared {result.deleted_count} tokens from database")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error clearing database tokens: {e}")
            return 0
    
    def get_database_tokens_count(self) -> int:
        """Get the number of tokens in the database"""
        try:
            return self.db.pumpfun_tokens.count_documents({})
        except Exception as e:
            logger.error(f"Error counting database tokens: {e}")
            return 0
    
    def reset_notification_time(self) -> None:
        """Reset notification time to 1 hour ago (for testing)"""
        self.last_notification_time = datetime.now() - timedelta(hours=1)
        logger.info(f"Reset notification time to: {self.last_notification_time.strftime('%H:%M:%S')}")

# Global notification service instance
notification_service = NotificationService()
