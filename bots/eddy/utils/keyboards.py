from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from shared.utils.ui import GLOBAL_REPLY_BUTTONS


def build_eddy_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Ed persistent reply keyboard standard per YouThopiaOS UI Spec:
    Row 1 (Bot Specific): [ 📅 View Calendar ]  [ 🎫 My Events ]
    Row 2 (Bot Specific): [ 🎂 Add Birthday  ]  [ 🔔 Reminders ]
    Row 3 (Global):        [ 👤 My Profile ]  [ ℹ️ Help ]  [ 🌐 Community Links ]
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📅 View Calendar"),
                KeyboardButton(text="🎫 My Events"),
            ],
            [
                KeyboardButton(text="🎂 Add Birthday"),
                KeyboardButton(text="🔔 Reminders"),
            ],
            GLOBAL_REPLY_BUTTONS,
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
