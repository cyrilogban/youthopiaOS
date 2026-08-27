import logging
from typing import Any
from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    ChatPermissions,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ChatMemberUpdated,
)
from aiogram.filters import Command, CommandObject, Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
import os
from shared.services.container import ServiceContainer
from core.telegram_runtime import register_group_chat, register_chat
from shared.utils.ui import (
    BOT_FAMILY_DIRECTORY_TEXT,
    get_community_links_keyboard,
    render_shared_profile_card,
    send_community_exploration_page,
    handle_global_onboarding_callback,
    handle_group_profile_acknowledgment,
)
from bots.pete.utils.keyboards import (
    build_pete_reply_keyboard,
    build_pete_start_inline_keyboard,
    build_pete_group_welcome_keyboard,
    build_pete_member_welcome_keyboard,
    build_pete_farewell_keyboard,
    build_pete_captcha_inline_keyboard,
    build_pete_post_captcha_group_keyboard,
)

logger = logging.getLogger(__name__)

router = Router()

from core.filters import IsAdminFilter


async def self_destruct_message(bot: Bot, chat_id: int, message_id: int, delay_seconds: int = 10) -> None:
    await asyncio.sleep(delay_seconds)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

# -----------------------------------------------------------------------------
# CORE ADMIN COMMANDS
# -----------------------------------------------------------------------------

@router.message(Command("warn"), IsAdminFilter())
async def handle_warn(message: Message, command: CommandObject, services: ServiceContainer) -> None:
    if not message.reply_to_message:
        await message.reply("🛡️ You must reply to the user's message to issue a warning.")
        return
        
    target_user = message.reply_to_message.from_user
    if target_user.id == message.bot.id:
        await message.reply("I cannot warn myself!")
        return
        
    reason = command.args or "No reason provided."
    
    # 1. Resolve Identities
    chat_record = await register_group_chat(message, services, "pete")
    admin_record = await services.identity.resolve_telegram_user(message.from_user)
    target_record = await services.identity.resolve_telegram_user(target_user)
    
    if not chat_record:
        return
        
    # 2. Log Action & Apply Penalty (-10 Trust Points for a warning)
    await services.moderation.record_action(
        user_id=target_record["id"],
        chat_id=chat_record["id"],
        moderator_user_id=admin_record["id"],
        action_type="warn",
        reason=reason,
        trust_delta=-10
    )
    
    # 3. Check threshold logic (Automated Justice)
    warnings = await services.moderation.get_user_warnings_count(target_record["id"], chat_record["id"])
    
    response_text = f"⚠️ **{target_user.first_name}** has been warned.\n**Reason:** {reason}\n**Total Warnings:** {warnings}"
    
    if warnings >= 5:
        try:
            await message.chat.ban(user_id=target_user.id)
            response_text += "\n\n🔨 **Automated Justice:** User reached 5 warnings and has been permanently banned."
            
            await services.moderation.record_action(
                user_id=target_record["id"],
                chat_id=chat_record["id"],
                moderator_user_id=admin_record["id"],
                action_type="ban",
                reason="Automated Justice: Reached 5 warnings.",
                trust_delta=-50
            )
        except Exception as e:
            logger.error(f"Automated ban failed: {e}")
    elif warnings >= 3:
        # Automated Mute on 3rd warning
        from aiogram.types import ChatPermissions
        try:
            await message.chat.restrict(user_id=target_user.id, permissions=ChatPermissions(can_send_messages=False))
            response_text += "\n\n🔇 **Automated Justice:** User reached 3 warnings and has been muted."
            
            await services.moderation.record_action(
                user_id=target_record["id"],
                chat_id=chat_record["id"],
                moderator_user_id=admin_record["id"],
                action_type="mute",
                reason="Automated Justice: Reached 3 warnings.",
                trust_delta=-20
            )
        except Exception as e:
            logger.error(f"Automated mute failed: {e}")
            
    await message.reply(response_text, parse_mode="Markdown")

