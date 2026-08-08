import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

from app.core.config import Setting

# Ensure environment variables are loaded
base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, "..", "..", ".env"))

_mongo_client = None


def get_mongo_client() -> AsyncIOMotorClient:
    global _mongo_client
    if _mongo_client is None:
        mongo_url = Setting.MONGODB_URL_KEY or os.getenv("MONGODB_URL_KEY")
        if not mongo_url:
            raise ValueError("MONGODB_URL_KEY is not set in environment or config.")
        _mongo_client = AsyncIOMotorClient(mongo_url, tlsCAFile=certifi.where())
    return _mongo_client


def get_vector_collection(db_name: str = "vector_demo_db", collection_name: str = "documents"):
    client = get_mongo_client()
    return client[db_name][collection_name]
