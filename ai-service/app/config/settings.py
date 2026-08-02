# Loads and validates configuration from .env using Pydantic Settings.
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    Application settings class for the AI Service.
    Loads and validates environment variables from the `.env` file.
    """
    # Google Gemini API key for interacting with Gemini LLM
    GEMINI_API_KEY: str = Field(default="", alias="GEMINI_API_KEY")
    
    # Local path to store persistent vector database files
    CHROMA_DB_PATH: str = Field(default="./chroma_db", alias="CHROMA_DB_PATH")
    
    # sentence-transformers model name to use locally
    EMBEDDING_MODEL_NAME: str = Field(default="all-MiniLM-L6-v2", alias="EMBEDDING_MODEL_NAME")
    
    # Host binding configuration for uvicorn
    HOST: str = Field(default="0.0.0.0", alias="HOST")
    
    # Port on which the AI Service FastAPI application runs
    PORT: int = Field(default=8001, alias="PORT")
    
    # Console logging verbosity level (e.g., DEBUG, INFO, WARNING, ERROR)
    LOG_LEVEL: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Single global instance of the Settings class to be imported in other modules
settings = Settings()