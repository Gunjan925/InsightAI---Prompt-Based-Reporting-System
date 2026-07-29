from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.schemas.auth_schema import UserRegister, UserLogin, Token, UserResponse
from app.controllers.auth_controller import AuthController
from app.middlewares.auth import get_current_user, security_scheme
from app.models.user import User

# Creates a group of related API endpoints. Adds /auth before every endpoint (/auth/login, /auth/register). Groups these APIs under Authentication in Swagger UI.
# Swagger UI is an automatically generated interactive webpage that documents all your FastAPI APIs. It lets you view, test, and understand your endpoints without using tools like Postman. Swagger UI: http://127.0.0.1:8000/docs — Interactive documentation where you can test APIs.
router = APIRouter(prefix="/auth", tags=["Authentication"]) 

# response_model : Formats and validates the API response using a Pydantic schema.
# status_code : Sets the HTTP status code returned by the endpoint (e.g., 201 Created, 200 OK).
# Depends : Automatically provides a database session to the endpoint.

# register a new user
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user with a unique username, email, and password.
    """
    return AuthController.register(db, user_data)

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Log in with username/email and password to receive a JWT access token.
    """
    return AuthController.login(db, login_data)

@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get the profile details of the currently authenticated user.
    """
    return UserResponse.from_orm(current_user)

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: HTTPAuthorizationCredentials = Depends(security_scheme)
):
    """
    Log out the current user by blacklisting their access token.
    """
    AuthController.logout(db, token.credentials)
    return {"message": "Successfully logged out"}