import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Settings:
    # Runtime environment: set ENV=production on Render (or let RENDER auto-detect
    # it). Local runs default to development, where the dev-mock login is allowed.
    ENV: str = os.getenv("ENV", os.getenv("APP_ENV", ""))

    # Bot Tokens
    THEO_BOT_TOKEN: str = os.getenv("THEO_BOT_TOKEN", "")
    LUSY_BOT_TOKEN: str = os.getenv("LUSY_BOT_TOKEN", "")
    PETE_BOT_TOKEN: str = os.getenv("PETE_BOT_TOKEN", "")
    EDIE_BOT_TOKEN: str = os.getenv("EDIE_BOT_TOKEN", "")
    ED_BOT_TOKEN: str = os.getenv("ED_BOT_TOKEN", "")
    EDDY_BOT_TOKEN: str = os.getenv("EDIE_BOT_TOKEN", os.getenv("EDDY_BOT_TOKEN", os.getenv("ED_BOT_TOKEN", "")))
    SUSY_BOT_TOKEN: str = os.getenv("SUSY_BOT_TOKEN", "")

    # Supabase (Primary Database)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # MongoDB (Optional Secondary Database)
    MONGO_URI: str = os.getenv("MONGO_URI", "")
    MONGO_DATABASE: str = os.getenv("MONGO_DATABASE", "youthopiaos")

    @property
    def is_production(self) -> bool:
        """Whether verification is hard-enforced and the dev mock is disabled.

        Priority: explicit ENV wins. With no ENV set, a hosted Render service
        (Render exports RENDER=true) counts as production so the mock bypass can
        never be left on by a missing variable. Everything else is development.
        """
        env = self.ENV.strip().lower()
        if env in ("development", "dev"):
            return False
        if env:
            return env in ("production", "prod")
        return bool(os.getenv("RENDER"))

settings = Settings()
