from __future__ import annotations

import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from core.filters import IsGlobalAdminFilter
from shared.services.container import ServiceContainer

logger = logging.getLogger(__name__)

admin_router = Router(name="global_admin_commands")


@admin_router.message(Command("stats"), IsGlobalAdminFilter())
async def handle_global_stats(message: Message, services: ServiceContainer) -> None:
    """Renders high-level community statistics across all YouThopiaOS bots."""
    stats = await services.admin.get_global_stats()
    breakdown = await services.admin.get_bot_breakdown()

    text = (
        "👑 <b>YouThopiaOS Admin Summary</b>\n\n"
        "📊 <b>Community Reach</b>\n"
        f"• Total Members: <b>{stats['total_users']}</b>\n"
        f"• Active Groups: <b>{stats['active_groups']}</b>\n"
        f"• User Subscriptions: <b>{stats['user_subscriptions']}</b>\n"
        f"• Group Subscriptions: <b>{stats['chat_subscriptions']}</b>\n\n"
        "🤖 <b>Bot Active Group Reach</b>\n"
        f"• 📖 Theo: <b>{breakdown.get('theo', {}).get('active_chats', 0)}</b> groups\n"
        f"• 🎮 Lusy: <b>{breakdown.get('lusy', {}).get('active_chats', 0)}</b> groups\n"
        f"• 🛡️ Pete: <b>{breakdown.get('pete', {}).get('active_chats', 0)}</b> groups\n"
        f"• 📅 Eddy: <b>{breakdown.get('eddy', {}).get('active_chats', 0)}</b> groups\n"
        f"• 🌸 Susy: <b>{breakdown.get('susy', {}).get('active_chats', 0)}</b> groups\n\n"
        "<i>Use <code>/botstats</code> or <code>/groups</code> for deeper details.</i>"
    )
    await message.answer(text, parse_mode="HTML")


@admin_router.message(Command("botstats"), IsGlobalAdminFilter())
async def handle_bot_stats(message: Message, services: ServiceContainer) -> None:
    """Renders detailed performance breakdown per bot."""
    breakdown = await services.admin.get_bot_breakdown()

    lines = ["🤖 <b>YouThopiaOS Bot Performance Breakdown</b>\n"]
    bot_display_names = {
        "theo": "📖 Theo (Daily Verse)",
        "lusy": "🎮 Lusy (Games & Fellowship)",
        "pete": "🛡️ Pete (Moderation)",
        "eddy": "📅 Eddy (Events & Calendar)",
        "susy": "🌸 Susy (Music & Hostess)",
    }

    for bot_key, display in bot_display_names.items():
        data = breakdown.get(bot_key, {})
        chats = data.get("active_chats", 0)
        subs = data.get("active_subs", 0)
        lines.append(f"• <b>{display}</b>\n  Active Chats: <code>{chats}</code> | Active Subscriptions: <code>{subs}</code>")

    await message.answer("\n\n".join(lines), parse_mode="HTML")


@admin_router.message(Command("groups"), IsGlobalAdminFilter())
async def handle_groups_list(message: Message, services: ServiceContainer) -> None:
    """Renders a list of all active registered groups in YouThopiaOS."""
    groups = await services.admin.get_active_groups_list()

    if not groups:
        await message.answer("🏰 No active registered groups found in YouThopiaOS.")
        return

    lines = [f"🏰 <b>Active Groups Directory ({len(groups)})</b>\n"]
    for g in groups:
        title = g.get("title") or "Unnamed Group"
        chat_id = g.get("telegram_chat_id") or g.get("id")
        official = " ⭐ (Official)" if g.get("is_official") else ""
        lines.append(f"• <b>{title}</b>{official}\n  Telegram ID: <code>{chat_id}</code>")

    await message.answer("\n\n".join(lines), parse_mode="HTML")
