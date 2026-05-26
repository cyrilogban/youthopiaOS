from supabase import create_client, Client
from shared.config.settings import settings
import logging

logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    """
    Initializes and returns the Supabase client using settings from config.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError("Supabase URL and Key must be set in the environment variables.")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Shared client instance across the ecosystem
try:
    supabase: Client = get_supabase_client()
except Exception as e:
    supabase = None
    logger.error(f"Failed to initialize Supabase client: {e}")
