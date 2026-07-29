import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.auth_schema import UserRegister, UserLogin
from app.config.security import get_password_hash, verify_password
from app.models.blacklisted_token import BlacklistedToken

logger = logging.getLogger("app")

class AuthService:
    @staticmethod
    def register_user(db: Session, user_data: UserRegister) -> User:
        """
        Registers a new user after verifying that the username and email both are unique.
        """
        # Check if username already exists - to allow unique usernames
        existing_username = db.query(User).filter(User.username == user_data.username).first()
        if existing_username: # if username already exists
            logger.warning(f"Registration failed: Username '{user_data.username}' is already taken.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is already registered"
            )

        # Check if email already exists - to allow unique emails
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            logger.warning(f"Registration failed: Email '{user_data.email}' is already registered.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address is already registered"
            )

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"Successfully registered user: {new_user.username} (ID: {new_user.id})")
        return new_user

    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin) -> User:
        """
        Authenticates a user using email or username and verifies password.
        """
        user = None
        if login_data.email:
            user = db.query(User).filter(User.email == login_data.email).first()
        elif login_data.username:
            user = db.query(User).filter(User.username == login_data.username).first()
            
        if not user:
            logger.warning("Authentication failed: User account not found.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username, email, or password"
            )

        if not verify_password(login_data.password, user.hashed_password):
            logger.warning(f"Authentication failed for user '{user.username}': Invalid password.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username, email, or password"
            )

        logger.info(f"User authenticated successfully: {user.username} (ID: {user.id})")
        return user

    @staticmethod
    def logout_user(db: Session, token: str) -> None:
        """
        Revokes the given JWT token by blacklisting it in the database.
        """
        existing = db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first()
        if not existing:
            blacklisted_token = BlacklistedToken(token=token)
            db.add(blacklisted_token)
            db.commit()
            logger.info("Successfully blacklisted the token (logout).")
