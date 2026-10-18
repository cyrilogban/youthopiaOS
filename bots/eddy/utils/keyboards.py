from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from shared.utils.ui import GLOBAL_REPLY_BUTTONS, get_open_app_inline_button
from shared.config.bot_registry import get_bot_identity, DEFAULT_MINI_APP_LINK


def build_eddy_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Edmund persistent reply keyboard:
    Row 1 (Global):        [ 👤 My Profile ]  [ ℹ️ Help ]  [ 🌐 Community ]
    Row 2 (Bot Specific): [ 📅 View Calendar ]  [ 🎫 My Events ]
    Row 3 (Bot Specific): [ 🎂 Add Birthday  ]  [ 🔔 Reminders ]
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            GLOBAL_REPLY_BUTTONS,
            [
                KeyboardButton(text="View Calendar"),
                KeyboardButton(text="My Events"),
            ],
            [
                KeyboardButton(text="Add Birthday"),
                KeyboardButton(text="Reminders"),
            ],
        ],
        resize_keyboard=True,
        persistent=True,
        input_field_placeholder="Choose an Edmund action..."
    )


def build_eddy_start_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Eddy DM /start Card Inline Keyboard:
    [ Open App ]
    [ 📅 Calendar ]  [ 🌐 Community ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                get_open_app_inline_button(),
            ],
            [
                InlineKeyboardButton(text="📅 Calendar", callback_data="eddy_view_calendar"),
                InlineKeyboardButton(text="🌐 Community", callback_data="eddy_community_links"),
            ]
        ]
    )


def build_eddy_group_welcome_keyboard() -> InlineKeyboardMarkup:
    """
    Inline keyboard attached to Eddy's group welcome card (Admin).
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Open App", url=DEFAULT_MINI_APP_LINK),
            ],
            [
                InlineKeyboardButton(text="📅 Calendar", callback_data="eddy_view_calendar"),
                InlineKeyboardButton(text="🌐 Community", callback_data="eddy_community_links"),
            ],
            [
                InlineKeyboardButton(text="🧭 Start Community Tour", url=get_bot_identity("eddy").get_start_link("tour")),
            ]
        ]
    )


def build_eddy_member_welcome_keyboard() -> InlineKeyboardMarkup:
    """
    Inline keyboard attached to Eddy's group welcome card (Regular Member).
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Open App", url=DEFAULT_MINI_APP_LINK),
            ],
            [
                InlineKeyboardButton(text="⚡ Promote Edmund to Admin", callback_data="eddy_prompt_admin"),
            ],
            [
                InlineKeyboardButton(text="📅 Calendar", callback_data="eddy_view_calendar"),
                InlineKeyboardButton(text="🌐 Community", callback_data="eddy_community_links"),
            ],
            [
                InlineKeyboardButton(text="🧭 Start Community Tour", url=get_bot_identity("eddy").get_start_link("tour")),
            ]
        ]
    )


def build_eddy_farewell_keyboard() -> InlineKeyboardMarkup:
    """
    Compact inline keyboard attached to Eddy's farewell messages.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🧭 Community Tour", url=get_bot_identity("eddy").get_start_link("tour")),
                InlineKeyboardButton(text="➕ Re-invite Edmund", url="https://t.me/ediecalendarbot?startgroup=true"),
            ]
        ]
    )
