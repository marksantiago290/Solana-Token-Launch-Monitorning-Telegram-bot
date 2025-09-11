import logging
import sys
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config.settings import TELEGRAM_TOKEN
from handlers.error_handlers import error_handler
from handlers.callback_handlers import (
    handle_expected_input, 
    handle_start_menu,
)
from handlers.notification_handlers import register_notification_handlers
from database import init_database
from services.scheduler_service import scheduler_service

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

def create_bot():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.Text(["/start"]), handle_start_menu))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_expected_input))
    
    register_notification_handlers(application)
    
    application.add_error_handler(error_handler)
    
    return application

async def main_async():
    # Initialize database connection
    if not init_database():
        logging.error("Could not connect to MongoDB. Please check your configuration.")
        sys.exit(1)
    
    logging.info("Starting Crypto DeFi Analyze Telegram Bot...")
    
    app = create_bot()
    
    # Set up the AsyncIOScheduler (no jobs needed for now)
    scheduler = AsyncIOScheduler()
    
    # Start the scheduler within the running event loop
    scheduler.start()
    
    # Start the PumpFun token monitoring
    await scheduler_service.start_monitoring()
    
    # Run the application
    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    
    # Keep the application running
    try:
        await asyncio.Future()  # Run forever
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopping...")
    finally:
        await scheduler_service.stop_monitoring()
        scheduler.shutdown()
        await app.stop()

def main():
    # Run the async main function with asyncio
    asyncio.run(main_async())

if __name__ == '__main__':
    main()
