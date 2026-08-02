# Starts the FastAPI application, loads configuration and registers all routers.
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.exceptions.exception_handler import register_exception_handlers
from app.routers.health_router import router as health_router
from app.routers.dashboard_router import router as dashboard_router
from app.routers.chat_router import router as chat_router
from app.routers.report_router import router as report_router
from app.utils.logger import logger

# Initialize FastAPI application instance
app = FastAPI(
    title="InsightAI AI Service Microservice",
    description="Core analytical microservice for structured data cleaning, automatic plotting, and Gemini prompt analysis.",
    version="1.0.0"
)

# CORS middleware mapping to allow cross-origin calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000", # backend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach the global error handlers
register_exception_handlers(app)

# Mount endpoints on app router
app.include_router(health_router)
app.include_router(report_router)                    # Exposes POST /api/generate
app.include_router(dashboard_router, prefix="/api")    # Exposes POST /api/dashboard
app.include_router(chat_router, prefix="/api")         # Exposes POST /api/chat

@app.on_event("startup")
async def startup_event():
    """
    Routines to run on microservice boot up.
    """
    logger.info("====================================================")
    # logger.info(f"InsightAI service active. Host: {settings.HOST} | Port: {settings.PORT}")
    logger.info(f"InsightAI service active. Port: {settings.PORT}")
    logger.info("====================================================")