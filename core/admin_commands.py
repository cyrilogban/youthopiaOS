from __future__ import annotations

import os
import logging
from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeChat, Message
from core.filters import IsGlobalAdminFilter
from shared.services.container import ServiceContainer

logger = logging.getLogger(__name__)

# Native side menu commands for each bot to merge with admin commands
BOT_NATIVE_COMMANDS = {
    "theo": [
        BotCommand(command="start", description="Wake Up Theo"),
        BotCommand(command="app", description="Open YouThopia Community Mini App"),
        BotCommand(command="help", description="Show help information"),
        BotCommand(command="subscribe", description="Subscribe to daily verses"),
        BotCommand(command="unsubscribe", description="Unsubscribe from daily verses"),
        BotCommand(command="send_votd", description="Send Today's Verse (Admin)"),
    ],
    "pete": [
        BotCommand(command="start", description="Meet Pete"),
        BotCommand(command="app", description="Open YouThopia Community Mini App"),
        BotCommand(command="appeal", description="Submit Appeal"),
        BotCommand(command="profile", description="View your profile"),
        BotCommand(command="help", description="Pete Safety Guide"),
        BotCommand(command="warn", description="Issue a warning"),
        BotCommand(command="mute", description="Revoke typing permissions"),
        BotCommand(command="kick", description="Remove user from group"),
        BotCommand(command="ban", description="Permanently ban user"),
        BotCommand(command="unban", description="Lift a ban"),
        BotCommand(command="unmute", description="Lift a mute"),
        BotCommand(command="lock", description="Lock the group chat"),
        BotCommand(command="unlock", description="Unlock the group chat"),
        BotCommand(command="biblestudy", description="Silence chat for teaching"),
        BotCommand(command="endbiblestudy", description="Unlock chat after teaching"),
    ],
    "lusy": [
        BotCommand(command="start", description="Meet Lusy"),
        BotCommand(command="app", description="Open YouThopia Community Mini App"),
        BotCommand(command="games", description="Browse Bible Games"),
        BotCommand(command="playgame", description="Choose and start a Bible game"),
        BotCommand(command="quit", description="Quit active game session"),
        BotCommand(command="leaderboard", description="View global leaderboard"),
        BotCommand(command="yp", description="Check your current YP and Level"),
        BotCommand(command="profile", description="View your profile"),
        BotCommand(command="help", description="How to play and earn YP"),
    ],
    "susy": [
        BotCommand(command="start", description="Meet Susy"),
        BotCommand(command="app", description="Open YouThopia Community Mini App"),
        BotCommand(command="where", description="Community topic directory & guide"),
        BotCommand(command="profile", description="View your profile"),
        BotCommand(command="help", description="Susy Hostess Guide"),
    ],
    "eddy": [
        BotCommand(command="start", description="Open Ed main dashboard"),
        BotCommand(command="app", description="Open YouThopia Community Mini App"),
        BotCommand(command="calendar", description="View this week's event schedule"),
        BotCommand(command="my_events", description="View events I am attending"),
        BotCommand(command="addbirthday", description="Add your birthday"),
        BotCommand(command="upcomingbirthday", description="View Upcoming Birthdays"),
        BotCommand(command="deletebirthday", description="Delete your registered birthday"),
        BotCommand(command="profile", description="View your profile"),
        BotCommand(command="help", description="Show Ed's instructions"),
    ],
}


