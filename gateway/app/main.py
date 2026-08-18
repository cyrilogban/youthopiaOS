"""YouThopiaOS gateway — the server-side trust boundary for the Mini App.

Exposes:
  - GET /health  — liveness probe (no auth).
  - GET /me      — the caller's verified Telegram identity, guarded by the
                   require_telegram_user dependency (401 if initData is missing,
                   forged, or stale). First endpoint that actually uses the
                   trust boundary end-to-end.
"""
from fastapi import Depends, FastAPI

from gateway.app.auth import require_telegram_user
from gateway.app.models import TelegramUser

app = FastAPI(title="YouThopiaOS Gateway")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe — proves the server is up and responding."""
    return {"status": "ok"}


@app.get("/me")
def me(user: TelegramUser = Depends(require_telegram_user)) -> TelegramUser:
    """Return the caller's verified Telegram identity (401 if initData is missing/invalid/stale)."""
    return user