@router.message(Command("kick"), IsAdminFilter())
async def handle_kick(message: Message, command: CommandObject, services: ServiceContainer) -> None:
    if not message.reply_to_message:
        await message.reply("🛡️ You must reply to the user's message to kick them.")
        return
        
    target_user = message.reply_to_message.from_user
    if target_user.id == message.bot.id:
        await message.reply("I cannot kick myself!")
        return
        
    reason = command.args or "No reason provided."
        
    try:
        # Resolve Identities & Log (-30 Trust Points)
        chat_record = await register_group_chat(message, services, "pete")
        admin_record = await services.identity.resolve_telegram_user(message.from_user)
        target_record = await services.identity.resolve_telegram_user(target_user)
        
        if chat_record:
            await services.moderation.record_action(
                user_id=target_record["id"],
                chat_id=chat_record["id"],
                moderator_user_id=admin_record["id"],
                action_type="kick",
                reason=reason,
                trust_delta=-30
            )

        # A "kick" in Telegram is a ban followed immediately by an unban
        await message.chat.ban(user_id=target_user.id)
        await message.chat.unban(user_id=target_user.id)
        await message.reply(f"👢 {target_user.first_name} has been kicked from the community.\n**Reason:** {reason}", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Kick failed: {e}")
        await message.reply("❌ Failed to kick user. Make sure I have admin rights.")

@router.message(Command("ban"), IsAdminFilter())
async def handle_ban(message: Message, command: CommandObject, services: ServiceContainer) -> None:
    if not message.reply_to_message:
        await message.reply("🛡️ You must reply to the user's message to ban them.")
        return
        
    target_user = message.reply_to_message.from_user
    if target_user.id == message.bot.id:
        await message.reply("I cannot ban myself!")
        return
        
    reason = command.args or "No reason provided."
        
    try:
        # Resolve Identities & Log (-50 Trust Points)
        chat_record = await register_group_chat(message, services, "pete")
        admin_record = await services.identity.resolve_telegram_user(message.from_user)
        target_record = await services.identity.resolve_telegram_user(target_user)
        
        if chat_record:
            await services.moderation.record_action(
                user_id=target_record["id"],
                chat_id=chat_record["id"],
                moderator_user_id=admin_record["id"],
                action_type="ban",
                reason=reason,
                trust_delta=-50
            )

        await message.chat.ban(user_id=target_user.id)
        await message.reply(f"🔨 {target_user.first_name} has been permanently banned.\n**Reason:** {reason}", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ban failed: {e}")
        await message.reply("❌ Failed to ban user. Make sure I have admin rights.")

@router.message(Command("mute"), IsAdminFilter())
async def handle_mute(message: Message, command: CommandObject, services: ServiceContainer) -> None:
    if not message.reply_to_message:
        await message.reply("🛡️ You must reply to the user's message to mute them.")
        return
        
    target_user = message.reply_to_message.from_user
    if target_user.id == message.bot.id:
        await message.reply("I cannot mute myself!")
        return
        
    reason = command.args or "No reason provided."
    until_date = None
    duration_str = ""
    
    if command.args:
        args_parts = command.args.split(maxsplit=1)
        import re
        from datetime import datetime, timedelta
        
        match = re.match(r"^(\d+)([smhd])$", args_parts[0].lower())
        if match:
            val = int(match.group(1))
            unit = match.group(2)
            td = None
            if unit == 's': td = timedelta(seconds=val); duration_str = f" for {val} seconds"
            elif unit == 'm': td = timedelta(minutes=val); duration_str = f" for {val} minutes"
            elif unit == 'h': td = timedelta(hours=val); duration_str = f" for {val} hours"
            elif unit == 'd': td = timedelta(days=val); duration_str = f" for {val} days"
            
            until_date = datetime.now() + td
            reason = args_parts[1] if len(args_parts) > 1 else "No reason provided."
        
    try:
        # Resolve Identities & Log (-20 Trust Points)
        chat_record = await register_group_chat(message, services, "pete")
        admin_record = await services.identity.resolve_telegram_user(message.from_user)
        target_record = await services.identity.resolve_telegram_user(target_user)
        
        if chat_record:
            await services.moderation.record_action(
                user_id=target_record["id"],
                chat_id=chat_record["id"],
                moderator_user_id=admin_record["id"],
                action_type="mute",
                reason=reason,
                trust_delta=-20
            )

        permissions = ChatPermissions(can_send_messages=False)
        await message.chat.restrict(user_id=target_user.id, permissions=permissions, until_date=until_date)
        await message.reply(f"🔇 {target_user.first_name} has been muted{duration_str}.\n**Reason:** {reason}", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Mute failed: {e}")
        await message.reply("❌ Failed to mute user. Make sure I have admin rights.")

@router.message(Command("unban"), IsAdminFilter())
async def handle_unban(message: Message, command: CommandObject, services: ServiceContainer) -> None:
    if not message.reply_to_message:
        await message.reply("🛡️ You must reply to the user's message to unban them.")
        return
        
    target_user = message.reply_to_message.from_user
    reason = command.args or "Forgiveness granted."
        
    try:
        chat_record = await register_group_chat(message, services, "pete")
        admin_record = await services.identity.resolve_telegram_user(message.from_user)
        target_record = await services.identity.resolve_telegram_user(target_user)
        
        if chat_record:
            await services.moderation.record_action(
                user_id=target_record["id"],
                chat_id=chat_record["id"],
                moderator_user_id=admin_record["id"],
                action_type="unban",
                reason=reason,
                trust_delta=0
            )

        await message.chat.unban(user_id=target_user.id)
        await message.reply(f"🕊️ {target_user.first_name} has been forgiven and unbanned.\n**Reason:** {reason}", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Unban failed: {e}")
        await message.reply("❌ Failed to unban user. Make sure I have admin rights.")

@router.message(Command("unmute"), IsAdminFilter())
async def handle_unmute(message: Message, command: CommandObject, services: ServiceContainer) -> None:
    if not message.reply_to_message:
        await message.reply("🛡️ You must reply to the user's message to unmute them.")
        return
        
    target_user = message.reply_to_message.from_user
    reason = command.args or "Forgiveness granted."
        
    try:
        chat_record = await register_group_chat(message, services, "pete")
        admin_record = await services.identity.resolve_telegram_user(message.from_user)
        target_record = await services.identity.resolve_telegram_user(target_user)
        
        if chat_record:
            await services.moderation.record_action(
                user_id=target_record["id"],
                chat_id=chat_record["id"],
                moderator_user_id=admin_record["id"],
                action_type="unmute",
                reason=reason,
                trust_delta=0
            )

        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_video_notes=True,
            can_send_voice_notes=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_invite_users=True
        )
        await message.chat.restrict(user_id=target_user.id, permissions=permissions)
        await message.reply(f"🕊️ {target_user.first_name} has been forgiven and unmuted.\n**Reason:** {reason}", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Unmute failed: {e}")
        await message.reply("❌ Failed to unmute user. Make sure I have admin rights.")

# -----------------------------------------------------------------------------
# CHAT FLOW CONTROL (LOCKDOWN COMMANDS)
# -----------------------------------------------------------------------------

@router.message(Command("lock"), IsAdminFilter())
async def handle_lock(message: Message) -> None:
    try:
        await message.chat.set_permissions(ChatPermissions(can_send_messages=False))
        await message.reply("🔒 **CHAT LOCKED**\n\nThe group has been temporarily locked by an admin. Only administrators can send messages right now.", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Lock failed: {e}")
        await message.reply("❌ Failed to lock the chat. Ensure I have the 'Change Group Info' permission.")

@router.message(Command("unlock"), IsAdminFilter())
async def handle_unlock(message: Message) -> None:
    try:
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_video_notes=True,
            can_send_voice_notes=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_invite_users=True
        )
        await message.chat.set_permissions(permissions)
        await message.reply("🔓 **CHAT UNLOCKED**\n\nThe group is open again. You may now send messages.", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Unlock failed: {e}")
        await message.reply("❌ Failed to unlock the chat. Ensure I have the 'Change Group Info' permission.")

@router.message(Command("biblestudy"), IsAdminFilter())
async def handle_biblestudy(message: Message) -> None:
    try:
        await message.chat.set_permissions(ChatPermissions(can_send_messages=False))
        study_banner = (
            "<b>BIBLE STUDY IN PROGRESS</b>\n\n"
            "<blockquote>The chat has been temporarily silenced so the teacher can minister without interruption.\n\n"
            "Please listen attentively and take notes. The chat will be unlocked for questions when the session is over.</blockquote>"
        )
        await message.answer(study_banner, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Bible study lock failed: {e}")
        await message.reply("❌ Failed to lock the chat. Ensure I have the 'Change Group Info' permission.")

@router.message(Command("endbiblestudy"), IsAdminFilter())
async def handle_endbiblestudy(message: Message) -> None:
    try:
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_video_notes=True,
            can_send_voice_notes=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_invite_users=True
        )
        await message.chat.set_permissions(permissions)
        end_banner = (
            "<b>BIBLE STUDY HAS ENDED</b>\n\n"
            "<blockquote>The chat is now open! Feel free to ask questions, share your notes, or discuss what we just learned.</blockquote>"
        )
        await message.answer(end_banner, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Bible study unlock failed: {e}")
        await message.reply("❌ Failed to unlock the chat. Ensure I have the 'Change Group Info' permission.")

# -----------------------------------------------------------------------------
# UNAUTHORIZED / FALLBACK HANDLERS
# -----------------------------------------------------------------------------

@router.message(Command("warn", "kick", "ban", "mute", "unban", "unmute", "lock", "unlock", "biblestudy", "endbiblestudy"))
async def handle_unauthorized(message: Message) -> None:
    """Catches anyone trying to run an admin command who failed the IsAdminFilter."""
    await message.reply("🛑 Only group administrators can wield the sword of justice.")

# -----------------------------------------------------------------------------
# YOUTOPIAN STATUS & APPEALS
# -----------------------------------------------------------------------------

def pete_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="My profile"),
                KeyboardButton(text="📝 Submit Appeal")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Choose an action"
    )

class AppealState(StatesGroup):
    waiting_for_appeal = State()

@router.callback_query(F.data == "appeal_init")
async def handle_appeal_init(callback_query: CallbackQuery, state: FSMContext) -> None:
    # Ensure they are appealing in DMs so they don't spam the group with their appeal text
    if callback_query.message.chat.type != "private":
        await callback_query.answer("Please DM me to submit your appeal.", show_alert=True)
        return
        
    await start_appeal_flow(callback_query.message, state)
    await callback_query.answer()

@router.message(Command("appeal"))
@router.message(F.text == "📝 Submit Appeal")
async def handle_submit_appeal_menu(message: Message, state: FSMContext) -> None:
    if message.chat.type != "private":
        return
    await start_appeal_flow(message, state)

async def start_appeal_flow(message: Message, state: FSMContext) -> None:
    await state.set_state(AppealState.waiting_for_appeal)
    await message.reply("Please type out your appeal or apology in a single message. Tell the admins what happened and why your Trust Score should be restored.")

@router.message(AppealState.waiting_for_appeal)
async def process_appeal_message(message: Message, state: FSMContext, services: ServiceContainer) -> None:
    await state.clear()
    
    owner_id_str = os.environ.get("ADMIN_OWNER_ID")
    if not owner_id_str or owner_id_str == "YOUR_TELEGRAM_ID_HERE":
        await message.reply("❌ The community owner has not configured their Telegram ID to receive appeals yet. Please contact an admin manually.")
        return
        
    target_record = await services.identity.resolve_telegram_user(message.from_user)
    db_id = target_record["id"]
    
    appeal_card = (
        "📝 **YOUTOPIAN APPEAL RECEIVED**\n\n"
        f"**From:** {message.from_user.first_name} (@{message.from_user.username or 'No Username'})\n"
        f"**Message:** \"{message.text}\""
    )
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Accept", callback_data=f"appeal_accept|{db_id}|{message.from_user.id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"appeal_reject|{db_id}|{message.from_user.id}")
        ]
    ])
    
    try:
        await message.bot.send_message(chat_id=owner_id_str, text=appeal_card, parse_mode="Markdown", reply_markup=markup)
        await message.reply("✅ Your appeal has been submitted directly to the administration. We will review it shortly.")
    except Exception as e:
        logger.error(f"Failed to forward appeal to owner: {e}")
        await message.reply("❌ Failed to send appeal. The owner might need to start a conversation with me first.")

@router.callback_query(F.data.startswith("appeal_accept|"))
async def handle_appeal_accept(callback_query: CallbackQuery, services: ServiceContainer) -> None:
    parts = callback_query.data.split("|")
    db_id = parts[1]
    tg_user_id = int(parts[2])
    
    # Restore trust score via a +100 delta (it automatically caps at 100)
    await services.moderation.record_action(
        user_id=db_id,
        chat_id=None,
        moderator_user_id=None,
        action_type="appeal_accepted",
        reason="Owner accepted appeal.",
        trust_delta=100
    )
    
    await callback_query.message.edit_text(callback_query.message.text + "\n\n✅ **STATUS: ACCEPTED**")
    try:
        await callback_query.bot.send_message(chat_id=tg_user_id, text="Rejoice! Your appeal was accepted by the admins and your Trust Score has been fully restored.")
    except Exception:
        pass

@router.callback_query(F.data.startswith("appeal_reject|"))
async def handle_appeal_reject(callback_query: CallbackQuery) -> None:
    parts = callback_query.data.split("|")
    tg_user_id = int(parts[2])
    
    await callback_query.message.edit_text(callback_query.message.text + "\n\n❌ **STATUS: REJECTED**")
    try:
        await callback_query.bot.send_message(chat_id=tg_user_id, text="Your appeal was reviewed but denied at this time.")
    except Exception:
        pass

# Captcha Memory Store: {user_id: {"chat_id": int, "msg_id": int}}
PENDING_CAPTCHAS = {}

@router.my_chat_member()
async def on_pete_group_join(event: ChatMemberUpdated, bot: Bot, services: ServiceContainer) -> None:
    old_status = event.old_chat_member.status
    new_status = event.new_chat_member.status

    # Case 1: Pete added or promoted in group
    if new_status in ("member", "administrator"):
        try:
            await register_chat(event.chat, services, "pete")
        except Exception as e:
            logger.warning(f"Failed to register group chat for Pete on join: {e}")
        chat_id = event.chat.id
        group_title = event.chat.title or "Group"

        # Status transition: Member -> Admin promotion upgrade
        if old_status == "member" and new_status == "administrator":
            try:
                sent_msg = await bot.send_message(
                    chat_id=chat_id,
                    text=(
                        f"⚡ <b>ADMIN RIGHTS GRANTED!</b>\n\n"
                        f"<blockquote>Thank you for promoting Pete in <b>{group_title}</b>! "
                        f"Automated moderation, captcha verification, and anti-spam shields are now active. 🛡️</blockquote>"
                    ),
                    parse_mode="HTML"
                )
                asyncio.create_task(self_destruct_message(bot, chat_id, sent_msg.message_id, 5))
            except Exception:
                pass
            return

        # Differentiated Welcome Card based on Admin vs Member status
        if new_status == "administrator":
            welcome_text = (
                f"<b>PETE IS HERE 🛡️</b>\n\n"
                f"<blockquote>I am Pete — High King of Security & Moderation in <b>YouThopiaOS</b>.\n\n"
                f"I protect our digital sanctuary across our 5-bot ecosystem:\n"
                f"• 📖 <b>Theo:</b> Daily Scripture & Devotionals\n"
                f"• 🎯 <b>Lusy:</b> Quizzes & YouTopian Points (YP)\n"
                f"• 🛡️ <b>Pete:</b> Security & Group Moderation\n"
                f"• 📅 <b>Eddy:</b> Events & Reminders\n"
                f"• 💬 <b>Susy:</b> Welcome & Onboarding</blockquote>\n\n"
                f"<b>SECURITY QUICK START</b>\n"
                f"<blockquote>• <b>Captcha Gatekeeper:</b> <code>ENABLED</code> (Auto-verifies new members).\n"
                f"• <b>Spam & Link Shield:</b> <code>ACTIVE</code> (Blocks profanity & links).\n"
                f"• <b>Admins:</b> Manage anytime using <code>/help</code> or <code>/warn</code>.</blockquote>\n\n"
                f"<i>Sharing God's Love All The Way 💜</i>"
            )
            markup = build_pete_group_welcome_keyboard()
        else:
            welcome_text = (
                f"<b>PETE IS HERE 🛡️</b>\n\n"
                f"<blockquote>I am Pete — High King of Security & Moderation in <b>YouThopiaOS</b>.\n\n"
                f"I protect our digital sanctuary across our 5-bot ecosystem:\n"
                f"• 📖 <b>Theo:</b> Daily Scripture & Devotionals\n"
                f"• 🎯 <b>Lusy:</b> Quizzes & YouTopian Points (YP)\n"
                f"• 🛡️ <b>Pete:</b> Security & Group Moderation\n"
                f"• 📅 <b>Eddy:</b> Events & Reminders\n"
                f"• 💬 <b>Susy:</b> Welcome & Onboarding</blockquote>\n\n"
                f"<b>⚠️ ADMIN RIGHTS NEEDED</b>\n"
                f"<blockquote>To filter spam and execute captcha mutes smoothly, please grant Pete <b>Admin Rights</b>!</blockquote>"
            )
            markup = build_pete_member_welcome_keyboard()

        try:
            sent_msg = await bot.send_message(
                chat_id=chat_id,
                text=welcome_text,
                parse_mode="HTML",
                reply_markup=markup
            )
            # Auto-delete welcome card after 120s
            asyncio.create_task(self_destruct_message(bot, chat_id, sent_msg.message_id, 120))
        except Exception as e:
            logger.warning(f"Failed to send Pete group welcome card: {e}")

    # Case 2: Pete removed or kicked from group
    elif new_status in ("left", "kicked"):
        chat_id = event.chat.id
        group_title = event.chat.title or "your group"
        try:
            await services.chats.set_subscription("pete", chat_id, "security", enabled=False)
        except Exception:
            pass

        # Notify Admin in DM
        admin_user_id = event.from_user.id if event.from_user else None
        if admin_user_id:
            try:
                farewell_text = (
                    f"<b>Pete Departs {group_title} 🛡️</b>\n\n"
                    f"<blockquote>Pete has been removed from <b>{group_title}</b>.\n"
                    f"Automated security and captcha verification have been paused for this group. "
                    f"You can re-invite Pete anytime or explore our other 4 community bots below! 💜</blockquote>"
                )
                await bot.send_message(
                    chat_id=admin_user_id,
                    text=farewell_text,
                    parse_mode="HTML",
                    reply_markup=build_pete_farewell_keyboard()
                )
            except Exception as e:
                logger.warning(f"Could not send Pete farewell DM to admin {admin_user_id}: {e}")

@router.callback_query(F.data == "pete_prompt_admin")
async def handle_pete_prompt_admin(callback: CallbackQuery, bot: Bot) -> None:
    try:
        member = await bot.get_chat_member(callback.message.chat.id, callback.from_user.id)
        if member.status not in ("administrator", "creator"):
            await callback.answer("⚠️ Only group administrators can promote bots to admin!", show_alert=True)
            return
    except Exception:
        pass

    await callback.answer()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Open Admin Permission Sheet", url="https://t.me/iampetebot?startgroup=admin&admin=delete_messages+restrict_members+pin_messages+invite_users")]
    ])
    try:
        sent_msg = await callback.message.answer(
            "<blockquote>🛡️ <b>Pete Administrator Setup</b>\n\n"
            "Tap below to open Telegram's permission sheet with required rights pre-checked!</blockquote>",
            parse_mode="HTML",
            reply_markup=markup
        )
        asyncio.create_task(self_destruct_message(bot, callback.message.chat.id, sent_msg.message_id, 20))
    except Exception:
        pass

