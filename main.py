#!/usr/bin/env python3
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import schedule
import time
from src import ConfigManager, logger
from src.services import EmailService

def run_daily_summary():
    """Execute the daily email summary process."""
    logger.info("Starting daily email summary process")
    
    email_service = EmailService()
    
    if email_service.connect():
        try:
            # TODO: Implement email processing and summarization
            pass
        except Exception as e:
            logger.error(f"Error in daily summary process: {e}")
        finally:
            email_service.disconnect()
    else:
        logger.error("Failed to connect to email server")

def main():
    """Main application entry point."""
    # Initialize configuration
    config_manager = ConfigManager()
    
    # Handle configuration commands if any
    if len(sys.argv) > 1:
        config_manager.setup_cli()
        return

    # Check if application is configured
    if not config_manager.is_configured():
        print("Initial configuration required.")
        config_manager.initial_setup()
    
    logger.info("Email Summary Manager started")
    
    # Schedule daily run
    scan_time = os.getenv('SCAN_TIME', '09:00')
    schedule.every().day.at(scan_time).do(run_daily_summary)
    
    # Run immediately on startup
    run_daily_summary()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
