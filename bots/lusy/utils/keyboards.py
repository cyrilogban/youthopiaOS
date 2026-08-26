from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from shared.utils.ui import GLOBAL_REPLY_BUTTONS


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
                KeyboardButton(text="🎯 Play Quizzes"),
                KeyboardButton(text="🏆 Leaderboard"),
                KeyboardButton(text="⭐ My Points"),
            ],
            [
                KeyboardButton(text="🛑 Quit Quiz"),
            ]
        ],
        resize_keyboard=True,
        persistent=True,
        input_field_placeholder="Choose a Lusy action..."
    )


def build_game_selection_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Lusy Quiz Mode Selection inline keyboard per spec:
    [ 📖 Bible Challenge ]  [ ✍️ Verse Completion ]
    [ 🔀 Verse Scramble  ]  [ ⚡ Trivia Race      ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📖 Bible Challenge", callback_data="lusy_play_quiz"),
                InlineKeyboardButton(text="✍️ Verse Completion", callback_data="lusy_play_fill_blank"),
            ],
            [
                InlineKeyboardButton(text="🔀 Verse Scramble", callback_data="lusy_play_scramble"),
                InlineKeyboardButton(text="⚡ Trivia Race", callback_data="lusy_play_race"),
            ],
        ]
    )


build_quiz_selection_inline_keyboard = build_game_selection_inline_keyboard


def build_lusy_group_welcome_keyboard() -> InlineKeyboardMarkup:
    """
    Inline keyboard attached to Lusy's group welcome card (Admin).
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎯 Start a Quiz", callback_data="lusy_menu_play"),
                InlineKeyboardButton(text="🏆 Global Leaderboard", callback_data="lusy_menu_leaderboard"),
            ],
            [
                InlineKeyboardButton(text="🌐 YouThopiaOS Ecosystem & Directory", callback_data="lusy_menu_directory"),
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
                InlineKeyboardButton(text="⚡ Promote Lusy to Group Admin", callback_data="lusy_prompt_admin"),
            ],
            [
                InlineKeyboardButton(text="🎯 Start a Quiz", callback_data="lusy_menu_play"),
                InlineKeyboardButton(text="🏆 Global Leaderboard", callback_data="lusy_menu_leaderboard"),
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
                InlineKeyboardButton(text="🌐 Explore Ecosystem", url="https://t.me/youthopiaos_bot"),
                InlineKeyboardButton(text="➕ Re-invite Lusy", url="https://t.me/iamlusybot?startgroup=true"),
            ],
        ]
    )