@router.message(Command("leave"))
@router.message(Command("remove_pete"))
async def handle_leave_command(message: Message, bot: Bot, services: ServiceContainer) -> None:
    if message.chat.type == "private":
        await message.answer("⚠️ This command is only for group chats.")
        return

    chat_id = message.chat.id
    group_title = message.chat.title or "your group"
    admin_id = message.from_user.id if message.from_user else None

    # Check if user is admin
    try:
        member = await bot.get_chat_member(chat_id, admin_id)
        if member.status not in ("creator", "administrator"):
            try:
                await message.delete()
            except Exception:
                pass
            msg = await message.answer("⚠️ Only group administrators can use /leave.")
            asyncio.create_task(self_destruct_message(bot, chat_id, msg.message_id, 5))
            return
    except Exception:
        pass

    # Send DM to admin
    if admin_id:
        try:
            farewell_text = (
                f"<b>Pete Departs {group_title} 🛡️</b>\n\n"
                f"<blockquote>Pete has left <b>{group_title}</b> as requested.\n"
                f"Automated security and captcha verification have been paused for this group. "
                f"You can re-invite Pete anytime or explore our other 4 community bots below! 💜</blockquote>"
            )
            await bot.send_message(
                chat_id=admin_id,
                text=farewell_text,
                parse_mode="HTML",
                reply_markup=build_pete_farewell_keyboard()
            )
        except Exception as e:
            logger.warning(f"Could not send Pete leave DM to admin {admin_id}: {e}")

    # Leave group cleanly
    try:
        await bot.leave_chat(chat_id)
    except Exception as e:
        logger.warning(f"Pete failed to leave chat {chat_id}: {e}")

