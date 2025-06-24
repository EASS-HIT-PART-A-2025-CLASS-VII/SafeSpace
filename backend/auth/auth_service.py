from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from backend.models.schemas import UserCreate, UserLogin, User, UserPreferences
from backend.user_db.user_service import UserService

class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.user_service = UserService()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def create_user(self, user_data: UserCreate) -> User:
        # Check if user already exists
        existing_user = await self.user_service.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Hash password
        hashed_password = self.get_password_hash(user_data.password)
        
        # Create user with default preferences
        user = User(
            id=f"user_{datetime.utcnow().timestamp()}",
            email=user_data.email,
            name=user_data.name,
            preferences=UserPreferences(),
            created_at=datetime.utcnow()
        )
        
        # Save user to database
        await self.user_service.create_user(user, hashed_password)
        return user

    async def authenticate_user(self, credentials: UserLogin) -> str:
        user = await self.user_service.get_user_by_email(credentials.email)
        if not user:
            raise ValueError("Invalid email or password")
        
        stored_password = await self.user_service.get_user_password(user.id)
        if not self.verify_password(credentials.password, stored_password):
            raise ValueError("Invalid email or password")

        # Update last login
        await self.user_service.update_last_login(user.id)
        
        # Create access token
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return access_token

    async def verify_token(self, token: str) -> User:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                raise ValueError("Invalid token")
        except JWTError:
            raise ValueError("Invalid token")
        
        user = await self.user_service.get_user_by_email(email)
        if user is None:
            raise ValueError("User not found")
        return user