import os
import logging

def configure_logging(name="Main"):
    """
    Configure application logging with consistent settings.
    
    Args:
        name: Name for the logger instance (default: "Main")
        
    Returns:
        Logger: Configured logger instance
    """
    # Configure logging based on environment variable
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Create base directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("logs/screenshots", exist_ok=True)
    
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler("logs/cheminotify.log", mode='a')
    ]
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True
    )
    
    # Return logger for calling function to use
    return logging.getLogger(name)