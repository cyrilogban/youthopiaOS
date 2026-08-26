from __future__ import annotations

from core.config import BotConfig
from core.telegram_runtime import run_polling_bot
from shared.services.container import ServiceContainer
from bots.susy.router import build_susy_router


async def run_bot(config: BotConfig, services: ServiceContainer) -> None:
    from bots.susy.clients.pyrogram_client import PyrogramClientManager
    from bots.susy.clients.pytgcalls_client import PyTgCallsClient
    from bots.susy.core.music.service import MusicService
    from bots.susy.infra.downloader.ytdlp import YtDlpDownloader
    from bots.susy.infra.audio.ffmpeg import FFmpegAudioProcessor
    import os

    app_config = services.app_config
    if app_config is None:
        from core.config import load_config
        app_config = load_config()
    
    # Inject Render static FFmpeg bin into system PATH
    bin_dir = os.path.join(os.getcwd(), "bin")
    if os.path.exists(bin_dir):
        os.environ["PATH"] = f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"
    
    # MUSIC SUBSYSTEM (DISABLED - PRESERVED FOR FUTURE REUSE)
    # pyrogram = PyrogramClientManager(config=app_config)
    # calls = PyTgCallsClient(pyrogram_manager=pyrogram)
    # music_service = MusicService(...)
    
    music_service = None

    from aiogram.types import BotCommand
    susy_commands = [
        BotCommand(command="start", description="Meet Susy & Community Welcome"),
        BotCommand(command="help", description="Show Susy hostess & community features"),
    ]

    susy_router = build_susy_router("Susy onboarding and engagement bot", music_service=None)

    # PyTgCalls and Pyrogram disabled
    # try:
    #     await pyrogram.start()
    #     await calls.start()
    # except Exception as e:
    #     print(f"SUSY VOICE STREAM NOTICE: {e}")

    try:
        await run_polling_bot(
            config, 
            services, 
            description="Susy onboarding and engagement bot",
            router=susy_router,
            commands=susy_commands,
        )
    finally:
        pass
