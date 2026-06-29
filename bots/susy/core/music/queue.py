from bots.susy.core.music.models import Track


class PerChatMusicQueue:
    """FIFO queue storage keyed by Telegram chat id."""

    def __init__(self) -> None:
        self._queues: dict[int, list[Track]] = {}

    def add(self, chat_id: int, track: Track) -> None:
        self._queues.setdefault(chat_id, []).append(track)

    def pop_next(self, chat_id: int) -> Track | None:
        queue = self._queues.get(chat_id, [])
        if not queue:
            return None

        track = queue.pop(0)
        if not queue:
            self._queues.pop(chat_id, None)
        return track

    def peek(self, chat_id: int) -> Track | None:
        queue = self._queues.get(chat_id, [])
        return queue[0] if queue else None

    def clear(self, chat_id: int) -> None:
        self._queues.pop(chat_id, None)

    def is_empty(self, chat_id: int) -> bool:
        return not self._queues.get(chat_id)

    def describe(self, chat_id: int) -> str:
        queue = self._queues.get(chat_id, [])
        if not queue:
            return "The queue is empty right now."

        lines = ["Current queue:"]
        lines.extend(f"{index}. {track.title}" for index, track in enumerate(queue, start=1))
        return "\n".join(lines)


MusicQueue = PerChatMusicQueue
