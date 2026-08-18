from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from shared.utils.ui import GLOBAL_REPLY_BUTTONS


def build_lusy_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Lusy persistent reply keyboard:
    Row 1 (Global):        [ 👤 My Profile ]  [ ℹ️ Help ]         [ 🌐 Community ]
    Row 2 (Bot Specific): [ 🎮 Play Games ]  [ 🏆 Leaderboard ]  [ ⭐ My Points ]
    Row 3 (Control):       [ 🛑 Quit Game ]
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            GLOBAL_REPLY_BUTTONS,
            [
                KeyboardButton(text="🎮 Play Games"),
                KeyboardButton(text="🏆 Leaderboard"),
                KeyboardButton(text="⭐ My Points"),
            ],
            [
                KeyboardButton(text="🛑 Quit Game"),
            ]
        ],
        resize_keyboard=True,
        persistent=True,
        input_field_placeholder="Choose a Lusy action..."
    )


def build_game_selection_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Lusy Game Mode Selection inline keyboard per spec:
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