@router.message(Command("start"))
async def handle_start(message: Message, bot: Bot, services: ServiceContainer) -> None:
    if message.chat.type != "private":
        try:
            await message.delete()
        except Exception:
            pass

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛡️ Open Security Dashboard", url="https://t.me/iampetebot?start=dashboard")],
            [InlineKeyboardButton(text="📝 Submit Appeal", callback_data="appeal_init")],
        ])
        try:
            sent_msg = await message.answer(
                "<blockquote>🛡️ <b>Pete Security Engine is active in this group!</b>\n"
                "Tap below to open your DM Security Dashboard or submit an appeal.</blockquote>",
                parse_mode="HTML",
                reply_markup=markup
            )
            asyncio.create_task(self_destruct_message(bot, message.chat.id, sent_msg.message_id, 10))
        except Exception:
            pass
        return
        
    # Check if this is a Deep Link Captcha verification
    if message.text and message.text.startswith("/start verify_"):
        chat_id_str = message.text.split("_")[1]
        markup = build_pete_captcha_inline_keyboard(chat_id_str)
        await message.answer(
            "Please click the button below to verify your account and unlock your chat permissions.",
            reply_markup=markup
        )
        return

    await register_group_chat(message, services, "pete")
    user = await services.identity.resolve_telegram_user(message.from_user)
    first_name = message.from_user.first_name or "Friend"
    
    try:
        warnings = await services.moderation.get_user_warnings_count(user["id"])
    except Exception:
        warnings = 0
        
    trust_score = user.get("trust_score", 100)

    if user.get("engagement_level") == "new":
        welcome_text = (
            f"<b>Welcome to YouThopia Security, {first_name}! 🛡️</b>\n\n"
            f"<blockquote>I am Pete (High King Peter) — guardian of the <b>YouThopiaOS</b> ecosystem.\n\n"
            f"I protect our community atmosphere by enforcing rules, filtering spam, and keeping our borders secure across all 5 pillar bots:\n"
            f"• 📖 <b>Theo:</b> Daily Scripture & Devotionals\n"
            f"• 🎯 <b>Lusy:</b> Quizzes & YouTopian Points (YP)\n"
            f"• 🛡️ <b>Pete:</b> Security & Group Moderation\n"
            f"• 📅 <b>Eddy:</b> Events & Reminders\n"
            f"• 💬 <b>Susy:</b> Welcome & Onboarding</blockquote>\n\n"
            f"<b>SELECT AN OPTION BELOW TO GET STARTED:</b>"
        )
        await services.users.set_engagement_level(user["id"], "active")
    else:
        welcome_text = (
            f"<b>Welcome back, {first_name}! 🛡️</b>\n\n"
            f"<blockquote>🛡️ <b>Active Warnings:</b> <code>{warnings}/5</code>\n"
            f"📜 <b>Safety Record:</b> <code>{'Clean Record ✨' if warnings == 0 else 'Under Observation'}</code>\n"
            f"💯 <b>Trust Score:</b> <code>{trust_score}/100</code>\n\n"
            f"I am constantly monitoring our community borders so you can fellowship in a clean, safe environment!</blockquote>\n\n"
            f"<b>WHAT WOULD YOU LIKE TO DO TODAY?</b>"
        )
    
    reply_menu = build_pete_reply_keyboard()
    inline_menu = build_pete_start_inline_keyboard()
    
    await message.answer("🛡️ <b>Welcome to Pete Security Dashboard!</b>", parse_mode="HTML", reply_markup=reply_menu)
    await message.answer(welcome_text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=inline_menu)

