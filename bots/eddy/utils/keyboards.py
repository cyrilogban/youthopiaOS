from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from shared.utils.ui import GLOBAL_REPLY_BUTTONS


def build_eddy_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Ed persistent reply keyboard:
    Row 1 (Global):        [ 👤 My Profile ]  [ ℹ️ Help ]  [ 🌐 Community ]
    Row 2 (Bot Specific): [ 📅 View Calendar ]  [ 🎫 My Events ]
    Row 3 (Bot Specific): [ 🎂 Add Birthday  ]  [ 🔔 Reminders ]
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            GLOBAL_REPLY_BUTTONS,
            [
                KeyboardButton(text="📅 View Calendar"),
                KeyboardButton(text="🎫 My Events"),
            ],
            [
                KeyboardButton(text="🎂 Add Birthday"),
                KeyboardButton(text="🔔 Reminders"),
            ],
        ],
        resize_keyboard=True,
        persistent=True,
        input_field_placeholder="Choose an Ed action..."
    )


def build_eddy_start_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Eddy DM /start Card Inline Keyboard:
    [ 📅 View Calendar ]  [ 🎂 Add Birthday ]
    [ 🌐 Community ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 View Calendar", callback_data="eddy_view_calendar"),
                InlineKeyboardButton(text="🎂 Add Birthday", callback_data="eddy_add_bday_init"),
            ],
            [
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
                InlineKeyboardButton(text="📅 View Calendar", callback_data="eddy_view_calendar"),
                InlineKeyboardButton(text="🌐 Community", callback_data="eddy_community_links"),
            ],
            [
                InlineKeyboardButton(text="🌐 YouThopiaOS Ecosystem", callback_data="eddy_menu_directory"),
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
                InlineKeyboardButton(text="⚡ Promote Eddy to Admin", callback_data="eddy_prompt_admin"),
            ],
            [
                InlineKeyboardButton(text="📅 View Calendar", callback_data="eddy_view_calendar"),
                InlineKeyboardButton(text="🌐 Community", callback_data="eddy_community_links"),
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
                InlineKeyboardButton(text="🌐 Explore Ecosystem", callback_data="eddy_menu_directory"),
                InlineKeyboardButton(text="➕ Re-invite Eddy", url="https://t.me/iamedyybot?startgroup=true"),
            ]
        ]
    )


def build_event_card_inline_keyboard(event_id: str, is_attending: bool = False) -> InlineKeyboardMarkup:
    """
    Event Card Inline Keyboard per spec:
    [ ✅ I'm Attending ]  [ 👥 View Attendees ]  [ 🔔 Set Reminder ]
    """
    attend_text = "✅ Attending" if is_attending else "✅ I'm Attending"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=attend_text, callback_data=f"eddy_rsvp_{event_id}"),
                InlineKeyboardButton(text="👥 View Attendees", callback_data=f"eddy_attendees_{event_id}"),
            ],
            [
                InlineKeyboardButton(text="🔔 Set Reminder", callback_data=f"eddy_remind_{event_id}"),
            ]
        ]
    )
