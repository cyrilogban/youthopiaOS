"""YouThopiaOS gateway — the server-side trust boundary & Supabase sync API for the Mini App.

Exposes:
  - GET /health         — liveness probe (no auth).
  - GET /me             — verified Telegram identity.
  - GET /profile        — verified user's stored YouThopiaOS profile from Supabase.
  - GET /api/settings   — verified user's saved preferences (translation, daily devotional).
  - PUT /api/settings   — update verified user's preferences in Supabase.
  - GET /api/votd       — live Verse of the Day text & reference from Supabase.
  - GET /api/theo/*     — Theo featured, saved, liked, and shared verses.
  - Static Mini App     — Serves miniapp/dist compiled SPA at root '/' when deployed.
"""
import asyncio
from contextlib import asynccontextmanager
from functools import lru_cache
import os
from typing import Any

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from gateway.app.auth import require_telegram_user
from gateway.app.models import (
    FeaturedVerseItem,
    LikeVerseRequest,
    SaveVerseRequest,
    ShareVerseRequest,
    TelegramUser,
    UserProfile,
    UserSettings,
    VotdItem,
)
from shared.config.settings import settings
from shared.db.supabase import SupabaseGateway
from shared.services.theo_feed_service import TheoFeedService
from shared.services.user_service import UserService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager — starts configured Telegram bots concurrently in background
    tasks when the FastAPI web server boots, ensuring a single process runs both the
    bots and the gateway web server.
    """
    bot_task = None
    try:
        from core.bot_manager import run as run_bots
        bot_task = asyncio.create_task(run_bots())
    except Exception as e:
        print(f"Warning: Could not start bot manager in lifespan: {e}")
    yield
    if bot_task:
        bot_task.cancel()


app = FastAPI(title="YouThopiaOS Gateway", lifespan=lifespan)

_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Vite dev server
    "http://127.0.0.1:3000",  # Vite dev server IP
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_methods=["GET", "PUT", "POST"],
    allow_headers=["Authorization", "Content-Type"],
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
    """Build the UserService once per process and reuse it."""
    gateway = SupabaseGateway(settings.SUPABASE_URL, settings.SUPABASE_KEY).connect()
    return UserService(gateway)


@lru_cache
def get_theo_feed_service() -> TheoFeedService:
    """Build the TheoFeedService once per process and reuse it."""
    gateway = SupabaseGateway(settings.SUPABASE_URL, settings.SUPABASE_KEY).connect()
    return TheoFeedService(gateway)



@app.get("/profile", response_model_exclude_defaults=True)
async def profile(
    user: TelegramUser = Depends(require_telegram_user),
    service: UserService = Depends(get_user_service),
) -> UserProfile:
    """Return the verified caller's personal profile for Theo."""
    # Always synchronize Supabase profile with the verified Telegram user data
    row = await service.get_or_create_from_telegram({
        "telegram_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
    })

    return UserProfile(display_name=row.get("display_name"))


@app.get("/api/settings")
async def get_settings(
    user: TelegramUser = Depends(require_telegram_user),
    service: UserService = Depends(get_user_service),
) -> UserSettings:
    """Return the verified caller's saved settings (translation preference & daily verse reminder)."""
    row = await service.get_by_telegram_id(user.id)
    if not row:
        return UserSettings()

    user_id = row["id"]
    state = await service.get_user_state(user_id, "theo")
    sub = await service.get_subscription(user_id, "theo", "daily_devotional")

    translation = state.get("translation", "KJV").upper()
    daily_devotional = sub.get("enabled", True) if sub else True

    return UserSettings(translation=translation, daily_devotional=daily_devotional)


@app.put("/api/settings")
async def update_settings(
    new_settings: UserSettings,
    user: TelegramUser = Depends(require_telegram_user),
    service: UserService = Depends(get_user_service),
) -> UserSettings:
    """Update the verified caller's saved settings in Supabase."""
    row = await service.get_by_telegram_id(user.id)
    if not row:
        # Provision user if missing
        row = await service.get_or_create_from_telegram({"telegram_id": user.id, "first_name": user.first_name})

    user_id = row["id"]
    clean_trans = new_settings.translation.lower()

    # Update translation state for Theo in Supabase
    state = await service.get_user_state(user_id, "theo")
    state["translation"] = clean_trans
    await service.set_user_state(user_id, "theo", state)

    # Update daily devotional subscription in Supabase
    await service.set_subscription(user_id, "theo", "daily_devotional", enabled=new_settings.daily_devotional)

    return UserSettings(translation=clean_trans.upper(), daily_devotional=new_settings.daily_devotional)


