from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from shared.utils.ui import GLOBAL_REPLY_BUTTONS, get_open_app_inline_button
from shared.config.bot_registry import get_bot_identity, DEFAULT_MINI_APP_LINK


def build_eddy_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Edmund persistent reply keyboard:
    Row 1 (Global):        [ ðŸ‘¤ My Profile ]  [ â„¹ï¸ Help ]  [ ðŸŒ Community ]
    Row 2 (Bot Specific): [ ðŸ“… View Calendar ]  [ ðŸŽ« My Events ]
    Row 3 (Bot Specific): [ ðŸŽ‚ Add Birthday  ]  [ ðŸ”” Reminders ]
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            GLOBAL_REPLY_BUTTONS,
            [
                KeyboardButton(text="ðŸ“… View Calendar"),
                KeyboardButton(text="ðŸŽ« My Events"),
            ],
            [
                KeyboardButton(text="ðŸŽ‚ Add Birthday"),
                KeyboardButton(text="ðŸ”” Reminders"),
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
    [ ðŸ“… Calendar ]  [ ðŸŒ Community ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                get_open_app_inline_button(),
            ],
            [
                InlineKeyboardButton(text="ðŸ“… Calendar", callback_data="eddy_view_calendar"),
                InlineKeyboardButton(text="ðŸŒ Community", callback_data="eddy_community_links"),
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
                InlineKeyboardButton(text="ðŸ“… Calendar", callback_data="eddy_view_calendar"),
                InlineKeyboardButton(text="ðŸŒ Community", callback_data="eddy_community_links"),
            ],
            [
                InlineKeyboardButton(text="ðŸ§­ Start Community Tour", url=get_bot_identity("eddy").get_start_link("tour")),
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
                InlineKeyboardButton(text="âš¡ Promote Edmund to Admin", callback_data="eddy_prompt_admin"),
            ],
            [
                InlineKeyboardButton(text="ðŸ“… Calendar", callback_data="eddy_view_calendar"),
                InlineKeyboardButton(text="ðŸŒ Community", callback_data="eddy_community_links"),
            ],
            [
                InlineKeyboardButton(text="ðŸ§­ Start Community Tour", url=get_bot_identity("eddy").get_start_link("tour")),
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
                InlineKeyboardButton(text="ðŸ§­ Community Tour", url=get_bot_identity("eddy").get_start_link("tour")),
                InlineKeyboardButton(text="âž• Re-invite Edmund", url="https://t.me/ediecalendarbot?startgroup=true"),
            ]
        ]
    )
