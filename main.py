#!/usr/bin/env python3
import sys
from pathlib import Path
import schedule
import time
from src.config.manager import ConfigManager
from src.utils.logger import logger
from src.services.email_service import EmailService
from src.services.summary_service import SummaryService
from src.services.todoist_service import TodoistService

# Add the project root directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_daily_summary():
    """Execute the daily email summary process."""
    logger.info("Starting daily email summary process")
    
    email_service = EmailService()
    
    if email_service.connect():
        try:
            emails = email_service.fetch_recent_emails(days=1)
            logger.info(f"Fetched {len(emails)} recent emails.")
            # print(emails)
            summary_text = SummaryService.summarize(emails)
            # print(text_summary)
            todoist_service = TodoistService()
            task_created = todoist_service.create_task("Daily Email Summary", summary_text)
            if task_created:
                logger.info("Todoist task created successfully.")
            else:
                logger.error("Failed to create Todoist task.")
        except Exception as e:
            logger.error(f"Error in daily summary process: {e}")
        finally:
            email_service.disconnect()
    else:
        logger.error("Failed to connect to Gmail API")

def main():
    """Main application entry point."""
    config_manager = ConfigManager()
    
    if len(sys.argv) > 1:
        config_manager.setup_cli()
        return
    
    if not config_manager.is_configured():
        print("Initial configuration required.")
        config_manager.initial_setup()
    
    logger.info("Email Summary Manager started")
    
    # Load configuration from the config file.
    config = config_manager.load_config()
    scan_time = config.get('SCAN_TIME', '09:00')
    schedule.every().day.at(scan_time).do(run_daily_summary)
    
    run_daily_summary()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()