def create_admin_router(bot_name: str = "global") -> Router:
    """Creates a fresh router with admin commands attached for a given bot."""
    router = Router(name=f"{bot_name}_admin_commands")

    @router.startup()
    async def on_admin_startup(bot: Bot) -> None:
        admin_commands_list = [
            BotCommand(command="stats", description="👑 Global Admin Statistics"),
            BotCommand(command="botstats", description="🤖 Per-Bot Performance Breakdown"),
            BotCommand(command="groups", description="🏰 Active Groups Directory"),
            BotCommand(command="setrank", description="👑 Appoint User Rank (Admin)"),
        ]

        admin_ids_str = os.getenv("ADMIN_OWNER_ID") or os.getenv("ADMIN_IDS") or ""
        admin_ids = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip().isdigit()]

        if bot_name.lower() != "eddy":
            for admin_id in admin_ids:
                try:
                    await bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=admin_id))
                except Exception:
                    pass
            return

        native_cmds = BOT_NATIVE_COMMANDS.get(bot_name.lower(), [])

        for admin_id in admin_ids:
            try:
                # Fetch existing private chat commands configured by this bot, fallback to static mapping
                existing_cmds = await bot.get_my_commands(scope=BotCommandScopeAllPrivateChats())
                base_cmds = existing_cmds if existing_cmds else native_cmds

                existing_names = {c.command for c in (base_cmds or [])}
                new_cmds = [c for c in admin_commands_list if c.command not in existing_names]
                full_admin_menu = list(base_cmds or []) + new_cmds

                await bot.set_my_commands(full_admin_menu, scope=BotCommandScopeChat(chat_id=admin_id))
                logger.info("Registered admin menu commands (%d items) for admin %d on %s.", len(full_admin_menu), admin_id, bot_name)
            except Exception as e:
                logger.warning(f"Failed to set admin commands menu for admin_id {admin_id}: {e}")

    @router.message(Command("stats"), IsGlobalAdminFilter())
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
            f"• 💬 Susy: <b>{breakdown.get('susy', {}).get('active_chats', 0)}</b> groups\n\n"
            "<i>Use <code>/botstats</code> or <code>/groups</code> for deeper details.</i>"
        )
        await message.answer(text, parse_mode="HTML")

    @router.message(Command("botstats"), IsGlobalAdminFilter())
    async def handle_bot_stats(message: Message, services: ServiceContainer) -> None:
        """Renders detailed performance breakdown per bot."""
        breakdown = await services.admin.get_bot_breakdown()

        lines = ["🤖 <b>YouThopiaOS Bot Performance Breakdown</b>\n"]
        bot_display_names = {
            "theo": "📖 Theo (Daily Verse)",
            "lusy": "🎮 Lusy (Games & Fellowship)",
            "pete": "🛡️ Pete (Moderation)",
            "eddy": "📅 Eddy (Events & Calendar)",
            "susy": "💬 Susy (Hostess & Onboarding)",
        }

        for bot_key, display in bot_display_names.items():
            data = breakdown.get(bot_key, {})
            chats = data.get("active_chats", 0)
            subs = data.get("active_subs", 0)
            lines.append(f"• <b>{display}</b>\n  Active Chats: <code>{chats}</code> | Active Subscriptions: <code>{subs}</code>")

        await message.answer("\n\n".join(lines), parse_mode="HTML")

    @router.message(Command("groups"), IsGlobalAdminFilter())
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

    @router.message(Command("setrank"), IsGlobalAdminFilter())
    async def handle_set_rank(message: Message, services: ServiceContainer) -> None:
        """Sets or resets a member's official YouTopian rank.
        Usage: /setrank @username <rank_id> or /setrank <telegram_id> <rank_id>
        Or reply to a user message: /setrank <rank_id>
        """
        args = (message.text or "").split()[1:]
        target_account = None
        rank_arg = None

        if message.reply_to_message and message.reply_to_message.from_user:
            target_user_from = message.reply_to_message.from_user
            target_account = await services.supabase.find_one("telegram_accounts", "telegram_id", target_user_from.id)
            if args:
                rank_arg = args[0].lower()
        elif len(args) >= 2:
            identifier = args[0]
            rank_arg = args[1].lower()
            if identifier.startswith("@"):
                username = identifier.lstrip("@")
                target_account = await services.supabase.find_one("telegram_accounts", "username", username)
            elif identifier.isdigit():
                target_account = await services.supabase.find_one("telegram_accounts", "telegram_id", int(identifier))
            else:
                target_account = await services.supabase.find_one("telegram_accounts", "username", identifier)

        if not target_account:
            valid_ranks = ", ".join([f"<code>{r.id}</code>" for r in services.ranks.get_all_ranks()])
            await message.answer(
                "⚠️ <b>Usage:</b>\n"
                "• <code>/setrank @username &lt;rank&gt;</code>\n"
                "• <code>/setrank &lt;telegram_id&gt; &lt;rank&gt;</code>\n"
                "• Reply to a user: <code>/setrank &lt;rank&gt;</code>\n\n"
                f"<b>Available Ranks:</b>\n{valid_ranks}, <code>auto</code> (reset to automated XP)",
                parse_mode="HTML"
            )
            return

        user_id = target_account["user_id"]
        user = await services.supabase.get_by_id("users", user_id)
        display_name = (user or {}).get("display_name") or target_account.get("first_name") or "YouTopian"

        if rank_arg == "auto":
            await services.supabase.update_by_id("users", user_id, {"manual_rank_id": None})
            xp = int((user or {}).get("total_xp", 0))
            resolved = services.ranks.resolve_rank(xp)
            await message.answer(
                f"✅ <b>Rank Reset to Automated!</b>\n\n"
                f"👤 Member: <b>{display_name}</b>\n"
                f"🏅 Current XP Rank: <b>{resolved.emoji} {resolved.title}</b> ({resolved.tier})\n"
                f"⭐ XP: <code>{xp} YP</code>",
                parse_mode="HTML"
            )
            return

        rank = services.ranks.get_rank_by_id(rank_arg or "")
        if not rank:
            valid_ranks = ", ".join([f"<code>{r.id}</code>" for r in services.ranks.get_all_ranks()])
            await message.answer(
                f"❌ Invalid rank <code>{rank_arg}</code>.\n\n"
                f"<b>Valid options:</b>\n{valid_ranks}, <code>auto</code>",
                parse_mode="HTML"
            )
            return

        # Update manual_rank_id in Supabase
        await services.supabase.update_by_id("users", user_id, {"manual_rank_id": rank.id})

        announcement = (
            f"👑 <b>Official Rank Appointment!</b> 🎉\n\n"
            f"👤 Member: <b>{display_name}</b>\n"
            f"🏅 New Rank: <b>{rank.emoji} {rank.title}</b>\n"
            f"🏛️ Tier: <b>{rank.tier}</b>\n"
            f"📜 <i>{rank.description}</i>\n\n"
            f"<i>Rank updated across all bots and the YouThopia Mini App.</i>"
        )
        sent_msg = await message.answer(announcement, parse_mode="HTML")
        if message.chat.type != "private":
            from core.telegram_runtime import delayed_delete_message
            import asyncio
            asyncio.create_task(delayed_delete_message(message.bot, message.chat.id, sent_msg.message_id, delay_seconds=180))

    return router