# -------------------------------------------------------------------------
# PROFILE & HELP HANDLERS
# -------------------------------------------------------------------------
@router.message(F.text == "👤 My Profile")
@router.message(Command("profile"))
@router.callback_query(F.data == "pete_profile")
async def handle_pete_profile(event: Message | CallbackQuery, bot: Bot, services: ServiceContainer) -> None:
    is_callback = isinstance(event, CallbackQuery)
    message = event.message if is_callback else event
    user_from = event.from_user

    if is_callback:
        await event.answer()

    if message.chat.type != "private":
        await handle_group_profile_acknowledgment(message, bot)
        if user_from:
            try:
                await send_pete_profile(message, services, telegram_user=user_from, send_to_dm=True, bot=bot)
            except Exception as e:
                logger.warning(f"Failed to send Pete profile to DM: {e}")
        return

    await send_pete_profile(message, services, telegram_user=user_from)

async def send_pete_profile(
    message: Message, services: ServiceContainer, telegram_user: Any | None = None, send_to_dm: bool = False, bot: Bot | None = None
) -> None:
    user_from = telegram_user or message.from_user
    user = await services.identity.resolve_telegram_user(user_from)
    try:
        warnings = await services.moderation.get_user_warnings_count(user["id"])
    except Exception:
        warnings = 0

    bot_stats = [
        f"🛡️ Active Warnings: <b>{warnings}/5</b>",
        f"📜 Safety Status: <b>{'Clean Record ✨' if warnings == 0 else 'Under Observation'}</b>",
    ]

    card_text = render_shared_profile_card(
        user_data=user,
        telegram_first_name=user_from.first_name or "Friend",
        bot_specific_stats=bot_stats
    )

    if send_to_dm and bot and user_from:
        await bot.send_message(
            chat_id=user_from.id,
            text=card_text,
            parse_mode="HTML",
            reply_markup=build_pete_reply_keyboard()
        )
    else:
        await message.answer(card_text, parse_mode="HTML", reply_markup=build_pete_reply_keyboard())

