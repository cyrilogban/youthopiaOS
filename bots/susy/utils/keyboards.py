from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from shared.utils.ui import FACEBOOK_LINK, TELEGRAM_GROUP_LINK, WHATSAPP_LINK, GLOBAL_REPLY_BUTTONS


def build_susy_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Susy persistent reply grid keyboard:
    Row 1 (Global): [ 👤 My Profile ]  [ ℹ️ Help ]  [ 🌐 Community ]
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            GLOBAL_REPLY_BUTTONS
        ],
        resize_keyboard=True,
        persistent=True,
        input_field_placeholder="Choose a Susy action..."
    )


def build_susy_start_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Susy DM /start Welcome Card Inline Keyboard:
    [ 🚀 Start Tour ]  [ 🌐 Community ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚀 Start Tour", callback_data="onboarding_1"),
                InlineKeyboardButton(text="🌐 Community", callback_data="susy_community_links"),
            ]
        ]
    )


def build_onboarding_tour_keyboard(page: int) -> InlineKeyboardMarkup:
    """
    Interactive Onboarding Tour inline keyboards:
    Page 1: [ Next ➡️ ]
    Page 2: [ ⬅️ Back ]  [ Next ➡️ ]
    Page 3: [ ⬅️ Back ]  [ ✅ Finish Tour ]
    """
    if page == 1:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Next ➡️", callback_data="onboarding_2")]
            ]
        )
    elif page == 2:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="⬅️ Back", callback_data="onboarding_1"),
                    InlineKeyboardButton(text="Next ➡️", callback_data="onboarding_3")
                ]
            ]
        )
    else:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="⬅️ Back", callback_data="onboarding_2"),
                    InlineKeyboardButton(text="✅ Finish Tour", callback_data="onboarding_finish")
                ]
            ]
        )


def build_susy_group_welcome_keyboard() -> InlineKeyboardMarkup:
    """
    Group welcome notice inline keyboard (Admin):
    [ 🌸 Meet Susy ]  [ 🌐 Community ]
    [ 🌐 Explore Ecosystem ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🌸 Meet Susy", url="https://t.me/iamsusiebot?start=welcome"),
                InlineKeyboardButton(text="🌐 Community", callback_data="susy_community_links"),
            ],
            [
                InlineKeyboardButton(text="🌐 Explore Ecosystem", callback_data="susy_menu_directory"),
            ]
        ]
    )


def build_susy_member_welcome_keyboard() -> InlineKeyboardMarkup:
    """
    Group welcome notice inline keyboard (Regular Member):
    [ ⚡ Promote Susy to Admin ]
    [ 🌸 Meet Susy ]  [ 🌐 Community ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⚡ Promote Susy to Admin", callback_data="susy_prompt_admin"),
            ],
            [
                InlineKeyboardButton(text="🌸 Meet Susy", url="https://t.me/iamsusiebot?start=welcome"),
                InlineKeyboardButton(text="🌐 Community", callback_data="susy_community_links"),
            ]
        ]
    )


def build_susy_farewell_keyboard() -> InlineKeyboardMarkup:
    """
    Compact inline keyboard attached to Susy's farewell messages.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🌐 Explore Ecosystem", callback_data="susy_menu_directory"),
                InlineKeyboardButton(text="➕ Re-invite Susy", url="https://t.me/iamsusiebot?startgroup=true"),
            ]
        ]
    )
