#!/usr/bin/env python3
"""
Production startup script for BearTech Bot on Render
"""
import os
import asyncio
import threading
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
        # Use Flask's built-in server
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        logger.error(f"Health server error: {str(e)}")

def run_bot():
    """Run the Telegram bot"""
    try:
        from src.bot.main import run_bot
        logger.info("Starting BearTech Bot...")
        run_bot()
    except Exception as e:
        logger.error(f"Bot error: {str(e)}")

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
