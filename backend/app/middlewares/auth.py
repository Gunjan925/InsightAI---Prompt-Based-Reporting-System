from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # Imports FastAPI's Bearer token authentication classes.
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.config.security import decode_access_token
from app.models.user import User
from app.models.blacklisted_token import BlacklistedToken

# Configure standard HTTPBearer token scheme
security_scheme = HTTPBearer() # Creates a Bearer authentication scheme that extracts the JWT token from the Authorization header.Example : Authorization: Bearer eyJhbGciOiJIUzI1Ni...

def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security_scheme), # Automatically extracts the Bearer token from the request header using HTTPBearer.
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency that extracts the JWT token from the Authorization header,
    decodes it, and retrieves the corresponding User database object.
    Raises 401 Unauthorized if validation fails.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check if the token has been blacklisted (logged out)
    blacklisted = db.query(BlacklistedToken).filter(BlacklistedToken.token == token.credentials).first()
    if blacklisted:
        raise credentials_exception

    payload = decode_access_token(token.credentials)
    if payload is None:
        raise credentials_exception
    
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    return user