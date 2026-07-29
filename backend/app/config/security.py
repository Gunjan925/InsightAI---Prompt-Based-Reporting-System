import logging
from datetime import datetime, timedelta
from typing import Optional
import jwt # to create and decode the jwt tokens
from passlib.context import CryptContext # to hash and verify the passwords
from app.config.settings import settings

logger = logging.getLogger("app") # Creates the application logger.

# Password hashing context using Bcrypt
# Creates a password hashing object.
# schemes=["bcrypt"] : Uses the bcrypt hashing algorithm.
# deprecated="auto" : If you later change to a newer hashing algorithm, Passlib can automatically identify old hashes and help migrate them.
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

# Function to hash a plain password.
def get_password_hash(password: str) -> str:
    """
    Hashes a plain text password using bcrypt.
    """
    return pwd_context.hash(password) # Hashes the password using bcrypt. Only the hashed password is stored in the database.

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that a plain text password matches a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password) # Passlib hashes the entered password and compares it with the stored hash.

# Function to generate a JWT access token.
# data : Payload to include inside the token. expires_delta : Optional custom expiry time. If not provided, default expiry is used.
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a JWT access token encoding the provided dictionary payload.
    """
    to_encode = data.copy() # Copies the payload. Avoids modifying the original dictionary.
    if expires_delta: # Checks whether a custom expiry was passed.
        expire = datetime.utcnow() + expires_delta # Creates expiration time using the custom value.
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) # Creates expiration time using the time value present in the env.
    
    to_encode.update({"exp": expire}) # exp is a standard JWT claim used for expiration.
    try:
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM) # Creates the JWT.
        return encoded_jwt # Returns the generated JWT string.
    except Exception as e:
        logger.error(f"Error encoding JWT token: {e}")
        raise e

def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodes a JWT access token and returns its claims payload.
    Returns None if token is invalid or expired.
    """
    try:
        decoded_payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        logger.warning("Attempted to decode an expired JWT token.")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Attempted to decode an invalid JWT token: {e}")
        return None

'''
User Registers
        │
        ▼
get_password_hash()
        │
        ▼
Store hashed password in DB
        │
        ▼
User Logs In
        │
        ▼
verify_password()
        │
Password Correct?
        │
      Yes
        ▼
create_access_token()
        │
        ▼
JWT Token
        │
        ▼
Frontend Stores Token
        │
        ▼
Every Protected API Request
        │
Authorization: Bearer <token>
        │
        ▼
decode_access_token()
        │
Token Valid?
        │
   Yes      No
    │        │
    ▼        ▼
Allow     Return 401 Unauthorized
'''