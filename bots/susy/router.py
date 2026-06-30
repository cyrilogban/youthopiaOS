from __future__ import annotations

import asyncio
from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import (
    Message,
    BotCommand,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllGroupChats,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from core.telegram_runtime import build_router
from aiogram.filters import Command, CommandObject

# Will add Susy's official photo URL here when available
SUSY_PHOTO = None

def build_susy_router(description: str, music_service=None) -> Router:
    router = build_router("susy", description, include_base_commands=False)

    @router.startup()
    async def on_startup(bot: Bot) -> None:
        # Define the exact sidebar commands requested
        commands = [
            BotCommand(command="start", description="Wake Up Susy"),
            BotCommand(command="help", description="Show help information"),
            BotCommand(command="download", description="Download a song"),
        ]
        
        # Apply them to DMs and Groups
        await bot.delete_my_commands()
        await bot.set_my_commands(commands, scope=BotCommandScopeAllPrivateChats())
        await bot.set_my_commands(commands, scope=BotCommandScopeAllGroupChats())

    @router.message(Command("start"))
    async def handle_start(message: Message, services: ServiceContainer) -> None:
        # Group Cleanup Mechanism
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
                
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
                InlineKeyboardButton(text="Explore the Community", callback_data="onboarding_1")
            ],
            [
                InlineKeyboardButton(text="Join Facebook", url="https://www.facebook.com/share/g/18wG8aWB6t/"),
                InlineKeyboardButton(text="Join Telegram", url="https://t.me/youthopiabiblecommunity"),
            ],
            [
                InlineKeyboardButton(text="Join WhatsApp", url="https://chat.whatsapp.com/HXZsnWjwizoHBojS2VwbHn"),
                InlineKeyboardButton(text="Join Threads", callback_data="ignore"),
            ]
        ])
        
        if SUSY_PHOTO:
            sent_msg = await message.answer_photo(
                photo=SUSY_PHOTO,
                caption=welcome_text,
                parse_mode="HTML",
                reply_markup=markup
            )
        else:
            sent_msg = await message.answer(
                welcome_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=markup
            )
            
        # Delete Susy's welcome message in groups after 15s to prevent spam
        if message.chat.type != "private":
            await asyncio.sleep(15)
            try:
                await sent_msg.delete()
            except Exception:
                pass

    # --- ONBOARDING PAGINATION LOGIC ---
    
    async def send_onboarding_page(message: Message | Any, page: int, edit: bool = False) -> None:
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
    async def handle_onboarding_callbacks(callback_query: Any, services: ServiceContainer) -> None:
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
        
        if message.chat.type != "private":
            await asyncio.sleep(15)
            try:
                await sent_msg.delete()
            except Exception:
                pass

    @router.message(Command("play"))
    async def handle_play(message: Message, command: CommandObject) -> None:
        if not music_service:
            await message.answer("My music engine is currently offline!")
            return
            
        if not command.args:
            await message.answer("Please provide a song name or YouTube link!\nExample: `/play Oceans Hillsong`", parse_mode="Markdown")
            return
            
        status_msg = await message.answer("🔍 Searching for your track...")
        try:
            result = await music_service.play(message.chat.id, command.args)
            await status_msg.edit_text(result.message)
        except Exception as e:
            await status_msg.edit_text(f"Error: {e}")

    @router.message(Command("download"))
    async def handle_download(message: Message, command: CommandObject) -> None:
        if not music_service:
            await message.answer("My music engine is currently offline!")
            return
            
        if not command.args:
            await message.answer("Please provide a song name or YouTube link!\nExample: `/download Oceans Hillsong`", parse_mode="Markdown")
            return
            
        status_msg = await message.answer("🔍 Searching and downloading... Give me a few seconds!")
        try:
            result = await music_service.fetch_track(command.args)
            if not result.track:
                await status_msg.edit_text(result.message)
                return
            
            track = result.track
            minutes = track.duration // 60
            seconds = track.duration % 60
            
            caption = (
                "⚡️ <b>Successfully Downloaded:</b>\n\n"
                f"🎶 <b>Title:</b> {track.title}\n"
                f"⏱ <b>Duration:</b> {minutes}:{seconds:02d} minutes\n"
                f"👤 <b>Requested by:</b> {message.from_user.first_name}\n"
                "🕊️"
            )
            
            if track.thumbnail_url:
                await message.answer_photo(
                    photo=track.thumbnail_url,
                    caption=caption,
                    parse_mode="HTML"
                )
            else:
                await message.answer(caption, parse_mode="HTML")
                
            from aiogram.types import FSInputFile
            import os
            
            audio_file = FSInputFile(track.file_path)
            await message.answer_audio(
                audio=audio_file,
                title=track.title,
                performer="YouThopia Music"
            )
            
            # Clean up the file
            if os.path.exists(track.file_path):
                os.remove(track.file_path)
                
            await status_msg.delete()
        except Exception as e:
            await status_msg.edit_text(f"Error fetching song: {e}")

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
