import logging
from sqlalchemy import create_engine # to create the connection between your application and the MySQL database. It is the first step before performing any database operations.
from sqlalchemy.ext.declarative import declarative_base # Used to create the base class for all SQLAlchemy models.
from sqlalchemy.orm import sessionmaker # Used to create database sessions.A session allows you to: Read data , Insert data , Update data , Delete data without repeatedly opening new database connections.
from app.config.settings import settings

logger = logging.getLogger("app") # Creates a logger named "app".

# Setup the SQLAlchemy database engine for MySQL
try:
    # Creates the SQLAlchemy Engine. The engine manages - database connections , connection pooling , SQL execution
    engine = create_engine(
        settings.DATABASE_URL, # Reads the database URL from .env.
        pool_pre_ping=True, # Before giving a connection, SQLAlchemy checks whether it is still alive. If a connection is broken, it creates a new one automatically. Or else uses the already created connection
        pool_size=10, # Keeps 10 database connections ready.
        max_overflow=10 # 10 connections are already busy. SQLAlchemy can temporarily create 10 additional connections. So maximum 10 + 10 = 20 connections.
    )
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise e

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Creates a factory that produces database sessions. Autocommit : Database changes are not automatically saved.AutoFlush : Changes are not automatically sent to the database. Bind : Connects this session factory to the engine created earlier.
Base = declarative_base() # Creates the parent class for every ORM model.

# Function that provides a database session.
def get_db():
    """
    FastAPI dependency to yield a database session and ensure it is closed after request lifecycle.
    """
    db = SessionLocal() # Creates a new database session.
    try:
        yield db
    finally:
        db.close()

# Function to create all database tables.
def init_db():
    """
    Initializes database tables by executing metadata creation.
    """
    try:
        logger.info("Initializing database tables...")
        Base.metadata.create_all(bind=engine) # creates all the required tables in the database if doesnt exists
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database tables: {e}")
        raise e

'''
This file is run when it is imported.
For example, 
when main.py imports something like : from app.api.auth import router
and auth.py imports : from app.config.database import get_db
Python loads database.py. During import, all top-level code executes, including:
engine = create_engine(...)
SessionLocal = sessionmaker(...)
Base = declarative_base()
Only the code inside functions (get_db(), init_db()) waits until those functions are called.
So create_engine() is not a function definition—it is a function call executed immediately when the module is imported.
'''