@router.message(F.text == "ℹ️ Help")
@router.message(Command("help"))
@router.callback_query(F.data == "pete_help")
async def handle_pete_help(event: Message | CallbackQuery, bot: Bot) -> None:
    is_callback = isinstance(event, CallbackQuery)
    message = event.message if is_callback else event

    if is_callback:
        await event.answer()

    if message.chat.type != "private":
        try:
            await message.delete()
        except Exception:
            pass
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛡️ Open Pete Guide in DM", url="https://t.me/iampetebot?start=help")],
            [InlineKeyboardButton(text="📝 Submit Appeal", callback_data="appeal_init")],
        ])
        try:
            sent_msg = await message.answer(
                "<blockquote>🛡️ <b>Pete Security Help Guide</b>\n"
                "Tap below to view full features and moderation rules in DM.</blockquote>",
                parse_mode="HTML",
                reply_markup=markup
            )
            asyncio.create_task(self_destruct_message(bot, message.chat.id, sent_msg.message_id, 10))
        except Exception:
            pass
        return

    first_name = event.from_user.first_name or "Friend"
    help_text = (
        f"<b>🛡️ Pete | Safety Bot Help Guide, {first_name}!</b>\n"
        "<blockquote>I am Pete (@iampetebot), the security guard for YOUTHOPIA BIBLE COMMUNITY.\n\n"
        "<b>Pete Features & Commands</b>\n"
        "• 🛡️ <b>Captcha Verification:</b> Automated new member verification.\n"
        "• 🚫 <b>Spam & Raid Protection:</b> Instant detection of links, floods, and bad words.\n"
        "• 📜 <b>Moderation Record:</b> Transparent warning system.\n"
        "• 📝 <b>Submit Appeal:</b> Appeal a warning or penalty directly to community admins.\n"
        "• <b>/warn:</b> Issue warning to a member (Admin).\n"
        "• <b>/mute /unmute:</b> Restrict or restore chat rights (Admin).\n"
        "• <b>/kick /ban /unban:</b> Remove or restrict disruptive accounts (Admin).\n"
        "• <b>/lock /unlock:</b> Lock or open group chat (Admin).</blockquote>\n\n"
        f"{BOT_FAMILY_DIRECTORY_TEXT}\n\n"
        "Sharing God's Love All The Way 💜"
    )

    await message.answer(
        help_text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=get_community_links_keyboard(),
    )

@router.message(F.text == "🌐 Community")
@router.message(F.text == "🌐 Community Links")
async def community_handler(message: Message) -> None:
    if message.chat.type != "private":
        return
    await send_community_exploration_page(message, 1)

@router.callback_query(F.data == "pete_community_links")
async def handle_pete_community_links(callback: CallbackQuery) -> None:
    await callback.answer()
    await send_community_exploration_page(callback.message, 1)

@router.callback_query(F.data.startswith("onboarding_"))
async def global_onboarding_callback_handler(callback_query: CallbackQuery, services: ServiceContainer) -> None:
    await handle_global_onboarding_callback(callback_query, services)

# -----------------------------------------------------------------------------
# AUTOMATED JUSTICE ENGINE (ACTIVE LISTENER)
# -----------------------------------------------------------------------------

import re
import time
from collections import defaultdict
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

FORBIDDEN_WORDS = {
    "anal", "anus", "arse", "arsehole", "ass", "asshat", "asshole", "bastard", "bitch", 
    "bitchy", "blowjob", "bollocks", "boobs", "bullshit", "chode", "clit", "cock", 
    "cocksucker", "crap", "cum", "cunt", "damn", "dammit", "dick", "dickhead", "dildo", 
    "dipshit", "douche", "douchebag", "dumbass", "dyke", "fag", "faggot", "fuck", "fucker", 
    "fucking", "goddamn", "handjob", "hoe", "hooker", "horseshit", "jackass", "jerkoff", 
    "motherfucker", "motherfucking", "nigga", "nigger", "orgasm", "penis", "piss", "pissed", 
    "porn", "prick", "pussy", "retard", "schlong", "scrotum", "sex", "shit", "shithead", 
    "shitty", "slut", "snatch", "sonofabitch", "sperm", "testicles", "tit", "tits", "twat", 
    "vagina", "wanker", "whore", "cuck", "gtfo", "incel", "kys", "lmao", "lmfao", "milf", 
    "nibba", "pedo", "simp", "stfu", "thot", "wtf", "wth", "gfy", "fml", "smfd", "b1tch", 
    "b!tch", "bullcrap", "circlejerk", "cumshot", "dickpic", "fatass", "fck", "f*ck", "phuck", 
    "pron", "sh1t", "sh*t", "xrated", "nsfw"
}

