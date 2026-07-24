from __future__ import annotations

import asyncio
from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    BotCommand,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllGroupChats,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from shared.services.container import ServiceContainer

from core.telegram_runtime import build_router
from aiogram.filters import Command, CommandObject

# Will add Susy's official photo URL here when available
SUSY_PHOTO = None

def build_susy_router(description: str, music_service=None) -> Router:
    router = build_router("susy", description, include_base_commands=False)

    @router.startup()
    async def on_startup(bot: Bot) -> None:
        private_commands = [
            BotCommand(command="start", description="Wake Up Susy"),
            BotCommand(command="playsong", description="Play song on telegram"),
            BotCommand(command="help", description="Show help information"),
        ]
        
        group_commands = [
            BotCommand(command="playsong", description="Play song in group"),
        ]
        
        await bot.delete_my_commands()
        await bot.set_my_commands(private_commands, scope=BotCommandScopeAllPrivateChats())
        await bot.set_my_commands(group_commands, scope=BotCommandScopeAllGroupChats())


    @router.message(Command("start"))
    async def handle_start(message: Message, services: ServiceContainer) -> None:
        # Group Cleanup Mechanism
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
            return
                
        # Check if deep link from Pete
        if message.text and "onboarding" in message.text:
            await send_onboarding_page(message, 1)
            return

        user = await services.identity.resolve_telegram_user(message.from_user)
        first_name = message.from_user.first_name or "Friend"
        
        welcome_text = (
            f"<b>Welcome to YOUTHOPIA BIBLE COMMUNITY, {first_name}! 🤍</b>\n"
            "<blockquote>I am Susy, your first friend and guide here in the YouThopia ecosystem.\n\n"
            "We are a Gen Z Christian community built to help you grow in your faith, connect with believers, and have fun doing it!</blockquote>\n\n"
            "<b>Getting Started</b>\n"
            "<blockquote>I'm here to show you around! If you are new here, my job is to make sure you know exactly how everything works.\n\n"
            "Whenever you feel lost, just ask me for help!</blockquote>\n\n"
            "Sharing God's Love All The Way. 💜"
        )
        
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Join Facebook", url="https://www.facebook.com/share/g/18wG8aWB6t/"),
                InlineKeyboardButton(text="Join Telegram", url="https://t.me/youthopiabiblecommunity"),
            ],
            [
                InlineKeyboardButton(text="Join WhatsApp", url="https://chat.whatsapp.com/HXZsnWjwizoHBojS2VwbHn"),
                InlineKeyboardButton(text="Join Threads", callback_data="ignore"),
            ],
            [
                InlineKeyboardButton(text="Explore the Community", callback_data="onboarding_1")
            ]
        ])
        
        if SUSY_PHOTO:
            await message.answer_photo(
                photo=SUSY_PHOTO,
                caption=welcome_text,
                parse_mode="HTML",
                reply_markup=markup
            )
        else:
            await message.answer(
                welcome_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=markup
            )
            


    @router.message(F.text == "🎧 Play Song")
    async def on_play_button(message: Message):
        if message.chat.type != "private": return
        await message.answer("📻 Ready to listen? Just type `/playsong` followed by the song name!\n\n*Example:* `/playsong Oceans Hillsong`", parse_mode="Markdown")

    @router.message(F.text == "🌍 Community")
    async def on_about_community(message: Message):
        if message.chat.type != "private": return
        
        about_text = (
            "<b>About YouThopia Bible Community 🌍</b>\n"
            "<blockquote>We are a cross-platform Gen Z Christian community. This is a space where faith meets real life. We grow together, share God's Word, and support one another on the journey of becoming who God created us to be.</blockquote>\n\n"
            "If you haven't joined the main group yet, jump in! We can't wait to fellowship with you. 🤍"
        )
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Join the Main Group", url="https://t.me/youthopiabiblecommunity")]
        ])
        
        await message.answer(about_text, parse_mode="HTML", reply_markup=markup)


    # --- ONBOARDING PAGINATION LOGIC ---
    
    async def send_onboarding_page(message: Message, page: int, edit: bool = False) -> None:
        if page == 1:
            text = (
                "<b>Welcome to YOUTHOPIA! 🤍 (1/3)</b>\n"
                "<blockquote>We are a cross-platform Gen Z Christian community. This is a space where faith meets real life. We grow together, share God's Word, and support one another on the journey of becoming who God created us to be.</blockquote>\n\n"
                "<i>Click Next to read our community guidelines.</i>"
            )
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Next ➡️", callback_data="onboarding_2")]
            ])
        elif page == 2:
            text = (
                "<b>The Core Rules 📜 (2/3)</b>\n"
                "<blockquote><b>1. Love & Respect:</b> Treat everyone with Christ-like love.\n"
                "<b>2. No Spam:</b> Keep the chat clean and focused on growth.\n"
                "<b>3. Guard the Vibe:</b> Keep conversations edifying and uplifting.</blockquote>\n\n"
                "<i>Click Next to meet the YouThopia Bot Family!</i>"
            )
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="⬅️ Back", callback_data="onboarding_1"),
                    InlineKeyboardButton(text="Next ➡️", callback_data="onboarding_3")
                ]
            ])
        elif page == 3:
            text = (
                "<b>Meet the Bot Family 🤖 (3/3)</b>\n"
                "<blockquote><b>Theo</b> (@iamtheobot) - Your daily devotional companion.\n"
                "<b>Lusy</b> (@iamlusybot) - Play games and earn YP!\n"
                "<b>Pete</b> (@iampetebot) - The security guard.\n"
                "<b>Ed</b> (@iamedyybot) - Announcements and events.\n"
                "<b>Susy</b> (Me!) - Your guide and friend.</blockquote>\n\n"
                "<i>Click Finish to complete your orientation!</i>"
            )
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="⬅️ Back", callback_data="onboarding_2"),
                    InlineKeyboardButton(text="Finish Exploring", callback_data="onboarding_finish")
                ]
            ])
            
        if edit:
            await message.edit_text(text, parse_mode="HTML", reply_markup=markup)
        else:
            await message.answer(text, parse_mode="HTML", reply_markup=markup)

    @router.callback_query(F.data.startswith("onboarding_"))
    async def handle_onboarding_callbacks(callback_query: CallbackQuery, services: ServiceContainer) -> None:
        action = callback_query.data.split("_")[1]
        
        if action in ["1", "2", "3"]:
            await send_onboarding_page(callback_query.message, int(action), edit=True)
            await callback_query.answer()
        elif action == "finish":
            user = await services.identity.resolve_telegram_user(callback_query.from_user)
            
            # Check if they have already completed orientation
            if user.get("engagement_level") in ["new", None]:
                # Grant 50 initial points for completing orientation via moderation service
                await services.moderation.record_action(
                    user_id=user["id"],
                    action_type="orientation_completed",
                    reason="Completed the Susy onboarding guide.",
                    trust_delta=50
                )
                await services.users.set_engagement_level(user["id"], "onboarded")
                
                finish_text = (
                    "<b>Exploration Complete! 🎉</b>\n"
                    "<blockquote>You are now officially a YouTopian! I've granted you <b>+50 Trust Points</b> for completing your exploration.</blockquote>\n\n"
                    "Head back to the main group and start <a href=\"https://t.me/youthopiabiblecommunity\">fellowship!</a>"
                )
                await callback_query.answer("Exploration Complete! +50 Trust Points!")
            else:
                # They already did it
                finish_text = (
                    "<b>Exploration Reviewed!</b>\n"
                    "<blockquote>It looks like you've already completed your official exploration! No extra points were granted, but it's always great to refresh your memory about the community.</blockquote>\n\n"
                    "Head back to the main group and start <a href=\"https://t.me/youthopiabiblecommunity\">fellowship!</a>"
                )
                await callback_query.answer("Exploration Reviewed!")
                
            await callback_query.message.edit_text(finish_text, parse_mode="HTML")

    @router.message(Command("help"))
    async def handle_help(message: Message, services: ServiceContainer) -> None:
        # Group Cleanup Mechanism
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
            return
                
        first_name = message.from_user.first_name or "Friend"
        help_text = (
            f"<b>Susy's Help Guide, {first_name}!</b>\n"
            "<blockquote>I'm Susy (@iamsusiebot). I am your onboarding specialist and guide to the community!</blockquote>\n\n"
            "<b>Meet the YouThopia Bot Family</b>\n"
            "<blockquote><b>Theo</b> - <a href=\"https://t.me/iamtheobot\">@iamtheobot</a>\n"
            "Your daily Bible companion. Devotionals, verses, and reflection.\n\n"
            "<b>Lusy</b> - <a href=\"https://t.me/iamlusybot\">@iamlusybot</a>\n"
            "Games, YP, and fun! Earn points and grow your rank.\n\n"
            "<b>Pete</b> - <a href=\"https://t.me/iampetebot\">@iampetebot</a>\n"
            "Security and moderation. Keeping our community safe.\n\n"
            "<b>Ed</b> - <a href=\"https://t.me/iamedyybot\">@iamedyybot</a>\n"
            "Events and announcements. Never miss what is happening.</blockquote>\n\n"
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
        
        sent_msg = await message.answer(
            help_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=markup
        )
        
        # Removed group auto-delete (command is now private only)

    def _get_music_controls_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="⏸️ Pause", callback_data="susy_pause"),
                    InlineKeyboardButton(text="▶️ Resume", callback_data="susy_resume"),
                    InlineKeyboardButton(text="⏭️ Skip", callback_data="susy_skip"),
                    InlineKeyboardButton(text="⏹️ Stop", callback_data="susy_stop"),
                ]
            ]
        )

    @router.message(Command("playsong"))
    async def handle_play(message: Message, command: CommandObject) -> None:
        if message.chat.type == "private":
            await message.answer("🎧 Music playback is designed for Telegram Group Voice Chats! Please use `/playsong` inside a group chat with an active Voice Chat.", parse_mode="Markdown")
            return

        if not music_service:
            await message.answer("My music engine is currently offline!")
            return
            
        if not command.args:
            await message.answer("Please provide a song name or link!\nExample: `/playsong Oceans Hillsong`", parse_mode="Markdown")
            return
            
        status_msg = await message.answer("🔍 Searching for your track...")
        try:
            result = await music_service.play(message.chat.id, command.args)
            try:
                await status_msg.delete()
            except Exception:
                pass

            if result.track:
                duration_min = result.track.duration // 60
                duration_sec = result.track.duration % 60
                dur_str = f"{duration_min}:{duration_sec:02d}" if result.track.duration else "Live Stream"
                user_mention = message.from_user.mention_html() if message.from_user else "User"
                
                caption = (
                    f"🎶 <b>Now Playing</b>\n\n"
                    f"🎵 <b>Title:</b> {result.track.title}\n"
                    f"⏱️ <b>Duration:</b> {dur_str}\n"
                    f"🎧 <b>Requested by:</b> {user_mention}"
                )
                
                if result.track.thumbnail_url:
                    try:
                        await message.answer_photo(
                            photo=result.track.thumbnail_url,
                            caption=caption,
                            parse_mode="HTML",
                            reply_markup=_get_music_controls_keyboard()
                        )
                        return
                    except Exception as photo_err:
                        print(f"SUSY PHOTO CARD NOTICE: {photo_err}")

                await message.answer(
                    caption,
                    parse_mode="HTML",
                    reply_markup=_get_music_controls_keyboard()
                )
            else:
                await message.answer(result.message)
        except Exception as e:
            try:
                await status_msg.edit_text(f"Error: {e}")
            except Exception:
                await message.answer(f"Error: {e}")

    @router.callback_query(F.data.startswith("susy_"))
    async def handle_music_callback(callback: CallbackQuery) -> None:
        if not music_service:
            await callback.answer("Music service offline", show_alert=True)
            return
            
        action = callback.data.replace("susy_", "")
        chat_id = callback.message.chat.id
        
        if action == "pause":
            res = await music_service.pause(chat_id)
            await callback.answer(res.message)
        elif action == "resume":
            res = await music_service.resume(chat_id)
            await callback.answer(res.message)
        elif action == "skip":
            res = await music_service.skip(chat_id)
            await callback.answer(res.message)
            await callback.message.answer(f"⏭️ {res.message}")
        elif action == "stop":
            res = await music_service.stop(chat_id)
            await callback.answer(res.message)
            await callback.message.answer(f"⏹️ {res.message}")

    @router.message(Command("stop"))
    async def handle_stop(message: Message) -> None:
        if not music_service:
            return
        result = await music_service.stop(message.chat.id)
        await message.answer(result.message)

    @router.message(Command("skip"))
    async def handle_skip(message: Message) -> None:
        if not music_service:
            return
        result = await music_service.skip(message.chat.id)
        await message.answer(result.message)

    @router.message(Command("pause"))
    async def handle_pause(message: Message) -> None:
        if not music_service:
            return
        result = await music_service.pause(message.chat.id)
        await message.answer(result.message)
        
    @router.message(Command("resume"))
    async def handle_resume(message: Message) -> None:
        if not music_service:
            return
        result = await music_service.resume(message.chat.id)
        await message.answer(result.message)

    return router
