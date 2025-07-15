from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from database.mongodb import db
from models.user import User, UserCreate, UserLogin, UserResponse, UserPreferences


class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv("SECRET_KEY")
        if not self.secret_key:
            raise ValueError("SECRET_KEY environment variable is required")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 24 * 60  # 24 hours

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def create_user(self, user_create: UserCreate) -> dict:
        """Create a new user"""
        # Check if user already exists
        existing_user = await db.get_user_by_email(user_create.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Hash password
        hashed_password = self.get_password_hash(user_create.password)

        # Create user data with default preferences
        user_data = {
            "email": user_create.email,
            "name": user_create.name,
            "hashed_password": hashed_password,
            "preferences": UserPreferences().dict(),
        }

        # Save user to database
        user_id = await db.create_user(user_data)

        # Return user without password
        return {
            "id": user_id,
            "email": user_create.email,
            "name": user_create.name
        }

    async def authenticate_user(self, user_login: UserLogin) -> dict:
        """Authenticate a user and return access token"""
        # Get user from database
        user = await db.get_user_by_email(user_login.email)
        if not user:
            raise ValueError("Invalid email or password")

        # Verify password
        if not self.verify_password(user_login.password, user["hashed_password"]):
            raise ValueError("Invalid email or password")

        # Check if user is active
        if not user.get("is_active", True):
            raise ValueError("Account is deactivated")

        # Update last login
        await db.update_last_login(user["_id"])

        # Create access token
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": user["email"], "user_id": user["_id"]},
            expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["_id"],
                "email": user["email"],
                "name": user["name"]
            }
        }

    async def verify_token(self, token: str) -> dict:
        """Verify a JWT token and return user data"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            user_id: str = payload.get("user_id")

            if email is None or user_id is None:
                raise ValueError("Invalid token")

        except JWTError:
            raise ValueError("Invalid token")

        # Get user from database
        user = await db.get_user_by_id(user_id)
        if user is None:
            raise ValueError("User not found")

        if not user.get("is_active", True):
            raise ValueError("Account is deactivated")

        return {
            "id": user["_id"],
            "email": user["email"],
            "name": user["name"]
        }

    async def get_user_profile(self, user_id: str) -> UserResponse:
        """Get complete user profile"""
        user = await db.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        return UserResponse(
            id=user["_id"],
            email=user["email"],
            name=user["name"],
            preferences=UserPreferences(**user.get("preferences", {})),
            created_at=user["created_at"],
            last_login=user.get("last_login"),
            is_active=user.get("is_active", True)
        )


# Global auth service instance
auth_service = AuthService()