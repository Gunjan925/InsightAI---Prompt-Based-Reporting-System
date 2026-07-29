import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware # Imports the base class used to create custom middleware in FastAPI.
from starlette.exceptions import HTTPException as StarletteHTTPException # Imports Starlette's HTTPException (FastAPI is built on Starlette) and renames it to avoid confusion.

logger = logging.getLogger("app")

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    # dispatch() is the main middleware function executed for every incoming request.request → Current HTTP request.call_next → Function that forwards the request to the next middleware or API endpoint.
    async def dispatch(self, request: Request, call_next):
        """
        Catches unhandled exceptions and HTTPExceptions during the request lifecycle
        and returns a structured JSON error response.
        """
        try:
            return await call_next(request) # Passes the request to the next middleware or route handler. If no exception occurs, returns the normal response.
        except StarletteHTTPException as exc: # Catches HTTP exceptions such as 401, 404, 403, etc.
            logger.warning(f"HTTP exception caught in middleware: {exc.status_code} - {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "error": {
                        "type": "HTTPException",
                        "message": exc.detail
                    }
                }
            )
        except Exception as exc: # Catches any unexpected exception not handled above.
            logger.error(f"Unhandled system exception: {str(exc)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "type": "InternalServerError",
                        "message": "An unexpected server error occurred."
                    }
                }
            )