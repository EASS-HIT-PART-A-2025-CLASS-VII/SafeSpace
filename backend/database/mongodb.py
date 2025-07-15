from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)


class MongoDB:
    def __init__(self):
        # MongoDB connection string from environment variable
        self.connection_string = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        if not self.connection_string:
            raise ValueError("MONGODB_URL environment variable is required")
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None

    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.db = self.client.safespace

            # Test connection
            await self.client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")

            # Create indexes
            await self.create_indexes()

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    async def create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Users collection indexes
            await self.db.users.create_index("email", unique=True)
            await self.db.users.create_index("created_at")

            # User data collections indexes
            await self.db.mood_entries.create_index([("user_id", 1), ("timestamp", -1)])
            await self.db.journal_entries.create_index([("user_id", 1), ("timestamp", -1)])
            await self.db.joy_moments.create_index([("user_id", 1), ("timestamp", -1)])

            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")

    # User Management
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user"""
        try:
            user_data["created_at"] = datetime.utcnow()
            user_data["last_login"] = None
            user_data["is_active"] = True

            result = await self.db.users.insert_one(user_data)
            return str(result.inserted_id)
        except DuplicateKeyError:
            raise ValueError("User with this email already exists")
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            user = await self.db.users.find_one({"email": email})
            if user:
                user["_id"] = str(user["_id"])
            return user
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            user = await self.db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                user["_id"] = str(user["_id"])
            return user
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None

    async def update_last_login(self, user_id: str):
        """Update user's last login time"""
        try:
            await self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"last_login": datetime.utcnow()}}
            )
        except Exception as e:
            logger.error(f"Failed to update last login: {e}")

    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Update user preferences"""
        try:
            await self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"preferences": preferences}}
            )
        except Exception as e:
            logger.error(f"Failed to update user preferences: {e}")
            raise

    # Mood Entries
    async def save_mood_entry(self, user_id: str, mood_data: Dict[str, Any]):
        """Save a mood entry"""
        try:
            mood_data["user_id"] = user_id
            mood_data["timestamp"] = datetime.utcnow()

            await self.db.mood_entries.insert_one(mood_data)
        except Exception as e:
            logger.error(f"Failed to save mood entry: {e}")
            raise

    async def get_mood_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's mood history"""
        try:
            cursor = self.db.mood_entries.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)

            entries = []
            async for entry in cursor:
                entry["_id"] = str(entry["_id"])
                entries.append(entry)

            return entries
        except Exception as e:
            logger.error(f"Failed to get mood history: {e}")
            return []

    # Journal Entries
    async def save_journal_entry(self, user_id: str, journal_data: Dict[str, Any]):
        """Save a journal entry"""
        try:
            journal_data["user_id"] = user_id
            journal_data["timestamp"] = datetime.utcnow()

            await self.db.journal_entries.insert_one(journal_data)
        except Exception as e:
            logger.error(f"Failed to save journal entry: {e}")
            raise

    async def get_journal_entries(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's journal entries"""
        try:
            cursor = self.db.journal_entries.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)

            entries = []
            async for entry in cursor:
                entry["_id"] = str(entry["_id"])
                entries.append(entry)

            return entries
        except Exception as e:
            logger.error(f"Failed to get journal entries: {e}")
            return []

    # Joy Moments
    async def save_joy_moment(self, user_id: str, joy_data: Dict[str, Any]):
        """Save a joy moment"""
        try:
            joy_data["user_id"] = user_id
            joy_data["timestamp"] = datetime.utcnow()

            await self.db.joy_moments.insert_one(joy_data)
        except Exception as e:
            logger.error(f"Failed to save joy moment: {e}")
            raise

    async def get_joy_moments(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get user's joy moments"""
        try:
            cursor = self.db.joy_moments.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)

            moments = []
            async for moment in cursor:
                moment["_id"] = str(moment["_id"])
                moments.append(moment)

            return moments
        except Exception as e:
            logger.error(f"Failed to get joy moments: {e}")
            return []

    async def delete_joy_moment(self, user_id: str, moment_id: str):
        """Delete a joy moment"""
        try:
            await self.db.joy_moments.delete_one({
                "_id": ObjectId(moment_id),
                "user_id": user_id
            })
        except Exception as e:
            logger.error(f"Failed to delete joy moment: {e}")
            raise


# Global database instance
db = MongoDB()