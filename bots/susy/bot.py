from __future__ import annotations

from core.config import BotConfig
from core.telegram_runtime import run_polling_bot
from shared.services.container import ServiceContainer
from bots.susy.router import build_susy_router


async def run_bot(config: BotConfig, services: ServiceContainer) -> None:
    from core.config import load_config
    from bots.susy.clients.pyrogram_client import PyrogramClientManager
    from bots.susy.clients.pytgcalls_client import PyTgCallsClient
    from bots.susy.core.music.service import MusicService
    from bots.susy.infra.downloader.ytdlp import YtDlpDownloader
    from bots.susy.infra.audio.ffmpeg import FFmpegAudioProcessor
    import os

    app_config = load_config()
    
    # Inject Render static FFmpeg bin into system PATH
    bin_dir = os.path.join(os.getcwd(), "bin")
    if os.path.exists(bin_dir):
        os.environ["PATH"] = f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"
    
    # Initialize Music Subsystem
    pyrogram = PyrogramClientManager(config=app_config)
    calls = PyTgCallsClient(pyrogram_manager=pyrogram)
    
    downloads_dir = os.path.join(os.getcwd(), "downloads")
    processed_dir = os.path.join(downloads_dir, "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    music_service = MusicService(
        downloader=YtDlpDownloader(
            download_dir=downloads_dir,
            retries=3,
            socket_timeout=15,
            extractor_retries=3,
            js_runtimes=["node"],
        ),
        audio_processor=FFmpegAudioProcessor(output_dir=processed_dir),
        stream_client=calls,
    )

    susy_router = build_susy_router("Susy onboarding and engagement bot", music_service=music_service)
    
    await pyrogram.start()
    await calls.start()
    
    try:
        await run_polling_bot(
            config, 
            services, 
            description="Susy onboarding and engagement bot",
            router=susy_router
        )
    finally:
        await calls.stop()
        await pyrogram.stop()
