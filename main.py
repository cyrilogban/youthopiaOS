from __future__ import annotations

import asyncio

from core.bot_manager import run
from keep_alive import keep_alive


if __name__ == "__main__":
    keep_alive()
    asyncio.run(run())
