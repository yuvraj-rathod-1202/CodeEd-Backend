from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
load_dotenv()

client = None

async def connect_to_mongo():
    global client
    if client is None:
        client = AsyncIOMotorClient(os.getenv("MONGO_DB_URL"))

def get_db():
    if client is None:
        raise Exception("MongoDB client is not connected. Call connect_to_mongo() first.")
    return client.elevateed
    