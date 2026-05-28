from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from importlib import import_module
from typing import Any

from core.config import BOT_NAMES, AppConfig, BotConfig, load_config
from shared.db.mongo import TelemetryMongoGateway
from shared.db.supabase import SupabaseGateway
from shared.logging.logger import get_logger
from shared.services import user_service
from shared.services.container import ServiceContainer, build_services

BotRunner = Callable[[BotConfig, ServiceContainer], Awaitable[None]]


@dataclass(slots=True)
class BotManager:
    config: AppConfig
    services: ServiceContainer

    @classmethod
    def from_env(cls) -> "BotManager":
        config = load_config()
        supabase = SupabaseGateway(config.supabase_url, config.supabase_key)
        telemetry = TelemetryMongoGateway(config.mongo_uri, config.mongo_database)
        services = build_services(supabase, telemetry)
        user_service.configure(services.users)
        return cls(config=config, services=services)

    async def start(self) -> None:
        logger = get_logger("youthopia.bot_manager")
        if not self.config.has_supabase:
            logger.warning("Supabase is not configured; bot runtime will not start.")
            return

        self.services.supabase.connect()
        self.services.telemetry.connect()

        runners: list[Awaitable[None]] = []
        for bot_name in BOT_NAMES:
            bot_config = self.config.bots[bot_name]
            if not bot_config.enabled:
                logger.info("Skipping disabled bot: %s", bot_name)
                continue
            if not bot_config.token:
                logger.info("Skipping bot without token: %s", bot_name)
                continue
            runners.append(self._run_bot(bot_name, bot_config))

        if not runners:
            logger.warning("No bots are enabled with tokens; startup completed without polling.")
            return

        await asyncio.gather(*runners)

    async def _run_bot(self, bot_name: str, bot_config: BotConfig) -> None:
        module = import_module(f"bots.{bot_name}.bot")
        run_bot: BotRunner | None = getattr(module, "run_bot", None)
        if run_bot is None:
            raise RuntimeError(f"bots.{bot_name}.bot must expose run_bot(config, services).")
        await run_bot(bot_config, self.services)


async def run() -> None:
    manager = BotManager.from_env()
    await manager.start()
