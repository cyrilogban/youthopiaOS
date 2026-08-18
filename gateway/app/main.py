"""YouThopiaOS gateway — the server-side trust boundary for the Mini App.

Exposes:
  - GET /health  — liveness probe (no auth).
  - GET /me      — the caller's verified Telegram identity, guarded by the
                   require_telegram_user dependency (401 if initData is missing,
                   forged, or stale). First endpoint that actually uses the
                   trust boundary end-to-end.
"""
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from gateway.app.auth import require_telegram_user
from gateway.app.models import TelegramUser

app = FastAPI(title="YouThopiaOS Gateway")

# The Mini App runs on a different origin (dev: localhost:3000; prod: the
# BotFather HTTPS URL, added in Module 5) than this gateway. Browsers block
# cross-origin reads unless the server opts in. Allow only our own front-end
# origin and only what /me needs: GET + the Authorization header that carries
# the tma initData. No wildcard, no credentials (we use a header, not cookies).
_ALLOWED_ORIGINS = ["http://localhost:3000"]  # Vite dev server (miniapp/vite.config.ts)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_methods=["GET"],
    allow_headers=["Authorization"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe — proves the server is up and responding."""
    return {"status": "ok"}


@app.get("/me")
def me(user: TelegramUser = Depends(require_telegram_user)) -> TelegramUser:
    """Return the caller's verified Telegram identity (401 if initData is missing/invalid/stale)."""
    return user