# Compile a highly efficient regex that only matches full words
# This prevents innocent words like 'passion' or 'glass' from being flagged as 'ass'
FORBIDDEN_PATTERN = re.compile(r'\b(?:' + '|'.join(map(re.escape, FORBIDDEN_WORDS)) + r')\b', re.IGNORECASE)

# Detect Telegram and WhatsApp invite links
INVITE_LINK_PATTERN = re.compile(r'(?:t\.me/|telegram\.me/|chat\.whatsapp\.com/)', re.IGNORECASE)

# Flood Control Configuration
USER_MESSAGE_TIMESTAMPS = defaultdict(list)
USER_MESSAGE_CONTENT = defaultdict(list)
FLOOD_LIMIT = 5   # Max messages allowed
FLOOD_WINDOW = 4  # Within 4 seconds

# -----------------------------------------------------------------------------
# PHASE 3: PERIMETER DEFENSE (WELCOME DECREE)
# -----------------------------------------------------------------------------

async def execute_quarantine_decree(bot: Bot, chat_id: int, user_id: int, first_name: str) -> None:
    """Reusable quarantine and challenge engine for Pete."""
    bot_me = await bot.get_me()
    try:
        # 1. Instantly revoke typing permissions
        await bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id, 
            permissions=ChatPermissions(can_send_messages=False)
        )
        
        # 2. Drop the Deep Link gateway in the chat
        welcome_text = (
            f"Welcome to YouThopia, **{first_name}**! 🕊️\n\n"
            f"To protect our community from spam bots, you have been temporarily muted.\n"
            f"Please click here to verify your account in my DMs: [Verify Here](https://t.me/{bot_me.username}?start=verify_{chat_id})"
        )
        
        sent_msg = await bot.send_message(
            chat_id=chat_id,
            text=welcome_text,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        
        # 3. Store the message ID so we can cleanly delete it later
        PENDING_CAPTCHAS[user_id] = {
            "chat_id": chat_id,
            "msg_id": sent_msg.message_id
        }
    except Exception as e:
        logger.error(f"Failed to execute Welcome Decree on {user_id}: {e}")


@router.message(F.new_chat_members)
async def welcome_decree_handler(message: Message, bot: Bot) -> None:
    """Intercepts new members joining via public link, mutes them, and drops the Deep Link challenge."""
    for new_member in message.new_chat_members:
        if new_member.is_bot:
            continue
        await execute_quarantine_decree(bot, message.chat.id, new_member.id, new_member.first_name)


@router.chat_member()
async def member_status_update_handler(event: ChatMemberUpdated, bot: Bot) -> None:
    """Intercepts new members joining via Admin Join Request Approval."""
    old_status = event.old_chat_member.status
    new_status = event.new_chat_member.status
    user = event.new_chat_member.user

    # If this is the bot itself being added, my_chat_member handles it
    if user.is_bot:
        return

    # Triggered when user enters group: from left/kicked/restricted -> member
    if old_status in ("left", "kicked", "restricted") and new_status == "member":
        if user.id not in PENDING_CAPTCHAS:
            await execute_quarantine_decree(bot, event.chat.id, user.id, user.first_name)

@router.callback_query(F.data.startswith("captcha|"))
async def captcha_callback_handler(callback_query: CallbackQuery) -> None:
    """Handles the Captcha button click in the DM."""
    chat_id = int(callback_query.data.split("|")[1])
    user_id = callback_query.from_user.id
    
    try:
        # 1. Restore all standard typing permissions in the main group
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_video_notes=True,
            can_send_voice_notes=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_invite_users=True
        )
        await callback_query.bot.restrict_chat_member(chat_id=chat_id, user_id=user_id, permissions=permissions)
        
        # 2. Update the DM message
        await callback_query.message.edit_text("✅ Verification successful! You can now return to the group and chat.")
        
        # 3. Clean up the group chat (delete the ugly deep link message)
        pending = PENDING_CAPTCHAS.pop(user_id, None)
        if pending and pending["chat_id"] == chat_id:
            try:
                await callback_query.bot.delete_message(chat_id=chat_id, message_id=pending["msg_id"])
            except Exception:
                pass
                
        # 4. Drop the public confirmation in the group
        markup = build_pete_post_captcha_group_keyboard()
        success_msg = await callback_query.bot.send_message(
            chat_id=chat_id, 
            text=f"✅ **{callback_query.from_user.first_name}** has passed verification and been granted entry!", 
            parse_mode="Markdown",
            reply_markup=markup
        )
        
        async def auto_delete_msg(msg, delay: int) -> None:
            import asyncio
            await asyncio.sleep(delay)
            try:
                await msg.delete()
            except Exception:
                pass
                
        import asyncio
        asyncio.create_task(auto_delete_msg(success_msg, 60))
        
        try:
            await callback_query.answer("Verification successful!")
        except Exception:
            pass
        
    except Exception as e:
        logger.error(f"Failed to unlock user {user_id} after Captcha: {e}")
        await callback_query.answer("❌ Error unlocking permissions. Ensure I am an admin in the group.", show_alert=True)

