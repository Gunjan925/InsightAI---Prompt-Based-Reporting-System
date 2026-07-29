import logging
import sys
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logger to output only to standard output console (not stored on disk)
logger = logging.getLogger("app")
logger.setLevel(logging.INFO) # Sets the minimum logging level to INFO (INFO, WARNING, ERROR, CRITICAL will be logged).

if not logger.handlers: # Ensures handlers are added only once to avoid duplicate log messages.
    console_handler = logging.StreamHandler(sys.stdout) # Creates a handler that prints log messages to the terminal (stdout)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# Creates middleware to log every incoming request and outgoing response.
class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        method = request.method
        path = request.url.path
        client = request.client.host if request.client else "unknown"
        
        # logger.info(f"HTTP Request: {method} {path} from {client}")
        logger.info(f"HTTP Request: {method} {path}")
        
        try:
            response = await call_next(request)
            duration = (time.time() - start_time) * 1000
            logger.info(f"HTTP Response: {method} {path} - Status: {response.status_code} - Time: {duration:.2f}ms") # HTTP Response: POST /auth/login - Status: 200 - Time: 42.18ms
            return response 
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"HTTP Exception: {method} {path} - Error: {str(e)} - Time: {duration:.2f}ms") # HTTP Exception: POST /report - Error: Database connection failed - Time: 85.32ms
            raise e

'''
%(asctime)s → Timestamp
%(levelname)s → INFO, ERROR, etc.
%(module)s → Python file name
%(message)s → Actual log message
'''