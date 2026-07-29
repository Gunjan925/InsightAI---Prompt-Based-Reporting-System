from pydantic_settings import BaseSettings # BaseSettings automatically reads values from environment variables or a .env file.

# we are not using dotenv because : pydantic_settings = industry appraoch and it uses dotenv only at the core
# Cons :  You fetch each variable manually. No type checking (everything is returned as a string). No validation for missing variables. Configuration is scattered across the project.

# Creates a configuration class.Every variable inside this class becomes a configuration setting.
class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    AI_SERVICE_URL: str

    # Special configuration for BaseSettings.
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

'''
                .env
                  │
                  ▼
         settings = Settings()
                  │
      ┌───────────┼────────────┐
      ▼           ▼            ▼
database.py   security.py   report.py
      │           │            │
      └────── uses settings ───┘
'''