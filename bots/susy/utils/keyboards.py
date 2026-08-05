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
    [ Join Facebook ]    [ Join Telegram ]
    [ Join WhatsApp ]    [ Join Threads  ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Join Facebook", url=FACEBOOK_LINK),
                InlineKeyboardButton(text="Join Telegram", url=TELEGRAM_GROUP_LINK),
            ],
            [
                InlineKeyboardButton(text="Join WhatsApp", url=WHATSAPP_LINK),
                InlineKeyboardButton(text="Join Threads", callback_data="global_ignore"),
            ]
        ]
    )


def build_onboarding_tour_keyboard(page: int) -> InlineKeyboardMarkup:
    """
    Interactive Onboarding Tour inline keyboards:
    Page 1: [ Next ➡️ ]
    Page 2: [ ⬅️ Back ]  [ Next ➡️ ]
    Page 3: [ ⬅️ Back ]  [ ✅ Finish Exploring ]
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
                    InlineKeyboardButton(text="✅ Finish Exploring", callback_data="onboarding_finish")
                ]
            ]
        )


def build_topic_directory_keyboard() -> InlineKeyboardMarkup:
    """
    Susy /where Topic Directory inline keyboard:
    [ 💬 Open YouThopia Group ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Open YouThopia Group", url=TELEGRAM_GROUP_LINK)]
        ]
    )


def build_susy_group_welcome_keyboard() -> InlineKeyboardMarkup:
    """
    Group welcome notice inline keyboard:
    [ 🌸 Meet Susy in DM ]
    [ 🗑️ Close ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🌸 Meet Susy in DM", url="https://t.me/iamsusiebot")
            ],
            [
                InlineKeyboardButton(text="🗑️ Close", callback_data="susy_close_msg")
            ]
        ]
    )
