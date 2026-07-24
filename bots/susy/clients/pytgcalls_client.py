from pathlib import Path

from bots.susy.clients.pyrogram_client import PyrogramClientManager


class PyTgCallsClient:
    """Media layer wrapper. All voice chat logic must pass through this class."""

    def __init__(self, pyrogram_manager: PyrogramClientManager) -> None:
        self._pyrogram_manager = pyrogram_manager
        self._app = None
        self._active_chats: set[int] = set()

    async def start(self) -> None:
        self._ensure_pyrogram_error_compat()
        from pytgcalls import PyTgCalls

        client = await self._pyrogram_manager.start()
        self._app = PyTgCalls(client)
        await self._app.start()

    async def stop(self) -> None:
        for chat_id in list(self._active_chats):
            await self.leave_group_call(chat_id)

    async def join_group_call(self, chat_id: int, file_path: str) -> None:
        app = self._require_app()
        _ensure_file_exists(file_path)
        from pytgcalls.types import MediaStream
        try:
            await self._pyrogram_manager.client.get_chat(chat_id)
        except Exception as e:
            print(f"PYROGRAM PEER CACHE RESOLVE NOTICE: {e}")
        await app.play(chat_id, MediaStream(file_path))
        self._active_chats.add(chat_id)

    async def switch_stream(self, chat_id: int, file_path: str) -> None:
        app = self._require_app()
        _ensure_file_exists(file_path)
        from pytgcalls.types import MediaStream
        try:
            await self._pyrogram_manager.client.get_chat(chat_id)
        except Exception as e:
            print(f"PYROGRAM PEER CACHE RESOLVE NOTICE: {e}")
        await app.play(chat_id, MediaStream(file_path))
        self._active_chats.add(chat_id)

    async def pause(self, chat_id: int) -> None:
        app = self._require_app()
        if chat_id in self._active_chats:
            await app.pause(chat_id)

    async def resume(self, chat_id: int) -> None:
        app = self._require_app()
        if chat_id in self._active_chats:
            await app.resume(chat_id)

    async def leave_group_call(self, chat_id: int) -> None:
        app = self._require_app()
        if chat_id in self._active_chats:
            await app.leave_call(chat_id)
            self._active_chats.discard(chat_id)

    def _require_app(self):
        if self._app is None:
            raise RuntimeError("PyTgCallsClient.start() must be called before streaming.")
        return self._app

    @staticmethod
    def _ensure_pyrogram_error_compat() -> None:
        """Patch missing error alias expected by some py-tgcalls builds."""
        import pyrogram.errors as pyrogram_errors

        if hasattr(pyrogram_errors, "GroupcallForbidden"):
            return

        class GroupcallForbidden(pyrogram_errors.BadRequest):
            pass

        pyrogram_errors.GroupcallForbidden = GroupcallForbidden


def _ensure_file_exists(file_path: str) -> None:
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Audio file does not exist: {file_path}")
