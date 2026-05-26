from pymongo import MongoClient
from shared.config.settings import settings
import logging

logger = logging.getLogger(__name__)

def get_mongo_client() -> MongoClient:
    """
    Initializes and returns the MongoDB client using settings from config.
    """
    if not settings.MONGO_URI:
        raise ValueError("MongoDB URI must be set in the environment variables.")
    return MongoClient(settings.MONGO_URI)

# Shared optional secondary client instance
try:
    mongo: MongoClient = get_mongo_client()
except Exception as e:
    mongo = None
    logger.info(f"MongoDB client not initialized (optional secondary database): {e}")
