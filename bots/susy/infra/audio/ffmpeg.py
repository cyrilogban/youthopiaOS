import asyncio
from pathlib import Path
from uuid import uuid4

import ffmpeg

from bots.susy.core.music.models import Track


class FFmpegAudioProcessor:
    """Converts downloaded audio into PyTgCalls-friendly PCM raw audio."""

    def __init__(self, output_dir: str) -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    async def prepare_for_stream(self, track: Track) -> Track:
        return await asyncio.to_thread(self._prepare_sync, track)

    def _prepare_sync(self, track: Track) -> Track:
        output_path = self._output_dir / f"{uuid4()}.wav"

        (
            ffmpeg.input(track.file_path)
            .output(
                str(output_path),
                format="wav",
                acodec="pcm_s16le",
                ac=2,
                ar="48000",
                loglevel="error",
            )
            .overwrite_output()
            .run()
        )

        return Track(
            title=track.title,
            file_path=str(output_path),
            duration=track.duration,
            source_url=track.source_url,
        )
