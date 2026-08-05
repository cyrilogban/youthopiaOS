from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from shared.utils.ui import GLOBAL_REPLY_BUTTONS

class VerseAction(CallbackData, prefix="verse", sep="|"):
    action: str  # "save" or "next"
    category: str
    reference: str

class SavedVersesPage(CallbackData, prefix="sv_page"):
    page: int


def build_theo_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Theo persistent reply keyboard:
    Row 1 (Bot Specific): [ 🔍 Search Scripture ]  [ 🔖 Saved Verses ]
    Row 2 (Global):        [ 👤 My Profile ]      [ ℹ️ Help ]           [ 🌐 Community Links ]
    Row 3 (Settings):      [ 🌐 Translation ]
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔍 Search Scripture"),
                KeyboardButton(text="🔖 Saved Verses"),
            ],
            GLOBAL_REPLY_BUTTONS,
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
    [ 🔍 Search Scripture ]  [ 🌐 Translation ]
    [ 👤 My Profile       ]  [ 🌐 Community Links ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔍 Search Scripture", callback_data="theo_search_scripture"),
                InlineKeyboardButton(text="🌐 Translation", callback_data="theo_translation_menu"),
            ],
            [
                InlineKeyboardButton(text="👤 My Profile", callback_data="theo_profile"),
                InlineKeyboardButton(text="🌐 Community Links", callback_data="theo_community_links"),
            ]
        ]
    )


def build_verse_actions_keyboard(category: str, reference: str) -> InlineKeyboardMarkup:
    """Builds the inline action keyboard for verse cards: [ 💜 Save ] [ 🔄 Next Verse ]."""
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
                    text="🔄 Next Verse",
                    callback_data=VerseAction(
                        action="next", 
                        category=category, 
                        reference=clean_ref
                    ).pack()
                ),
            ]
        ]
    )
