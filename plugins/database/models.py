from .db import db
from datetime import datetime

class Users:
    """Collection for storing users who have interacted with the bot"""
    collection = "users"
    
    @staticmethod
    async def add_user(user_id, username=None, first_name=None, last_name=None):
        """Add a new user or update existing user"""
        user = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "last_active": datetime.now(),
            "joined_date": datetime.now()
        }
        
        # Use upsert to add if not exists, or update if exists
        await db.db[Users.collection].update_one(
            {"user_id": user_id},
            {"$set": {"username": username, "first_name": first_name, "last_name": last_name, "last_active": datetime.now()},
             "$setOnInsert": {"joined_date": datetime.now()}},
            upsert=True
        )
        
    @staticmethod
    async def count_users():
        """Count total users in database"""
        return await db.db[Users.collection].count_documents({})
        
    @staticmethod
    async def get_user(user_id):
        """Get user details"""
        return await db.db[Users.collection].find_one({"user_id": user_id})


class Chats:
    """Collection for storing groups where bot is added"""
    collection = "chats"
    
    @staticmethod
    async def add_chat(chat_id, title=None, chat_type=None):
        """Add a new chat or update existing chat"""
        chat = {
            "chat_id": chat_id,
            "title": title,
            "chat_type": chat_type,
            "last_active": datetime.now(),
            "joined_date": datetime.now()
        }
        
        # Use upsert to add if not exists, or update if exists
        await db.db[Chats.collection].update_one(
            {"chat_id": chat_id},
            {"$set": {"title": title, "chat_type": chat_type, "last_active": datetime.now()},
             "$setOnInsert": {"joined_date": datetime.now()}},
            upsert=True
        )
        
    @staticmethod
    async def count_chats():
        """Count total chats in database"""
        return await db.db[Chats.collection].count_documents({})
        
    @staticmethod
    async def count_group_chats():
        """Count group chats in database"""
        return await db.db[Chats.collection].count_documents({"chat_type": {"$in": ["group", "supergroup"]}})
        
    @staticmethod
    async def get_chat(chat_id):
        """Get chat details"""
        return await db.db[Chats.collection].find_one({"chat_id": chat_id})
