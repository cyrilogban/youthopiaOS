from __future__ import annotations

import asyncio
import os
from pathlib import Path
import httpx
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
    ReplyKeyboardMarkup,
    KeyboardButton,
    BufferedInputFile,
    FSInputFile,
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
            BotCommand(command="start", description="Meet Susy & Welcome"),
            BotCommand(command="where", description="Community Topic Directory"),
            BotCommand(command="help", description="Susy Hostess Guide"),
        ]
        
        group_commands = [
            BotCommand(command="start", description="Meet Susy"),
            BotCommand(command="where", description="Community Topic Directory"),
            BotCommand(command="help", description="Susy Hostess Guide"),
        ]
        
        await bot.delete_my_commands()
        await bot.set_my_commands(private_commands, scope=BotCommandScopeAllPrivateChats())
        await bot.set_my_commands(group_commands, scope=BotCommandScopeAllGroupChats())

    @router.my_chat_member()
    async def on_bot_added(event, bot: Bot) -> None:
        if event.new_chat_member.status in {"member", "administrator"}:
            first_name = event.from_user.first_name if event.from_user else "Friend"
            chat_title = event.chat.title or "your group"
            
            welcome_caption = (
                f"🌸 <b>Hey {first_name}, This is Susy!</b>\n\n"
                f"Thanks for having me in <b>{chat_title}</b>! I am your friendly community hostess.\n\n"
                f"I'm here to make sure every member feels welcomed, connected, and guided across our community!"
            )
            
            welcome_markup = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🌸 Meet Susy in DM", url="https://t.me/iamsusiebot")
                ],
                [
                    InlineKeyboardButton(text="🗑️ Close", callback_data="susy_close_msg")
                ]
            ])
            
            try:
                await bot.send_message(
                    chat_id=event.chat.id,
                    text=welcome_caption,
                    parse_mode="HTML",
                    reply_markup=welcome_markup
                )
            except Exception as e:
                print(f"SUSY BOT ADDED WELCOME NOTICE: {e}")


    async def send_group_welcome_card(message: Message) -> None:
        first_name = message.from_user.first_name if message.from_user else "Friend"
        chat_title = message.chat.title or "your community"

        welcome_text = (
            f"🌸 <b>Hey {first_name}, This is Susy!</b>\n\n"
            f"Thanks for having me in <b>{chat_title}</b>! I am your community hostess.\n\n"
            f"I am here to welcome you, answer your questions, and guide you around!"
        )

        welcome_markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🌸 Meet Susy in DM", url="https://t.me/iamsusiebot")
            ],
            [
                InlineKeyboardButton(text="🗑️ Close", callback_data="susy_close_msg")
            ]
        ])

        banner_url = "https://images.unsplash.com/photo-1507692049790-de58290a4334?w=1200&q=80"
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(banner_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                if resp.status_code == 200:
                    banner_file = BufferedInputFile(resp.content, filename="welcome.jpg")
                    await message.answer_photo(
                        photo=banner_file,
                        caption=welcome_text,
                        parse_mode="HTML",
                        reply_markup=welcome_markup
                    )
                    return
        except Exception:
            pass

        await message.answer(welcome_text, parse_mode="HTML", reply_markup=welcome_markup)

    @router.message(Command("start"))
    async def handle_start(message: Message, command: CommandObject, services: ServiceContainer) -> None:
        # Group Cleanup & Targeted Start Mechanism
        if message.chat.type != "private":
            is_targeted = message.text and ("susy" in message.text.lower() or "@" in message.text)
            if not is_targeted:
                try:
                    await message.delete()
                except Exception:
                    pass
                return
            await send_group_welcome_card(message)
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
            


    @router.message(Command("where"))
    async def on_where_command(message: Message):
        directory_text = (
            "<b>🗺️ YouThopia Topic Directory & Guide</b>\n\n"
            "<blockquote>Where would you like to go today? Here is your quick map to our group threads:</blockquote>\n\n"
            "📢 <b>Announcements & Events:</b> Stay up to date with community news.\n"
            "📖 <b>Devotionals & Scripture:</b> Daily inspiration with Theo (@iamtheobot).\n"
            "🎮 <b>Games & Quizzes:</b> Test your Bible knowledge with Lusy (@iamlusybot).\n"
            "🙏 <b>Prayer & Testimonies:</b> Stand in faith and share praise reports.\n"
            "💬 <b>General Fellowship:</b> Connect and chat with fellow YouTopians!\n\n"
            "<i>Tap below to jump right into the main group! 💜</i>"
        )
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Open YouThopia Group", url="https://t.me/youthopiabiblecommunity")]
        ])
        await message.answer(directory_text, parse_mode="HTML", reply_markup=markup)

    @router.message(F.text == "Community")
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

    @router.message(Command("playlist"))
    @router.message(F.text == "My Playlist")
    @router.callback_query(F.data == "susy_my_playlist")
    async def handle_my_playlist(event: Message | CallbackQuery, services: ServiceContainer) -> None:
        is_cb = isinstance(event, CallbackQuery)
        message = event.message if is_cb else event
        user_obj = event.from_user

        empty_txt = (
            "<b>📜 Your Personal Playlist is Empty!</b>\n\n"
            "You haven't saved any tracks yet. Play a song and tap <b>💜 Save to Favorites</b> to build your collection!"
        )

        try:
            user = await services.identity.resolve_telegram_user(user_obj)
            user_id = user["id"]

            try:
                saved_tracks = await services.supabase.find_many("user_favorite_tracks", {"user_id": user_id})
            except Exception as e:
                saved_tracks = []

            if not saved_tracks:
                if is_cb:
                    await event.answer("Your playlist is currently empty! Play a song to save it. 💜", show_alert=True)
                else:
                    await message.answer(empty_txt, parse_mode="HTML")
                return

            list_txt = "<b>📜 Your Saved Playlist 🎶</b>\n\n"
            for idx, tr in enumerate(saved_tracks, 1):
                list_txt += f"{idx}. <b>{tr.get('title', 'Unknown Track')}</b>\n"

            list_txt += "\n<i>Type the name of any track to play it instantly!</i>"

            if is_cb:
                await event.answer()
            await message.answer(list_txt, parse_mode="HTML")
        except Exception:
            if is_cb:
                await event.answer("Your playlist is currently empty! Play a song to save it. 💜", show_alert=True)
            else:
                await message.answer(empty_txt, parse_mode="HTML")

    # --- DM MUSIC QUERY (DISABLED - PRESERVED FOR FUTURE REUSE) ---
    # @router.message(F.chat.type == "private", F.text & ~F.text.startswith("/"))
    # async def handle_private_dm_music_query(message: Message) -> None:
    #     ...


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
    @router.message(F.text == "Help")
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

    def _get_dm_music_controls_keyboard(is_saved: bool = False) -> InlineKeyboardMarkup:
        save_text = "💜 Saved in Playlist" if is_saved else "💜 Save to Favorites"
        share_url = "https://t.me/share/url?url=https%3A%2F%2Ft.me%2Fiamsusiebot&text=Listen%20to%20worship%20music%20with%20Susy%20on%20Telegram%20%F0%9F%8E%B6"
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=save_text, callback_data="susy_fav_save"),
                    InlineKeyboardButton(text="📜 My Playlist", callback_data="susy_my_playlist")
                ],
                [
                    InlineKeyboardButton(text="➕ Request Another", callback_data="susy_request_another"),
                    InlineKeyboardButton(text="👥 Share Track ↗️", url=share_url)
                ]
            ]
        )

    def _get_music_controls_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="💜 Save to Favorites", callback_data="susy_fav_save"),
                    InlineKeyboardButton(text="📜 My Playlist", callback_data="susy_group_playlist")
                ],
                [
                    InlineKeyboardButton(text="➕ Request Another", callback_data="susy_group_request"),
                    InlineKeyboardButton(text="💬 Open Susy DM ↗️", url="https://t.me/iamsusiebot")
                ],
                [
                    InlineKeyboardButton(text="🗑️ Close", callback_data="susy_close_msg")
                ]
            ]
        )

    @router.callback_query(F.data == "susy_fav_save")
    async def handle_save_favorite(callback: CallbackQuery, services: ServiceContainer) -> None:
        track_title = "Worship Track"
        if callback.message and callback.message.caption:
            for line in callback.message.caption.split("\n"):
                if "Title:" in line:
                    track_title = line.replace("Title:", "").replace("<b>", "").replace("</b>", "").strip()

        try:
            user = await services.identity.resolve_telegram_user(callback.from_user)
            user_id = user["id"]

            payload = {
                "user_id": user_id,
                "title": track_title,
                "bot_name": "susy"
            }

            await services.supabase.upsert(
                "user_favorite_tracks",
                payload,
                on_conflict="user_id, title"
            )

            is_private = callback.message and callback.message.chat.type == "private"

            if is_private:
                try:
                    await callback.message.edit_reply_markup(reply_markup=_get_dm_music_controls_keyboard(is_saved=True))
                except Exception:
                    pass

                await callback.answer(
                    f"🎉 Saved to Favorites! 💜\n\n"
                    f"\"{track_title}\" has been added to your personal playlist.\n\n"
                    f"Tap '📜 My Playlist' below to view your saved songs!",
                    show_alert=True
                )
            else:
                await callback.answer(
                    f"🎉 Saved to Favorites! 💜\n\n"
                    f"\"{track_title}\" has been saved to your personal playlist.\n\n"
                    f"Open a private chat with Susy (@iamsusiebot) to view your saved songs!",
                    show_alert=True
                )
        except Exception as e:
            await callback.answer(f"🎉 \"{track_title}\" saved to your playlist! 💜", show_alert=True)

    @router.callback_query(F.data == "susy_group_playlist")
    async def handle_group_playlist(callback: CallbackQuery) -> None:
        await callback.answer(
            "📜 Your Saved Playlist:\n\n"
            "Open a private chat with Susy (@iamsusiebot) and type /playlist to view and play your saved songs!",
            show_alert=True
        )

    @router.callback_query(F.data == "susy_group_request")
    async def handle_group_request(callback: CallbackQuery) -> None:
        await callback.answer(
            "🎶 Request a Song:\n\n"
            "Type /playsong <song name> right here in this chat to request your next song!",
            show_alert=True
        )

    @router.callback_query(F.data == "susy_request_another")
    async def handle_request_another(callback: CallbackQuery) -> None:
        await callback.answer("🎧 Type the title or link of your next song right here in this chat!", show_alert=True)

    # --- MUSIC COMMANDS & CALLBACKS (DISABLED - PRESERVED FOR FUTURE REUSE) ---
    # @router.message(Command("playsong"))
    # async def handle_play(message: Message, command: CommandObject) -> None:
    #     ...
    # @router.message(Command("stop")) ...

    @router.callback_query(F.data == "susy_close_msg")
    async def handle_close_msg(callback: CallbackQuery) -> None:
        try:
            await callback.message.delete()
        except Exception:
            await callback.answer("Message closed")

    return router
