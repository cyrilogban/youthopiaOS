from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from shared.utils.ui import GLOBAL_REPLY_BUTTONS, get_open_app_inline_button

class VerseAction(CallbackData, prefix="verse", sep="|"):
    action: str  # "save", "compare_menu", "switch_trans", "back"
    category: str
    reference: str
    trans: str = "kjv"

class SavedVersesPage(CallbackData, prefix="sv_page"):
    page: int


def build_theo_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Theo persistent reply keyboard:
    Row 1 (Global):        [ 👤 My Profile ]      [ Open App ] [ ℹ️ Help ]  [ 🌐 Community ]
    Row 2 (Bot Specific): [ 🔍 Search Scripture ]  [ 🔖 Saved Verses ]
    Row 3 (Settings):      [ 🌐 Translation ]
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            GLOBAL_REPLY_BUTTONS,
            [
                KeyboardButton(text="🔍 Search Scripture"),
                KeyboardButton(text="🔖 Saved Verses"),
            ],
            [
                KeyboardButton(text="🌐 Translation"),
            ]
        ],
        resize_keyboard=True,
        persistent=True,
        input_field_placeholder="Choose a Theo action..."
    )


def build_theo_welcome_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Theo /start Welcome Card inline keyboard:
    [ Open App ]
    [ 🔍 Search ]  [ 🌐 Translation ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                get_open_app_inline_button(),
            ],
            [
                InlineKeyboardButton(text="🔍 Search", callback_data="theo_search_scripture"),
                InlineKeyboardButton(text="🌐 Translation", callback_data="theo_translation_menu"),
            ]
        ]
    )


def build_theo_group_welcome_keyboard() -> InlineKeyboardMarkup:
    """
    Inline keyboard attached to Theo's group welcome card (Admin).
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Open App", url="https://t.me/iamtheobot/app"),
            ],
            [
                InlineKeyboardButton(text="🔍 Search", callback_data="theo_search_scripture"),
                InlineKeyboardButton(text="🌐 Translation", callback_data="theo_translation_menu"),
            ],
            [
                InlineKeyboardButton(text="🌐 Explore Ecosystem", callback_data="theo_community_links"),
            ],
        ]
    )


def build_theo_member_welcome_keyboard() -> InlineKeyboardMarkup:
    """
    Inline keyboard attached to Theo's group welcome card (Regular Member).
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Open App", url="https://t.me/iamtheobot/app"),
            ],
            [
                InlineKeyboardButton(text="⚡ Promote Theo to Admin", callback_data="theo_prompt_admin"),
            ],
            [
                InlineKeyboardButton(text="🔍 Search", callback_data="theo_search_scripture"),
                InlineKeyboardButton(text="🌐 Translation", callback_data="theo_translation_menu"),
            ],
        ]
    )


def build_theo_farewell_keyboard() -> InlineKeyboardMarkup:
    """
    Compact inline keyboard attached to Theo's farewell messages.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🌐 Explore Ecosystem", callback_data="theo_community_links"),
                InlineKeyboardButton(text="➕ Re-invite Theo", url="https://t.me/iamtheobot?startgroup=true"),
            ],
        ]
    )


def build_verse_actions_keyboard(
    category: str,
    reference: str,
    is_group: bool = False,
    bot_username: str = "iamtheobot",
    trans: str = "kjv"
) -> InlineKeyboardMarkup:
    """Builds the mobile-optimized inline action keyboard for verse cards:
    Row 1: [ Save ] [ Compare ]
    Row 2: [ Share ]
    """
    clean_ref = reference.replace(" ", "_")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Save",
                    callback_data=VerseAction(
                        action="save", 
                        category=category, 
                        reference=clean_ref,
                        trans=trans
                    ).pack()
                ),
                InlineKeyboardButton(
                    text="Compare",
                    callback_data=VerseAction(
                        action="compare_menu", 
                        category=category, 
                        reference=clean_ref,
                        trans=trans
                    ).pack()
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Share",
                    switch_inline_query=reference
                ),
            ]
        ]
    )


def build_verse_compare_drawer(
    category: str,
    reference: str,
    active_trans: str = "kjv",
    is_group: bool = False,
    bot_username: str = "iamtheobot"
) -> InlineKeyboardMarkup:
    """Builds the interactive translation drawer keyboard for verse cards:
    Row 1: [ ● KJV ] [ ASV ] [ WEB ] [ BBE ]
    Row 2: [ ◀ Back ] [ Save ]
    """
    clean_ref = reference.replace(" ", "_")
    available_trans = ["kjv", "asv", "web", "bbe"]
    trans_buttons = []

    for t in available_trans:
        label = f"● {t.upper()}" if t.lower() == active_trans.lower() else t.upper()
        trans_buttons.append(
            InlineKeyboardButton(
                text=label,
                callback_data=VerseAction(
                    action="switch_trans",
                    category=category,
                    reference=clean_ref,
                    trans=t
                ).pack()
            )
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            trans_buttons,
            [
                InlineKeyboardButton(
                    text="◀ Back",
                    callback_data=VerseAction(
                        action="back",
                        category=category,
                        reference=clean_ref,
                        trans=active_trans
                    ).pack()
                ),
                InlineKeyboardButton(
                    text="Save",
                    callback_data=VerseAction(
                        action="save",
                        category=category,
                        reference=clean_ref,
                        trans=active_trans
                    ).pack()
                ),
            ]
        ]
    )
