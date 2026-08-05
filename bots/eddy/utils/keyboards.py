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
