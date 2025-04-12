import motor.motor_asyncio
from pymongo.errors import ServerSelectionTimeoutError
from config import MONGO_URI, DB_NAME

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self._connection_ready = False
        
    async def connect(self):
        """Connect to the MongoDB database"""
        if self._connection_ready:
            return
            
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
            await self.client.server_info()  # Will raise exception if connection fails
            self.db = self.client[DB_NAME]
            self._connection_ready = True
            print("Connected to MongoDB!")
        except ServerSelectionTimeoutError:
            print("Failed to connect to MongoDB. Check if the URI is correct and the server is running.")
            self._connection_ready = False
            
    async def close(self):
        """Close the database connection"""
        if self.client:
            self.client.close()
            self._connection_ready = False
            print("Disconnected from MongoDB")

# Create singleton instance
db = Database()