@app.get("/api/votd")
async def get_votd(
    translation: str = "KJV",
    service: UserService = Depends(get_user_service),
) -> VotdItem:
    """Return today's active Verse of the Day dynamically from Supabase + Bible API."""
    clean_trans = translation.lower()
    try:
        from bots.theo.services.devotional_service import VOTDService
        votd_svc = VOTDService(service.db)
        item = await votd_svc.get_todays_reference()
        ref = item.get("reference", "John 14:27") if item else "John 14:27"

        text = await votd_svc.fetch_bible_text(ref, translation=clean_trans)
        if text:
            return VotdItem(reference=ref, text=text, translation=translation.upper())
    except Exception as e:
        print(f"Warning in /api/votd: {e}")

    # Fallback default if external API is unreachable
    return VotdItem(
        reference="John 14:27",
        text="Peace I leave with you, my peace I give unto you: not as the world giveth, give I unto you. Let not your heart be troubled, neither let it be afraid.",
        translation=translation.upper(),
    )


@app.get("/api/theo/featured")
async def get_theo_featured(
    feed_svc: TheoFeedService = Depends(get_theo_feed_service),
) -> list[FeaturedVerseItem]:
    """Return active curated featured verses from Supabase."""
    rows = await feed_svc.get_featured_verses(limit=10)
    return [
        FeaturedVerseItem(
            id=str(r.get("id")),
            verse_reference=r["verse_reference"],
            verse_text=r["verse_text"],
            translation=r.get("translation", "KJV"),
            scheduled_date=str(r.get("scheduled_date")),
            style_override=r.get("style_override"),
        )
        for r in rows
    ]


@app.get("/api/theo/saved")
async def get_theo_saved(
    user: TelegramUser = Depends(require_telegram_user),
    feed_svc: TheoFeedService = Depends(get_theo_feed_service),
) -> list[dict[str, Any]]:
    """Return all saved/bookmarked verses for the verified caller."""
    return await feed_svc.get_saved_verses(user.id)


@app.post("/api/theo/saved")
async def save_theo_verse(
    req: SaveVerseRequest,
    user: TelegramUser = Depends(require_telegram_user),
    feed_svc: TheoFeedService = Depends(get_theo_feed_service),
) -> dict[str, Any]:
    """Save/bookmark a verse in Supabase for the verified caller."""
    return await feed_svc.save_verse(
        telegram_id=user.id,
        verse_reference=req.verse_reference,
        verse_text=req.verse_text,
        translation=req.translation,
    )


@app.post("/api/theo/saved/remove")
async def unsave_theo_verse(
    req: SaveVerseRequest,
    user: TelegramUser = Depends(require_telegram_user),
    feed_svc: TheoFeedService = Depends(get_theo_feed_service),
) -> dict[str, Any]:
    """Remove a bookmarked verse in Supabase for the verified caller."""
    removed = await feed_svc.unsave_verse(telegram_id=user.id, verse_reference=req.verse_reference)
    return {"success": removed}


@app.get("/api/theo/likes")
async def get_theo_likes(
    user: TelegramUser = Depends(require_telegram_user),
    feed_svc: TheoFeedService = Depends(get_theo_feed_service),
) -> list[str]:
    """Return list of verse references liked by the verified caller."""
    return await feed_svc.get_user_likes(user.id)


@app.post("/api/theo/likes/toggle")
async def toggle_theo_like(
    req: LikeVerseRequest,
    user: TelegramUser = Depends(require_telegram_user),
    feed_svc: TheoFeedService = Depends(get_theo_feed_service),
) -> dict[str, Any]:
    """Toggle like on a verse in Supabase. Returns {"liked": bool}."""
    liked = await feed_svc.toggle_like(telegram_id=user.id, verse_reference=req.verse_reference)
    return {"liked": liked}


@app.post("/api/theo/share")
async def log_theo_share(
    req: ShareVerseRequest,
    user: TelegramUser = Depends(require_telegram_user),
    users: UserService = Depends(get_user_service),
    feed_svc: TheoFeedService = Depends(get_theo_feed_service),
) -> dict[str, Any]:
    """Log a verse share event in analytics_events in Supabase."""
    row = await users.get_or_create_from_telegram({"telegram_id": user.id, "first_name": user.first_name})
    user_uuid = row["id"]
    return await feed_svc.log_share_event(user_uuid=user_uuid, verse_reference=req.verse_reference)


# Single-service deployment: Mount compiled Mini App frontend at root '/'
class SPAStaticFiles(StaticFiles):
    """Serve the built Mini App and fall back to index.html for client-side routes.

    Clean routes like /theo have no file on disk, so any 404 for a path without a
    file extension is resolved by returning the SPA shell, letting React Router
    handle it. Real missing assets (with an extension) still 404.
    """

    async def get_response(self, path, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404 and "." not in os.path.basename(path):
                return await super().get_response("index.html", scope)
            raise


miniapp_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../miniapp/dist"))
if os.path.exists(miniapp_dist):
    app.mount("/", SPAStaticFiles(directory=miniapp_dist, html=True), name="miniapp")
