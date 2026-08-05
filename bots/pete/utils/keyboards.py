from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_pete_start_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Pete DM /start Card Inline Keyboard per YouThopiaOS UI Spec:
    [ 👤 My Profile ]  [ ℹ️ Help ]  [ 🌐 Community Links ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 My Profile", callback_data="pete_profile"),
                InlineKeyboardButton(text="ℹ️ Help", callback_data="pete_help"),
                InlineKeyboardButton(text="🌐 Community Links", callback_data="pete_community_links"),
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
