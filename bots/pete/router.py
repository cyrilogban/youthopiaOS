import logging
from typing import Any
from aiogram import Router, F
from aiogram.types import Message, ChatPermissions
from aiogram.filters import Command, CommandObject, Filter
from shared.services.container import ServiceContainer
from core.telegram_runtime import register_group_chat

logger = logging.getLogger(__name__)

router = Router()

class IsAdminFilter(Filter):
    """Filter to restrict commands to group administrators or creators."""
    async def __call__(self, message: Message) -> bool:
        # Admin commands only make sense in group chats
        if message.chat.type == "private":
            return False 
            
        try:
            member = await message.chat.get_member(message.from_user.id)
            return member.status in ("administrator", "creator")
        except Exception as e:
            logger.error(f"Failed to check admin status: {e}")
            return False

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
    
    if warnings >= 3:
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
        await message.chat.restrict(user_id=target_user.id, permissions=permissions)
        await message.reply(f"🔇 {target_user.first_name} has been muted.\n**Reason:** {reason}", parse_mode="Markdown")
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
            "📖 **BIBLE STUDY IN PROGRESS** 📖\n\n"
            "<blockquote>The chat has been temporarily silenced so the teacher can minister without interruption.\n\n"
            "Please listen attentively and take notes. The chat will be unlocked for questions when the session is over.</blockquote>"
        )
        await message.answer(study_banner, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Bible study lock failed: {e}")
        await message.reply("❌ Failed to lock the chat. Ensure I have the 'Change Group Info' permission.")

# -----------------------------------------------------------------------------
# UNAUTHORIZED / FALLBACK HANDLERS
# -----------------------------------------------------------------------------

@router.message(Command("warn", "kick", "ban", "mute", "unban", "unmute", "lock", "unlock", "biblestudy"))
async def handle_unauthorized(message: Message) -> None:
    """Catches anyone trying to run an admin command who failed the IsAdminFilter."""
    await message.reply("🛑 Only group administrators can wield the sword of justice.")

# Captcha Memory Store: {user_id: {"chat_id": int, "msg_id": int}}
PENDING_CAPTCHAS = {}

@router.message(Command("start", "help"))
async def handle_start(message: Message, services: ServiceContainer) -> None:
    # Check if this is a Deep Link Captcha verification
    if message.text and message.text.startswith("/start verify_"):
        chat_id_str = message.text.split("_")[1]
        
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛡️ Tap here to prove you are human", callback_data=f"captcha|{chat_id_str}")]
        ])
        
        await message.answer("Please click the button below to verify your account and unlock your chat permissions.", reply_markup=markup)
        return

    # Standard welcome for normal DMs or help commands
    first_name = message.from_user.first_name or "Friend"
    welcome_text = (
        f"<b>Welcome to YOUTHOPIA BIBLE COMMUNITY, {first_name}!</b>\n"
        "<blockquote>We are a cross-platform Gen Z Christian community where faith meets real life. We grow together, share God's Word, and support one another on the journey of becoming who God created us to be.</blockquote>\n\n"
        "<b>You're currently talking to Pete</b>\n"
        "<blockquote>Pete (High King Peter) is the silent guardian of the YouThopia bot family. He protects the spiritual atmosphere by enforcing rules, filtering spam, and keeping our borders secure.</blockquote>\n\n"
        "<b>Meet the YouThopia Bot Family</b>\n"
        "<blockquote><b>Theo</b> - <a href=\"https://t.me/iamtheobot\">@iamtheobot</a>\n"
        "Your daily Bible companion. Devotionals, verses, and reflection.\n\n"
        "<b>Lusy</b> - <a href=\"https://t.me/iamlusybot\">@iamlusybot</a>\n"
        "Games, XP, and fun! Earn points and grow your rank.\n\n"
        "<b>Pete</b> - <a href=\"https://t.me/iampetebot\">@iampetebot</a>\n"
        "Security and moderation. Keeping our community safe.\n\n"
        "<b>Ed</b> - <a href=\"https://t.me/iamedyybot\">@iamedyybot</a>\n"
        "Events and announcements. Never miss what is happening.\n\n"
        "<b>Susy</b> - <a href=\"https://t.me/iamsusiebot\">@iamsusiebot</a>\n"
        "Your first friend here. Welcomes new YouTopians.</blockquote>\n\n"
        "<b>How to Use Pete (Admins Only)</b>\n"
        "<blockquote>Pete's commands are strictly reserved for group administrators:\n"
        "/warn - Issue a warning (-10 Trust)\n"
        "/mute - Revoke typing permissions (-20 Trust)\n"
        "/kick - Remove user from group (-30 Trust)\n"
        "/ban - Permanently ban user (-50 Trust)\n"
        "/unban - Lift a ban\n"
        "/unmute - Lift a mute\n"
        "/lock - Lock the group chat\n"
        "/unlock - Unlock the group chat\n"
        "/biblestudy - Silence the chat for a teaching session</blockquote>\n\n"
        "Sharing God's Love All The Way 💜"
    )
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Join Facebook", url="https://www.facebook.com/share/g/18wG8aWB6t/"),
            InlineKeyboardButton(text="Join Telegram", url="https://t.me/youthopiabiblecommunity"),
        ],
        [
            InlineKeyboardButton(text="Join WhatsApp", url="https://chat.whatsapp.com/HXZsnWjwizoHBojS2VwbHn"),
            InlineKeyboardButton(text="Join Threads", callback_data="ignore"),
        ]
    ])
    
    await message.answer(
        welcome_text, 
        parse_mode="HTML", 
        disable_web_page_preview=True, 
        reply_markup=markup
    )

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
FLOOD_LIMIT = 5   # Max messages allowed
FLOOD_WINDOW = 4  # Within 4 seconds

