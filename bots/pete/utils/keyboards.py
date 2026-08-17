from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from shared.utils.ui import GLOBAL_REPLY_BUTTONS


def build_pete_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Pete persistent reply grid keyboard:
    Row 1 (Global): [ 👤 My Profile ]  [ ℹ️ Help ]  [ 🌐 Community ]
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            GLOBAL_REPLY_BUTTONS
        ],
        resize_keyboard=True,
        persistent=True,
        input_field_placeholder="Choose a Pete action..."
    )


def build_pete_start_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Pete DM /start Card Inline Keyboard (Cleaned):
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💬 Open Main Group",
                    url="https://t.me/youthopiabiblecommunity"
                )
            ]
        ]
    )


def build_pete_captcha_inline_keyboard(chat_id_str: str) -> InlineKeyboardMarkup:
    """
    Captcha Verification Inline Keyboard:
    [ 🛡️ Tap here to prove you are human ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛡️ Tap here to prove you are human",
                    callback_data=f"captcha|{chat_id_str}"
                )
            ]
        ]
    )


def build_pete_post_captcha_group_keyboard() -> InlineKeyboardMarkup:
    """
    Post-Captcha Group Announcement Inline Keyboard:
    [ 👋 Meet Susy in DM ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👋 Meet Susy in DM",
                    url="https://t.me/iamsusiebot?start=onboarding"
                )
            ]
        ]
    )
