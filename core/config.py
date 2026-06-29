from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


BOT_NAMES = ("theo", "lusy", "pete", "eddy", "susy")


@dataclass(frozen=True, slots=True)
class BotConfig:
    name: str
    token: str
    enabled: bool


@dataclass(frozen=True, slots=True)
class AppConfig:
    supabase_url: str
    supabase_key: str
    mongo_uri: str
    mongo_database: str
    bots: dict[str, BotConfig]
    api_id: int
    api_hash: str
    susy_string_session: str

    @property
    def has_supabase(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)


def _env_bool(name: str, default: bool = True) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def load_config() -> AppConfig:
    load_dotenv()

    bots: dict[str, BotConfig] = {}
    for bot_name in BOT_NAMES:
        env_prefix = bot_name.upper()
        if bot_name == "eddy":
            token = os.getenv("EDDY_BOT_TOKEN") or os.getenv("ED_BOT_TOKEN", "")
        else:
            token = os.getenv(f"{env_prefix}_BOT_TOKEN", "")
        enabled = _env_bool(f"{env_prefix}_BOT_ENABLED", True)
        bots[bot_name] = BotConfig(name=bot_name, token=token, enabled=enabled)

    return AppConfig(
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_key=os.getenv("SUPABASE_KEY", ""),
        mongo_uri=os.getenv("MONGO_URI", ""),
        mongo_database=os.getenv("MONGO_DATABASE", "youthopiaos"),
        bots=bots,
        api_id=int(os.getenv("API_ID", "0")),
        api_hash=os.getenv("API_HASH", "").strip(),
        susy_string_session=os.getenv("SUSY_STRING_SESSION", "").strip(),
    )