# -----------------------------------------------------------------------------
# PHASE 3: PERIMETER DEFENSE (WELCOME DECREE)
# -----------------------------------------------------------------------------

@router.message(F.new_chat_members)
async def welcome_decree_handler(message: Message) -> None:
    """Intercepts new members, mutes them, and drops the Deep Link challenge."""
    bot_me = await message.bot.get_me()
    
    for new_member in message.new_chat_members:
        if new_member.is_bot:
            continue
            
        try:
            # 1. Instantly revoke typing permissions
            await message.chat.restrict(
                user_id=new_member.id, 
                permissions=ChatPermissions(can_send_messages=False)
            )
            
            # 2. Drop the Deep Link gateway in the chat
            welcome_text = (
                f"Welcome to YouThopia, **{new_member.first_name}**! 🕊️\n\n"
                f"To protect our community from spam bots, you have been temporarily muted.\n"
                f"Please click here to verify your account in my DMs: [Verify Here](https://t.me/{bot_me.username}?start=verify_{message.chat.id})"
            )
            
            sent_msg = await message.answer(welcome_text, parse_mode="Markdown", disable_web_page_preview=True)
            
            # 3. Store the message ID so we can cleanly delete it later
            PENDING_CAPTCHAS[new_member.id] = {
                "chat_id": message.chat.id,
                "msg_id": sent_msg.message_id
            }
            
        except Exception as e:
            logger.error(f"Failed to execute Welcome Decree on {new_member.id}: {e}")

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
        await callback_query.bot.send_message(
            chat_id=chat_id, 
            text=f"✅ **{callback_query.from_user.first_name}** has passed verification and been granted entry!", 
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Failed to unlock user {user_id} after Captcha: {e}")
        await callback_query.answer("❌ Error unlocking permissions. Ensure I am an admin in the group.", show_alert=True)

@router.message()
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
    
    # Check 1: Forbidden Language
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
    
    # 3. Publicly reprimand the user
    await message.answer(
        f"⚠️ **{message.from_user.first_name}**, {reprimand}! Your message was removed and your Trust Score has been penalized.",
        parse_mode="Markdown"
    )
