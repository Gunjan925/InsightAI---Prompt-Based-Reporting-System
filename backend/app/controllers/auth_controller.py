from sqlalchemy.orm import Session # Imports SQLAlchemy Session for performing database operations.
from app.schemas.auth_schema import UserRegister, UserLogin, Token, UserResponse # Imports request and response schemas used for validation and API responses.
from app.services.auth_service import AuthService # Imports the service layer containing authentication business logic.
from app.config.security import create_access_token # Imports the function to generate JWT access tokens.

# Controller class that coordinates authentication-related requests.
class AuthController:
    @staticmethod # Declares a static method that can be called without creating an object of AuthController.
    # Handles user registration by accepting a database session and validated user data, then returns user details. here the type of user_data should validate the UserRegister schema and the function should return the schema matching to the UserResponse
    def register(db: Session, user_data: UserRegister) -> UserResponse:
        """
        Coordinates user registration operations and returns the new user.
        """
        user = AuthService.register_user(db, user_data) # Calls the service layer to register the user in the database - this will return an orm object
        return UserResponse.from_orm(user) # Converts the SQLAlchemy User object into a Pydantic response model and returns it. Take this SQLAlchemy object and create a Pydantic object from it

    @staticmethod
    # Handles user login and returns a JWT token on successful authentication.
    def login(db: Session, login_data: UserLogin) -> Token:
        """
        Coordinates user login verification and generates an access token on success.
        """
        user = AuthService.authenticate_user(db, login_data)# Verifies the user's login credentials using the service layer.
        
        # Generate JWT token
        token_data = {"user_id": user.id, "username": user.username} # Creates the payload that will be stored inside the JWT token.
        access_token = create_access_token(data=token_data)
        
        user_resp = UserResponse.from_orm(user) # Converts the authenticated User object into a response schema.
        return Token(
            access_token=access_token, # Includes the generated JWT token in the response.
            token_type="bearer", # Specifies the authentication scheme as Bearer Token.
            user=user_resp # Includes the authenticated user's details in the response.
        )

    @staticmethod
    def logout(db: Session, token: str) -> None:
        """
        Coordinates token blacklisting to log out a user.
        """
        AuthService.logout_user(db, token)


'''
SQLAlchemy Object user contains
{
    id: 1,
    username: "abcd",
    email: "abcd@gmail.com",
    password: "$2b$12$abc..."
}
↓
from_orm()
↓
Creates
UserResponse(
    id=1,
    username="abcd",
    email="abcd@gmail.com"
)
Notice : Password is removed automatically because it isn't part of UserResponse.
FastAPI converts the Pydantic model into JSON.
Client receives
{
    "id": 1,
    "username": "abcd",
    "email": "abcd@gmail.com"
}
No password.

Without from_orm()
You would have to write
return UserResponse(
    id=user.id,
    username=user.username,
    email=user.email
)
for every response.
Imagine doing this for,User,Report,Upload,History,Dashboard
It becomes repetitive.
'''

'''
Complete workflow 
API Request
      │
      ▼
AuthController
      │
      ▼
AuthService (Business Logic)
      │
      ▼
Database
      │
      ▼
Controller generates JWT
      │
      ▼
Returns Token + User Details
'''