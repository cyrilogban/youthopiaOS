"""YouThopiaOS gateway — the server-side trust boundary & Supabase sync API for the Mini App.

Exposes:
  - GET /health         — liveness probe (no auth).
  - GET /me             — verified Telegram identity.
  - GET /profile        — verified user's stored YouThopiaOS profile + XP from Supabase.
  - GET /api/settings   — verified user's saved preferences (translation, daily devotional).
  - PUT /api/settings   — update verified user's preferences in Supabase.
  - GET /api/leaderboard— live top community rankings from Supabase users table.
  - GET /api/events     — live upcoming community gatherings & schedule from Supabase.
  - GET /api/votd       — live Verse of the Day text & reference from Supabase.
  - Static Mini App     — Serves miniapp/dist compiled SPA at root '/' when deployed.
"""
import asyncio
from contextlib import asynccontextmanager
from functools import lru_cache
import os
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from gateway.app.auth import require_telegram_user
from gateway.app.models import (
    EventItem,
    LeaderboardItem,
    TelegramUser,
    UserProfile,
    UserSettings,
    VotdItem,
)
from shared.config.settings import settings
from shared.db.supabase import SupabaseGateway
from shared.services.event_service import EventService
from shared.services.quiz_service import QuizService
from shared.services.rank_service import RankService
from shared.services.user_service import UserService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager — starts all 5 Telegram bots concurrently in background
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
def get_quiz_service() -> QuizService:
    """Build the QuizService once per process and reuse it."""
    gateway = SupabaseGateway(settings.SUPABASE_URL, settings.SUPABASE_KEY).connect()
    return QuizService(gateway)


@lru_cache
def get_event_service() -> EventService:
    """Build the EventService once per process and reuse it."""
    gateway = SupabaseGateway(settings.SUPABASE_URL, settings.SUPABASE_KEY).connect()
    return EventService(gateway)


@app.get("/profile")
async def profile(
    user: TelegramUser = Depends(require_telegram_user),
    service: UserService = Depends(get_user_service),
    quiz_svc: QuizService = Depends(get_quiz_service),
) -> UserProfile:
    """Return the verified caller's stored YouThopiaOS profile (profile + XP + quiz stats + official rank)."""
    # Always synchronize Supabase profile with the verified Telegram user data
    row = await service.get_or_create_from_telegram({
        "telegram_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
    })

    stats = await quiz_svc.get_user_quiz_stats(row["id"])
    profile_dict = dict(row)
    profile_dict["quizzes_played"] = stats.get("quizzes_played", 0)
    profile_dict["accuracy_pct"] = stats.get("accuracy_pct", 100)

    # Resolve official YouThopia rank from RankService
    total_xp = int(row.get("total_xp", 0))
    manual_rank = row.get("manual_rank_id")
    rank = RankService.resolve_rank(total_xp, manual_rank)

    profile_dict["rank_title"] = rank.title
    profile_dict["rank_tier"] = rank.tier
    profile_dict["rank_badge_color"] = rank.bg_color
    profile_dict["rank_emoji"] = rank.emoji

    return UserProfile.model_validate(profile_dict)


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


@app.get("/api/leaderboard")
async def get_leaderboard(
    service: UserService = Depends(get_user_service),
) -> list[LeaderboardItem]:
    """Return top 10 community members ordered by total_xp descending from Supabase with official rank badges."""
    items = await service.get_leaderboard(limit=10)
    leaderboard_items = []
    for item in items:
        xp = int(item.get("total_xp", 0))
        manual_rank = item.get("manual_rank_id")
        rank = RankService.resolve_rank(xp, manual_rank)
        leaderboard_items.append(LeaderboardItem(
            display_name=item.get("display_name"),
            total_xp=xp,
            level=int(item.get("level", 1)),
            rank_title=rank.title,
            rank_badge_color=rank.bg_color,
            rank_emoji=rank.emoji,
        ))
    return leaderboard_items


@app.get("/api/events")
async def get_events(
    event_svc: EventService = Depends(get_event_service),
) -> list[EventItem]:
    """Return live upcoming community events from Supabase."""
    try:
        latest = await event_svc.get_latest_event()
        if latest:
            return [EventItem(
                id=latest.get("id"),
                title=latest.get("title", "Weekly Bible Study & Discussion"),
                starts_at=latest.get("starts_at", "Sundays at 6:00 PM UTC"),
                category="Community Gathering",
                location="Telegram Main Channel"
            )]
    except Exception:
        pass

    # Fallback to default community schedule list
    return [
        EventItem(
            title="Weekly Bible Study & Discussion",
            starts_at="Sundays at 6:00 PM UTC",
            category="Community Gathering",
            location="Telegram Main Channel",
        ),
        EventItem(
            title="Midweek Prayer & Intercession",
            starts_at="Wednesdays at 7:30 PM UTC",
            category="Prayer Session",
            location="Voice Chat Room",
        ),
        EventItem(
            title="Weekend Scripture Challenge",
            starts_at="Saturdays at 4:00 PM UTC",
            category="Community Quiz",
            location="Lusy Bot Channel",
        ),
    ]


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


# Single-service deployment: Mount compiled Mini App frontend at root '/'
miniapp_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../miniapp/dist"))
if os.path.exists(miniapp_dist):
    app.mount("/", StaticFiles(directory=miniapp_dist, html=True), name="miniapp")
