from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from shared.utils.ui import FACEBOOK_LINK, TELEGRAM_GROUP_LINK, WHATSAPP_LINK


def build_susy_start_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Susy DM /start Welcome Card Inline Keyboard per YouThopiaOS UI Spec:
    [ Join Facebook ]    [ Join Telegram ]
    [ Join WhatsApp ]    [ Join Threads  ]
    [     🌸 Explore the Community     ]
    [ 👤 My Profile ]  [ ℹ️ Help ]
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
            ],
            [
                InlineKeyboardButton(text="🌸 Explore the Community", callback_data="onboarding_1")
            ],
            [
                InlineKeyboardButton(text="👤 My Profile", callback_data="susy_profile"),
                InlineKeyboardButton(text="ℹ️ Help", callback_data="susy_help"),
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
                    InlineKeyboardButton(text="Next ➡️", callback_data="onboarding_3"),
                ]
            ]
        )
    else:  # Page 3
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="⬅️ Back", callback_data="onboarding_2"),
                    InlineKeyboardButton(text="✅ Finish Exploring", callback_data="onboarding_finish"),
                ]
            ]
        )


def build_topic_directory_keyboard() -> InlineKeyboardMarkup:
    """
    Topic Directory (/where) Inline Keyboard:
    [ 💬 Open YouThopia Group ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Open YouThopia Group", url=TELEGRAM_GROUP_LINK)]
        ]
    )


def build_susy_group_welcome_keyboard() -> InlineKeyboardMarkup:
    """
    Group Welcome Card Inline Keyboard:
    [ 🌸 Meet Susy in DM ]  [ 🗑️ Close ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌸 Meet Susy in DM", url="https://t.me/iamsusiebot")],
            [InlineKeyboardButton(text="🗑️ Close", callback_data="susy_close_msg")]
        ]
    )
