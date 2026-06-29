from typing import Protocol

from bots.susy.core.music.errors import DownloadFailedError
from bots.susy.core.music.models import MusicResult, Track
from bots.susy.core.music.queue import PerChatMusicQueue


class Downloader(Protocol):
    async def download(self, query: str) -> Track: ...


class AudioProcessor(Protocol):
    async def prepare_for_stream(self, track: Track) -> Track: ...


class StreamClient(Protocol):
    async def join_group_call(self, chat_id: int, file_path: str) -> None: ...

    async def switch_stream(self, chat_id: int, file_path: str) -> None: ...

    async def pause(self, chat_id: int) -> None: ...

    async def resume(self, chat_id: int) -> None: ...

    async def leave_group_call(self, chat_id: int) -> None: ...


class MusicService:
    """Framework-agnostic music orchestrator.

    aiogram calls this service, but this service never imports aiogram or Telegram Bot API types.
    Voice logic is delegated to the PyTgCalls stream client.
    """

    def __init__(
        self,
        downloader: Downloader,
        audio_processor: AudioProcessor,
        stream_client: StreamClient,
        queue: PerChatMusicQueue | None = None,
    ) -> None:
        self._downloader = downloader
        self._audio_processor = audio_processor
        self._stream_client = stream_client
        self._queue = queue or PerChatMusicQueue()
        self._playing_chats: set[int] = set()

    async def play(self, chat_id: int, query: str) -> MusicResult:
        try:
            downloaded = await self._downloader.download(query)
            track = await self._audio_processor.prepare_for_stream(downloaded)
        except DownloadFailedError as error:
            return MusicResult(message=_friendly_download_error(error.reason))
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"MUSIC PREPARE ERROR: {error_trace}")
            return MusicResult(
                message=f"I couldn't prepare that track right now. Debug: {str(e)}"
            )
        self._queue.add(chat_id, track)

        if chat_id not in self._playing_chats:
            await self._start_next(chat_id)
            return MusicResult(message=f"Now playing: {track.title}", track=track)

        return MusicResult(message=f"Added to queue: {track.title}", track=track)

    async def skip(self, chat_id: int) -> MusicResult:
        if chat_id not in self._playing_chats and self._queue.is_empty(chat_id):
            return MusicResult(message="There is nothing to skip right now.")

        next_track = self._queue.pop_next(chat_id)
        if next_track is None:
            await self.stop(chat_id)
            return MusicResult(message="Skipped. The queue is now empty.")

        await self._stream_client.switch_stream(chat_id=chat_id, file_path=next_track.file_path)
        self._playing_chats.add(chat_id)
        return MusicResult(message=f"Now playing: {next_track.title}", track=next_track)

    async def stop(self, chat_id: int) -> MusicResult:
        self._queue.clear(chat_id)
        self._playing_chats.discard(chat_id)
        await self._stream_client.leave_group_call(chat_id)
        return MusicResult(message="Music stopped and the queue is cleared.")

    async def pause(self, chat_id: int) -> MusicResult:
        await self._stream_client.pause(chat_id)
        return MusicResult(message="Paused playback.")

    async def resume(self, chat_id: int) -> MusicResult:
        await self._stream_client.resume(chat_id)
        return MusicResult(message="Resumed playback.")

    def describe_queue(self, chat_id: int) -> str:
        return self._queue.describe(chat_id)

    async def _start_next(self, chat_id: int) -> Track | None:
        track = self._queue.pop_next(chat_id)
        if track is None:
            self._playing_chats.discard(chat_id)
            await self._stream_client.leave_group_call(chat_id)
            return None

        self._playing_chats.add(chat_id)
        await self._stream_client.join_group_call(chat_id=chat_id, file_path=track.file_path)
        return track


def _friendly_download_error(reason: str) -> str:
    if reason == "timeout":
        return "I couldn't fetch that track right now due to a network timeout. Please try again."
    if reason == "source_unavailable":
        return "I couldn't access that source right now. Please try another link or query."
    return f"Debug Fetch Error: {reason}"
