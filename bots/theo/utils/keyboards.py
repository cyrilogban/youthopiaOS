from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class VerseAction(CallbackData, prefix="verse", sep="|"):
    action: str  # "save" or "next"
    category: str
    reference: str

class SavedVersesPage(CallbackData, prefix="sv_page"):
    page: int


def build_verse_actions_keyboard(category: str, reference: str) -> InlineKeyboardMarkup:
    """Builds the 3-button keyboard for verse interaction (Save, Next, Share)."""
    
    # We clean the reference string to avoid callback_data size limits
    # and to ensure it maps correctly to the DB logic.
    clean_ref = reference.replace(" ", "_")
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Save",
                callback_data=VerseAction(
                    action="save", 
                    category=category, 
                    reference=clean_ref
                ).pack()
            ),
            InlineKeyboardButton(
                text="Next",
                callback_data=VerseAction(
                    action="next", 
                    category=category, 
                    reference=clean_ref
                ).pack()
            ),
            InlineKeyboardButton(
                text="Share",
                switch_inline_query=reference
            )
        ]
    ])
