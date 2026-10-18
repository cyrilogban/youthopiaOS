from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from shared.utils.ui import GLOBAL_REPLY_BUTTONS, get_open_app_inline_button
from shared.config.bot_registry import get_bot_identity, DEFAULT_MINI_APP_LINK

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
    Row 1 (Global):        [ ðŸ‘¤ My Profile ]      [ Open App ] [ â„¹ï¸ Help ]  [ ðŸŒ Community ]
    Row 2 (Bot Specific): [ ðŸ” Search Scripture ]  [ ðŸ”– Saved Verses ]
    Row 3 (Settings):      [ ðŸŒ Translation ]
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            GLOBAL_REPLY_BUTTONS,
            [
                KeyboardButton(text="ðŸ” Search Scripture"),
                KeyboardButton(text="ðŸ”– Saved Verses"),
            ],
            [
                KeyboardButton(text="ðŸŒ Translation"),
            ]
        ],
        resize_keyboard=True,
        persistent=True,
        input_field_placeholder="Choose a Theodore action..."
    )


def build_theo_welcome_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Theo /start Welcome Card inline keyboard:
    [ Open App ]
    [ ðŸ” Search ]  [ ðŸŒ Translation ]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                get_open_app_inline_button(),
            ],
            [
                InlineKeyboardButton(text="ðŸ” Search", callback_data="theo_search_scripture"),
                InlineKeyboardButton(text="ðŸŒ Translation", callback_data="theo_translation_menu"),
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
                InlineKeyboardButton(text="Open App", url=DEFAULT_MINI_APP_LINK),
            ],
            [
                InlineKeyboardButton(text="ðŸ” Search", callback_data="theo_search_scripture"),
                InlineKeyboardButton(text="ðŸŒ Translation", callback_data="theo_translation_menu"),
            ],
            [
                InlineKeyboardButton(text="ðŸ§­ Start Community Tour", url=get_bot_identity("theo").get_start_link("tour")),
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
                InlineKeyboardButton(text="Open App", url=DEFAULT_MINI_APP_LINK),
            ],
            [
                InlineKeyboardButton(text="âš¡ Promote Theodore to Admin", callback_data="theo_prompt_admin"),
            ],
            [
                InlineKeyboardButton(text="ðŸ” Search", callback_data="theo_search_scripture"),
                InlineKeyboardButton(text="ðŸŒ Translation", callback_data="theo_translation_menu"),
            ],
            [
                InlineKeyboardButton(text="ðŸ§­ Start Community Tour", url=get_bot_identity("theo").get_start_link("tour")),
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
                InlineKeyboardButton(text="ðŸ§­ Community Tour", url=get_bot_identity("theo").get_start_link("tour")),
                InlineKeyboardButton(text="âž• Re-invite Theodore", url="https://t.me/theobiblebot?startgroup=true"),
            ],
        ]
    )


def build_verse_actions_keyboard(
    category: str,
    reference: str,
    is_group: bool = False,
    bot_username: str = "theobiblebot",
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
    bot_username: str = "theobiblebot"
) -> InlineKeyboardMarkup:
    """Builds the interactive translation drawer keyboard for verse cards:
    Row 1: [ â— KJV ] [ ASV ] [ WEB ] [ BBE ]
    Row 2: [ â—€ Back ] [ Save ]
    """
    clean_ref = reference.replace(" ", "_")
    available_trans = ["kjv", "asv", "web", "bbe"]
    trans_buttons = []

    for t in available_trans:
        label = f"â— {t.upper()}" if t.lower() == active_trans.lower() else t.upper()
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
                    text="â—€ Back",
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
