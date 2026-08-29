from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from shared.utils.ui import GLOBAL_REPLY_BUTTONS, get_open_app_inline_button

class VerseAction(CallbackData, prefix="verse", sep="|"):
    action: str  # "save" or "next"
    category: str
    reference: str

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


def build_verse_actions_keyboard(category: str, reference: str) -> InlineKeyboardMarkup:
    """Builds the inline action keyboard for verse cards: [ 💜 Save ] [ Next Verse ] [ Share ]."""
    clean_ref = reference.replace(" ", "_")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💜 Save",
                    callback_data=VerseAction(
                        action="save", 
                        category=category, 
                        reference=clean_ref
                    ).pack()
                ),
                InlineKeyboardButton(
                    text="Next Verse",
                    callback_data=VerseAction(
                        action="next", 
                        category=category, 
                        reference=clean_ref
                    ).pack()
                ),
                InlineKeyboardButton(
                    text="Share",
                    switch_inline_query=reference
                ),
            ]
        ]
    )
