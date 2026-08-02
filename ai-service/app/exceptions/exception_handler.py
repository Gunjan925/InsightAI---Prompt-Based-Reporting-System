# Converts exceptions into standardized HTTP responses.
import logging
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from app.exceptions.custom_exception import AIServiceException

# Retrieve the logger configuration
logger = logging.getLogger("ai_service")

# a single exception handler called in the main to handle the entire ai-service exceptions instead of try-catch block
def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers global exception handling middleware routines on the FastAPI app.
    Catch custom AIServiceExceptions and generic system errors to return clean HTTP responses.
    """
    @app.exception_handler(AIServiceException)
    async def ai_service_exception_handler(request: Request, exc: AIServiceException):
        logger.error(f"AI Service Specific Error: {exc.message} (HTTP status: {exc.status_code})")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.__class__.__name__,
                "message": exc.message
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled Exception during request processing: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "InternalServerError",
                "message": f"An unexpected system failure occurred in the AI service: {str(exc)}"
            }
        )