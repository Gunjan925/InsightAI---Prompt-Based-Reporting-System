# Configures console logging for the AI service (no log files).
import sys
import logging
from app.config.settings import settings

def setup_logger() -> logging.Logger:
    """
    Configures and initializes logging to stdout for the AI Service.
    Uses log levels defined in settings configuration.
    """
    logger = logging.getLogger("ai_service")
    
    # Prevent handler duplication if the logger has already been setup
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(settings.LOG_LEVEL)

    # Configure stdout streaming format (logs timestamp, level, module name and payload message)
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(settings.LOG_LEVEL)
    
    logger.addHandler(console_handler)
    
    # Stop log duplication propagation to parents (like uvicorn wrapper loggers)
    logger.propagate = False

    return logger

# Single application-wide logging utility instance
logger = setup_logger()