@router.message(F.chat.type.in_({"group", "supergroup"}), F.text)
async def automated_justice_filter(message: Message, services: ServiceContainer) -> None:
    """Scans every message sent in the chat for forbidden language and unauthorized links."""
    # Only process text messages in groups
    if not message.text or message.chat.type == "private":
        return
        
    user_id = message.from_user.id
    current_time = time.time()
    
    # Check 1: Flood Detection
    timestamps = USER_MESSAGE_TIMESTAMPS[user_id]
    timestamps[:] = [ts for ts in timestamps if current_time - ts <= FLOOD_WINDOW]
    timestamps.append(current_time)
    
    if len(timestamps) > FLOOD_LIMIT:
        # Check if they are an admin before punishing (admins might need to paste multi-part studies)
        try:
            member = await message.chat.get_member(user_id)
            if member.status in ("administrator", "creator"):
                return
        except Exception:
            pass
            
        timestamps.clear()  # Reset to prevent duplicate triggers
        await execute_automated_justice(message, services, "Automated Justice: Spam/Flood detected.", -20, "stop flooding the chat")
        return
        
    text_lower = message.text.lower()
    
    # Check 1.5: Repetitive Text Detection (Copy-Paste Spam)
    history = USER_MESSAGE_CONTENT[user_id]
    history[:] = [(ts, txt) for ts, txt in history if current_time - ts <= 60]
    history.append((current_time, text_lower))
    
    same_text_count = sum(1 for _, txt in history if txt == text_lower)
    if same_text_count >= 3:
        try:
            member = await message.chat.get_member(user_id)
            if member.status in ("administrator", "creator"):
                pass
            else:
                history.clear()
                await execute_automated_justice(message, services, "Automated Justice: Repetitive copy-paste detected.", -15, "stop sending the exact same message")
                return
        except Exception:
            pass
    
    # Check 2: Forbidden Language
    if FORBIDDEN_PATTERN.search(message.text):
        await execute_automated_justice(message, services, "Automated Justice: Profanity detected.", -5, "please watch your language")
        return
        
    # Check 2: Unauthorized Invite Links
    if INVITE_LINK_PATTERN.search(message.text):
        # We must check if the sender is an admin before punishing for a link!
        # Admins are allowed to post official links.
        try:
            member = await message.chat.get_member(message.from_user.id)
            if member.status in ("administrator", "creator"):
                return  # Admin is allowed to post links
        except Exception:
            pass
            
        await execute_automated_justice(message, services, "Automated Justice: Unauthorized invite link.", -15, "unauthorized invite links are not allowed here")
        return

async def execute_automated_justice(message: Message, services: ServiceContainer, reason: str, trust_delta: int, reprimand: str) -> None:
    """Helper function to execute automated punishments."""
    # 1. Instantly delete the message
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"Failed to delete message: {e}")
        return
        
    # 2. Log the penalty
    chat_record = await register_group_chat(message, services, "pete")
    if not chat_record:
        return
        
    target_record = await services.identity.resolve_telegram_user(message.from_user)
    
    await services.moderation.record_action(
        user_id=target_record["id"],
        chat_id=chat_record["id"],
        moderator_user_id=None,  # Automated action
        action_type="warn",
        reason=reason,
        trust_delta=trust_delta
    )
    
    # 3. Check threshold logic for Automated Warning
    warnings = await services.moderation.get_user_warnings_count(target_record["id"], chat_record["id"])
    
    extra_msg = ""
    if warnings >= 5:
        try:
            await message.chat.ban(user_id=message.from_user.id)
            extra_msg = "\n\n🔨 You have reached 5 warnings and have been permanently banned."
            await services.moderation.record_action(
                user_id=target_record["id"],
                chat_id=chat_record["id"],
                moderator_user_id=None,
                action_type="ban",
                reason="Automated Justice: Reached 5 warnings.",
                trust_delta=-50
            )
        except Exception as e:
            logger.error(f"Automated ban failed: {e}")
    elif warnings >= 3:
        try:
            from aiogram.types import ChatPermissions
            await message.chat.restrict(user_id=message.from_user.id, permissions=ChatPermissions(can_send_messages=False))
            extra_msg = "\n\n🔇 You have reached 3 warnings and have been automatically muted."
            await services.moderation.record_action(
                user_id=target_record["id"],
                chat_id=chat_record["id"],
                moderator_user_id=None,
                action_type="mute",
                reason="Automated Justice: Reached 3 warnings.",
                trust_delta=-20
            )
        except Exception as e:
            logger.error(f"Automated mute failed: {e}")
    
    # 4. Publicly reprimand the user
    await message.answer(
        f"⚠️ **{message.from_user.first_name}**, {reprimand}! Your message was removed and your Trust Score has been penalized.{extra_msg}",
        parse_mode="Markdown"
    )

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllChatAdministrators, BotCommandScopeAllGroupChats, BotCommandScopeAllPrivateChats

@router.startup()
async def on_startup(bot: Bot) -> None:
    admin_commands = [
        BotCommand(command="warn", description="Issue a warning"),
        BotCommand(command="mute", description="Revoke typing permissions"),
        BotCommand(command="kick", description="Remove user from group"),
        BotCommand(command="ban", description="Permanently ban user"),
        BotCommand(command="unban", description="Lift a ban"),
        BotCommand(command="unmute", description="Lift a mute"),
        BotCommand(command="lock", description="Lock the group chat"),
        BotCommand(command="unlock", description="Unlock the group chat"),
        BotCommand(command="biblestudy", description="Silence chat for a teaching session"),
        BotCommand(command="endbiblestudy", description="Unlock chat after teaching session")
    ]
    
    user_commands = [
        BotCommand(command="start", description="Meet Pete"),
        BotCommand(command="appeal", description="Submit Appeal"),
        BotCommand(command="profile", description="View your profile"),
        BotCommand(command="help", description="Pete Safety Guide")
    ]
    
    # Clear any stale admin chat scope overrides for Pete
    import os
    from aiogram.types import BotCommandScopeChat
    admin_ids_str = os.getenv("ADMIN_OWNER_ID") or os.getenv("ADMIN_IDS") or ""
    admin_ids = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip().isdigit()]
    for admin_id in admin_ids:
        try:
            await bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=admin_id))
        except Exception:
            pass

    group_commands = [
        BotCommand(command="start", description="Meet Pete"),
        BotCommand(command="help", description="Pete Safety Guide")
    ]

    # Set public commands for Private DMs only
    await bot.set_my_commands(user_commands, scope=BotCommandScopeAllPrivateChats())
    
    # Normal group members see /start and /help
    await bot.set_my_commands(group_commands, scope=BotCommandScopeAllGroupChats())
    
    # Group Administrators see /start, /help, and moderation tools in groups
    await bot.set_my_commands(group_commands + admin_commands, scope=BotCommandScopeAllChatAdministrators())
