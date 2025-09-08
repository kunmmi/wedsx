#!/usr/bin/env python3
"""
Production startup script for BearTech Bot on Render - Clean v20 version
"""
import os
import logging
from multiprocessing import Process

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('beartech_bot.log')
    ]
)

logger = logging.getLogger(__name__)

def run_health_server():
    """Run the health check server in a separate process"""
    try:
        from health_check import app
        port = int(os.getenv("PORT", 8000))
        logger.info(f"Starting health check server on port {port}")
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        logger.error(f"Health server error: {str(e)}")

def run_bot():
    """Run the Telegram bot using v20 Application.run_polling() - NO Updater"""
    try:
        from telegram.ext import ApplicationBuilder
        from telegram import BotCommand
        from src.bot.handlers import get_handlers
        
        logger.info("Starting BearTech Bot with v20 Application.run_polling()...")
        
        # Build application
        application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
        
        # Add handlers
        handlers = get_handlers()
        for handler in handlers:
            application.add_handler(handler)
        
        # Set bot commands
        async def set_commands():
            commands = [
                BotCommand("start", "Start the bot and see welcome message"),
                BotCommand("help", "Show detailed help and usage instructions"),
                BotCommand("analyze", "Analyze a specific token contract address"),
                BotCommand("chains", "Show supported blockchain networks"),
                BotCommand("status", "Show bot status and statistics")
            ]
            await application.bot.set_my_commands(commands)
            logger.info("Bot commands set successfully")
        
        # Run polling (blocking) - NO Updater
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"],
            post_init=set_commands
        )
    except Exception as e:
        logger.error(f"Bot error: {str(e)}")
        raise

def main():
    """Main production startup function"""
    logger.info("Starting BearTech Bot in production mode...")
    
    # Check required environment variables
    required_vars = ["TELEGRAM_BOT_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return
    
    # Start health check server in a separate process
    health_process = Process(target=run_health_server)
    health_process.start()
    
    # Start the bot in the main process
    try:
        run_bot()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
    finally:
        # Clean up health server process
        if health_process.is_alive():
            health_process.terminate()
            health_process.join()

if __name__ == "__main__":
    main()
