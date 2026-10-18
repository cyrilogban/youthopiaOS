from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from shared.utils.ui import GLOBAL_REPLY_BUTTONS, get_open_app_inline_button
from shared.config.bot_registry import get_bot_identity, DEFAULT_MINI_APP_LINK


def build_lusy_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Lusy persistent reply keyboard:
    Row 1 (Global):        [ 👤 My Profile ]  [ ℹ️ Help ]         [ 🌐 Community ]
    Row 2 (Bot Specific): [ 🎯 Play Quizzes ] [ 🏆 Leaderboard ]  [ ⭐ My Points ]
    Row 3 (Control):       [ 🛑 Quit Quiz ]
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            GLOBAL_REPLY_BUTTONS,
            [
                KeyboardButton(text="Play Quizzes"),
                KeyboardButton(text="Leaderboard"),
                KeyboardButton(text="My Points"),
            ],
            [
                KeyboardButton(text="Quit Quiz"),
            ]
        ],
        resize_keyboard=True,
        persistent=True,
        input_field_placeholder="Choose a Lucy action..."
    )


def build_game_selection_inline_keyboard(is_group: bool = False) -> InlineKeyboardMarkup:
    """
    Lusy Quiz Mode Selection inline keyboard:
    [ Open App ]
    [ 📖 Bible Challenge ]
    [ ✍️ Verse Completion ]
    [ 🔀 Verse Scramble ]
    [ ⚡ Trivia Race ]
    """
    open_app_btn = InlineKeyboardButton(text="Open App", url=DEFAULT_MINI_APP_LINK) if is_group else get_open_app_inline_button()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [open_app_btn],
            [InlineKeyboardButton(text="📖 Bible Challenge", callback_data="lusy_play_quiz")],
            [InlineKeyboardButton(text="✍️ Verse Completion", callback_data="lusy_play_fill_blank")],
            [InlineKeyboardButton(text="🔀 Verse Scramble", callback_data="lusy_play_scramble")],
            [InlineKeyboardButton(text="⚡ Trivia Race", callback_data="lusy_play_race")],
        ]
    )


def build_lusy_group_welcome_keyboard() -> InlineKeyboardMarkup:
    """
    Inline keyboard attached to Lusy's group welcome card (Admin).
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Open App", url=DEFAULT_MINI_APP_LINK),
            ],
            [
                InlineKeyboardButton(text="🎯 Start Quiz", callback_data="lusy_menu_play"),
                InlineKeyboardButton(text="🏆 Rankings", callback_data="lusy_menu_leaderboard"),
            ],
            [
                InlineKeyboardButton(text="🧭 Start Community Tour", url=get_bot_identity("lusy").get_start_link("tour")),
            ],
        ]
    )


def build_lusy_member_welcome_keyboard() -> InlineKeyboardMarkup:
    """
    Inline keyboard attached to Lusy's group welcome card (Regular Member).
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Open App", url=DEFAULT_MINI_APP_LINK),
            ],
            [
                InlineKeyboardButton(text="⚡ Promote Lucy to Admin", callback_data="lusy_prompt_admin"),
            ],
            [
                InlineKeyboardButton(text="🎯 Start Quiz", callback_data="lusy_menu_play"),
                InlineKeyboardButton(text="🏆 Rankings", callback_data="lusy_menu_leaderboard"),
            ],
            [
                InlineKeyboardButton(text="🧭 Start Community Tour", url=get_bot_identity("lusy").get_start_link("tour")),
            ],
        ]
    )


def build_lusy_farewell_keyboard() -> InlineKeyboardMarkup:
    """
    Compact inline keyboard attached to Lusy's farewell messages.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🧭 Community Tour", url=get_bot_identity("lusy").get_start_link("tour")),
                InlineKeyboardButton(text="➕ Re-invite Lucy", url="https://t.me/lusiequizbot?startgroup=true"),
            ],
        ]
    )
