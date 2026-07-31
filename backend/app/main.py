from contextlib import asynccontextmanager # contextlib is a built-in Python module. It provides utilities for creating and working with context managers (objects used with the with statement).
# asynccontextmanager is a decorator used to create an asynchronous context manager. It is used with async with instead of with. It is commonly used in asynchronous frameworks like FastAPI, asyncio, and httpx.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.database import init_db
from app.middlewares.logger import LoggerMiddleware
from app.middlewares.error_handler import ErrorHandlerMiddleware
from app.api.auth import router as auth_router
from app.api.upload import router as upload_router
from app.api.report import router as report_router
from app.api.history import router as history_router
from app.api.dashboard import router as dashboard_router

# Import all models to ensure they are registered on the Base metadata before table creation
from app.models.user import User
from app.models.uploaded_file import UploadedFile
from app.models.report import Report
from app.models.blacklisted_token import BlacklistedToken

# Defines the application's lifespan.

# Runs once when the server starts and once when it shuts down.
# app: FastAPI is the FastAPI application instance.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database schemas on application startup
    init_db() # Creates all database tables if they do not already exist. Runs only once when the server starts.
    yield # Marks the point where FastAPI starts handling requests. Code before yield runs at startup. Code after yield (if present) runs during shutdown.

app = FastAPI(
    title="InsightAI Prompt-Based Reporting System Backend",
    description="Central backend server managing authentication, uploads, report retrieval, and AI coordination.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware, # CORS (Cross-Origin Resource Sharing) allows your frontend to call your backend.
    allow_origins=[
        "http://localhost:5173",   # React frontend
    ],  # Adjust in production to frontend origins
    # check->
    allow_credentials=True, # Allows cookies and authentication credentials to be sent.
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom middleware
# Middlewares are evaluated in the order they are wrapped (onion architecture)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggerMiddleware)

# Include API Routers under /api
app.include_router(auth_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(report_router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")

@app.get("/health", tags=["Health Check"])
def read_root():
    return {
        "status": "online",
        "app": "InsightAI Prompt-Based Reporting System API Server"
    }