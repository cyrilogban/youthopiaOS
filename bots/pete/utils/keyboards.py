from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from shared.utils.ui import GLOBAL_REPLY_BUTTONS, get_open_app_inline_button


def build_pete_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Pete persistent reply grid keyboard:
    Row 1 (Global): [ 👤 My Profile ]  [ ℹ️ Help ]  [ 🌐 Community ]
    Row 2 (Pete Specific): [ 📝 Submit Appeal ]
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            GLOBAL_REPLY_BUTTONS,
            [
                KeyboardButton(text="📝 Submit Appeal")
            ]
        ],
        resize_keyboard=True,
        persistent=True,
        input_field_placeholder="Choose a Pete action..."
    )


def build_pete_start_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Pete DM /start Card Inline Keyboard:
    [ Open App ]
    [ 📝 Appeal ]  [ 🌐 Community ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                get_open_app_inline_button(),
            ],
            [
                InlineKeyboardButton(text="📝 Appeal", callback_data="appeal_init"),
                InlineKeyboardButton(text="🌐 Community", callback_data="pete_community_links"),
            ]
        ]
    )


def build_pete_group_welcome_keyboard() -> InlineKeyboardMarkup:
    """
    Inline keyboard attached to Pete's group welcome card (Admin).
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                get_open_app_inline_button(),
            ],
            [
                InlineKeyboardButton(text="📝 Appeal", callback_data="appeal_init"),
                InlineKeyboardButton(text="🌐 Community", callback_data="pete_community_links"),
            ],
            [
                InlineKeyboardButton(text="🌐 Explore Ecosystem", callback_data="pete_menu_directory"),
            ]
        ]
    )


def build_pete_member_welcome_keyboard() -> InlineKeyboardMarkup:
    """
    Inline keyboard attached to Pete's group welcome card (Regular Member).
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                get_open_app_inline_button(),
            ],
            [
                InlineKeyboardButton(text="⚡ Promote Pete to Admin", callback_data="pete_prompt_admin"),
            ],
            [
                InlineKeyboardButton(text="📝 Appeal", callback_data="appeal_init"),
                InlineKeyboardButton(text="🌐 Community", callback_data="pete_community_links"),
            ]
        ]
    )


def build_pete_farewell_keyboard() -> InlineKeyboardMarkup:
    """
    Compact inline keyboard attached to Pete's farewell messages.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🌐 Explore Ecosystem", callback_data="pete_menu_directory"),
                InlineKeyboardButton(text="➕ Re-invite Pete", url="https://t.me/iampetebot?startgroup=true"),
            ]
        ]
    )


def build_pete_captcha_inline_keyboard(chat_id_str: str) -> InlineKeyboardMarkup:
    """
    Captcha Verification Inline Keyboard:
    [ 🛡️ Verify Human (Tap Here) ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛡️ Verify Human (Tap Here)",
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
