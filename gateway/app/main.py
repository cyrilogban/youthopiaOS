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
from starlette.exceptions import HTTPException as StarletteHTTPException

from gateway.app.auth import require_telegram_user
from gateway.app.models import (
    CommunityStats,
    EventItem,
    FeaturedVerseItem,
    LeaderboardItem,
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
from shared.services.event_service import EventService
from shared.services.moderation_service import ModerationService
from shared.services.quiz_service import QuizService
from shared.services.rank_service import RankService
from shared.services.theo_feed_service import TheoFeedService
from shared.services.user_service import UserService
from shared.services.xp_service import XPService, calculate_level


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


@lru_cache
def get_xp_service() -> XPService:
    """Build the XPService once per process and reuse it."""
    gateway = SupabaseGateway(settings.SUPABASE_URL, settings.SUPABASE_KEY).connect()
    return XPService(gateway)


@lru_cache
def get_moderation_service() -> ModerationService:
    """Build the ModerationService once per process and reuse it."""
    gateway = SupabaseGateway(settings.SUPABASE_URL, settings.SUPABASE_KEY).connect()
    return ModerationService(gateway)


@lru_cache
def get_theo_feed_service() -> TheoFeedService:
    """Build the TheoFeedService once per process and reuse it."""
    gateway = SupabaseGateway(settings.SUPABASE_URL, settings.SUPABASE_KEY).connect()
    return TheoFeedService(gateway)



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

    # Resolve official YouThopia rank from the holistic rank_score & calculate level dynamically
    total_xp = int(row.get("total_xp", 0))
    computed_level = calculate_level(total_xp)
    rank_score = int(row.get("rank_score", 0) or 0)
    rank = RankService.resolve_rank(rank_score, row.get("manual_rank_id"))

    profile_dict["total_xp"] = total_xp
    profile_dict["level"] = computed_level
    profile_dict["rank_score"] = rank_score
    profile_dict["rank_title"] = rank.title
    profile_dict["rank_tier"] = rank.tier
    profile_dict["rank_badge_color"] = rank.bg_color
    profile_dict["rank_emoji"] = rank.emoji

    # Asynchronously synchronize the users.level column in Supabase if out of sync
    if row.get("level") != computed_level:
        try:
            await service.db.update_by_id("users", row["id"], {"level": computed_level})
        except Exception:
            pass

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
        computed_level = calculate_level(xp)
        score = int(item.get("rank_score", 0) or 0)
        rank = RankService.resolve_rank(score, item.get("manual_rank_id"))
        leaderboard_items.append(LeaderboardItem(
            display_name=item.get("display_name"),
            total_xp=xp,
            level=computed_level,
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


@app.get("/api/community/stats")
async def get_community_stats(
    service: UserService = Depends(get_user_service),
) -> CommunityStats:
    """Return 100% live raw community statistics directly from Supabase."""
    try:
        users = await service.db.find_many("users", {})
        user_count = len(users)

        chats = await service.db.find_many("telegram_chats", {"is_active": True})
        group_count = len(chats)

        history = await service.db.find_many("lusy_game_history", {})
        quizzes_count = len(history)

        return CommunityStats(
            total_members=user_count,
            active_groups=group_count,
            quizzes_played=quizzes_count,
        )
    except Exception as e:
        print(f"Warning in /api/community/stats: {e}")
        return CommunityStats(total_members=0, active_groups=0, quizzes_played=0)


@app.get("/api/community/tour")
def get_community_tour() -> dict[str, Any]:
    """The unified YouThopia Tour — the same 5 pages & copy all 5 Telegram bots serve (no auth)."""
    # Imported lazily so the plain-content modules stay out of the process bootstrap graph.
    from shared.config.bot_registry import BOT_REGISTRY
    from shared.content import tour as tour_content
    from shared.utils.ui import FACEBOOK_LINK, TELEGRAM_GROUP_LINK, WHATSAPP_LINK

    bots = [
        {
            "emoji": identity.emoji,
            "name": identity.full_name,
            "short": identity.short_name,
            "tagline": identity.tagline,
            "handle": identity.handle,
            "link": identity.link,
            "responsibility": identity.responsibility,
        }
        for identity in BOT_REGISTRY.values()
    ]
    pages = [
        {"id": 1, "heading": "About YouThopia", "blocks": [
            {"label": "Who we are", "text": tour_content.ABOUT_TEXT},
            {"label": "Our Vision", "text": tour_content.VISION_TEXT},
        ]},
        {"id": 2, "heading": "Our Mission", "bullets": list(tour_content.MISSION_BULLETS)},
        {"id": 3, "heading": "Our Aims & Objectives", "bullets": list(tour_content.AIMS_BULLETS)},
        {"id": 4, "heading": "Five Pillars, One Family", "bots": bots, "note": (
            "Each pillar has its own duty — together we grow, connect, "
            "and shine as one family in CHRIST."
        )},
        {"id": 5, "heading": "Your Journey", "blocks": [{
            "label": "Grow in grace",
            "text": (
                "Every YouTopian grows through 9 ranks of grace — from The Seeker to "
                "YouThopia's Ambassador. Earn YouTopian Points (YP) by engaging in the "
                "community: quizzes, devotionals, events, and fellowship — and your "
                "Trust Score reflects your reliability and integrity."
            ),
        }], "spaces": [
            {"name": "Telegram Community", "role": "Main fellowship group", "link": TELEGRAM_GROUP_LINK},
            {"name": "WhatsApp Community", "role": "Daily encouragement on WhatsApp", "link": WHATSAPP_LINK},
            {"name": "Facebook Community", "role": "Fellowship and community updates", "link": FACEBOOK_LINK},
        ]},
    ]
    return {
        "title": tour_content.TOUR_TITLE,
        "slogan": tour_content.TOUR_SLOGAN,
        "pages": pages,
    }


@app.post("/api/community/tour/complete")
async def complete_community_tour(
    user: TelegramUser = Depends(require_telegram_user),
    users: UserService = Depends(get_user_service),
    xp_svc: XPService = Depends(get_xp_service),
    moderation: ModerationService = Depends(get_moderation_service),
) -> dict[str, Any]:
    """Marks the caller oriented and awards the one-time +50 YP welcome boost.

    Shared-channel idempotency: uses the same `orientation_completed` action and
    `onboarding_xp_{user_id}` XP idempotency key the Telegram bots use, so the
    tour's boost can only ever be awarded once per member — finishing it in the
    Mini App first, and a bot later, resolves to `already_completed` on the bot
    side (and vice versa).
    """
    row = await users.get_or_create_from_telegram({
        "telegram_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
    })
    user_id = row["id"]

    already = row.get("engagement_level") == "onboarded"
    if not already:
        try:
            actions = await users.db.find_many(
                "moderation_actions", {"user_id": user_id, "action_type": "orientation_completed"}
            )
            already = bool(actions)
        except Exception:
            pass

    if already:
        return {"status": "already_completed", "xp_awarded": 0}

    try:
        await users.set_engagement_level(user_id, "onboarded")
        await moderation.record_action(
            user_id=user_id,
            action_type="orientation_completed",
            reason="Completed the YouThopia community tour in the Mini App.",
            trust_delta=50,
        )
        await xp_svc.award_xp(
            user_id=user_id,
            amount=50,
            bot_name="susy",
            source="onboarding_tour",
            idempotency_key=f"onboarding_xp_{user_id}",
        )
    except Exception as e:
        print(f"Warning in /api/community/tour/complete: {e}")
        return {"status": "error", "xp_awarded": 0}

    return {"status": "completed", "xp_awarded": 50}


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
