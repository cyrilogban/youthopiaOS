from pyrogram import Client

from core.config import AppConfig


class PyrogramClientManager:
    """Owns the Pyrogram client session used by PyTgCalls."""

    def __init__(self, config: AppConfig) -> None:
        self.client = Client(
            name="susy",
            api_id=config.api_id,
            api_hash=config.api_hash,
            session_string=config.susy_string_session,
        )

    async def start(self) -> Client:
        if not self.client.is_connected:
            await self.client.start()
        return self.client

    async def stop(self) -> None:
        if self.client.is_connected:
            await self.client.stop()
