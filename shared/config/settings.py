import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Settings:
    # Bot Tokens
    THEO_BOT_TOKEN: str = os.getenv("THEO_BOT_TOKEN", "")
    LUSY_BOT_TOKEN: str = os.getenv("LUSY_BOT_TOKEN", "")
    PETE_BOT_TOKEN: str = os.getenv("PETE_BOT_TOKEN", "")
    ED_BOT_TOKEN: str = os.getenv("ED_BOT_TOKEN", "")
    SUSY_BOT_TOKEN: str = os.getenv("SUSY_BOT_TOKEN", "")

    # Supabase (Primary Database)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # MongoDB (Optional Secondary Database)
    MONGO_URI: str = os.getenv("MONGO_URI", "")

settings = Settings()
