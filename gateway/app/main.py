"""YouThopiaOS gateway — the server-side trust boundary for the Mini App.

Exposes:
  - GET /health  — liveness probe (no auth).
  - GET /me      — the caller's verified Telegram identity, guarded by the
                   require_telegram_user dependency (401 if initData is missing,
                   forged, or stale). First endpoint that actually uses the
                   trust boundary end-to-end.
  - GET /profile — the verified caller's stored YouThopiaOS profile + XP, fetched
                   from Supabase by the verified telegram_id (404 if no account).
  - Static Mini App — Serves miniapp/dist compiled SPA at root '/' when deployed.
"""
from functools import lru_cache
import os

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from gateway.app.auth import require_telegram_user
from gateway.app.models import TelegramUser, UserProfile
from shared.config.settings import settings
from shared.db.supabase import SupabaseGateway
from shared.services.user_service import UserService

app = FastAPI(title="YouThopiaOS Gateway")

# The Mini App runs on a different origin in dev (localhost:3000) than this gateway.
# Allow dev origins, plus wildcard/same-origin in production when served directly.
_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Vite dev server
    "http://127.0.0.1:3000",  # Vite dev server IP
]

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


@lru_cache
def get_user_service() -> UserService:
    """Build the UserService once per process and reuse it — one connected Supabase
    client, not a fresh one per request. Lazy on purpose: /health and /me stay up
    even when Supabase is unconfigured; the connection is made on the first /profile
    call and cached thereafter (@lru_cache memoizes the single instance).
    """
    gateway = SupabaseGateway(settings.SUPABASE_URL, settings.SUPABASE_KEY).connect()
    return UserService(gateway)


@app.get("/profile")
async def profile(
    user: TelegramUser = Depends(require_telegram_user),
    service: UserService = Depends(get_user_service),
) -> UserProfile:
    """Return the verified caller's stored YouThopiaOS profile (profile + XP).

    The verified telegram_id is the forge-proof key — identity was already proven by
    require_telegram_user, so we trust it to look up the users row. Returns 404 if this
    Telegram user has no YouThopiaOS account yet (read-only: no provisioning here). The
    UserProfile return type filters the full DB row down to the public whitelist.
    """
    row = await service.get_by_telegram_id(user.id)
    if row is None:
        raise HTTPException(status_code=404, detail="No YouThopiaOS profile for this Telegram user")
    return UserProfile.model_validate(row)


# Single-service deployment: Mount compiled Mini App frontend at root '/'
miniapp_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../miniapp/dist"))
if os.path.exists(miniapp_dist):
    app.mount("/", StaticFiles(directory=miniapp_dist, html=True), name="miniapp")
