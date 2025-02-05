import logging
from pathlib import Path

def setup_logger():
    """Configure and return the application logger."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / 'app.log')
        ]
    )
    
    return logging.getLogger('email_manager')

logger = setup_logger()
