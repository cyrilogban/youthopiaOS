# Theo - Verse of the Day (VOTD) Progress Log

*Date: June 12, 2026*

Today, we successfully built and integrated the automated Verse of the Day (VOTD) delivery pipeline for Theo. Here is a comprehensive breakdown of the features, architecture, and logic implemented:

## 1. Database Architecture & Storage
- **Schema Creation**: Created a new Supabase migration (`003_verse_of_the_day.sql`) to define the `verse_of_the_day` table.
- **Reference-Only Storage**: Adhered to the requirement of not hardcoding bible text. The database purely serves as a "calendar of truth", storing only the `scheduled_date` and the `reference` (e.g., "John 14:27").
- **Schema Refinements**: Removed the `reflection` column entirely from both the code and the database, ensuring clean and minimal storage.

## 2. Curated Content Seeding
- **Seed Script**: Built `bots/theo/utils/seed_votd.py`.
- **Curated Selection**: Hand-picked exactly 100 New Testament, Christ-centered verses.
- **Thematic Balance**: The 100 verses were evenly split across five core themes: Peace (20), Faith (20), Love (20), Joy (20), and Patience (20).
- **Execution**: Successfully ran the script and populated the Supabase `verse_of_the_day` table for the next 100 days.

## 3. Dynamic API Integration
- **VOTD Service**: Developed `bots/theo/services/devotional_service.py` to bridge Supabase and external APIs.
- **Bible-API Connection**: Added logic to dynamically fetch the actual verse text from `bible-api.com` based on the user's or group's preferred translation (e.g., KJV, NIV).
- **Stability**: Added a 10-second `aiohttp` timeout to prevent the bot from hanging if the user's internet connection or the API servers become unstable.

## 4. Delivery & Broadcast Pipeline
- **Delivery Service**: Created `bots/theo/services/delivery_service.py` to handle the heavy lifting of messaging.
- **Multi-Target Broadcasting**: Designed the pipeline to pull all active subscriptions for both Group Chats (`chat_subscriptions`) and Private DMs (`user_subscriptions`).
- **Translation Caching**: Implemented a caching mechanism so that if 50 groups all want the KJV translation, the bot only queries `bible-api.com` once, preventing rate limits.
- **Formatting**: Implemented clean, emoji-free markdown formatting for the delivered verses.

## 5. User & Admin Subscription Control
- **Menu Overhaul**: Removed the "Subscribe" button from the ReplyKeyboardMarkup (grid menu) to clean up the interface.
- **Sidebar Integration**: Added `/subscribe` and `/unsubscribe` commands to `THEO_COMMANDS` in `bots/theo/bot.py`.
- **Admin Security**: Added strict permissions in `bots/theo/router.py`. If the commands are used in a group chat, Theo verifies that the sender is an Administrator or Creator before toggling the subscription.
- **Database Resolution**: Handled missing `user_subscriptions` table by providing the raw SQL to update the Supabase schema cache.
- **Duplicate Checks**: Added intelligent checks before updating subscriptions. If a user or group is already subscribed, the bot will notify them instead of repeating the action.

## 6. UI & Text Refinements
- **Personalized Responses**: Updated subscription text to dynamically inject the Telegram group's name (e.g., `✅ **Youth Ministry Team** is now subscribed...`).
- **Schedule Transparency**: Included the expected delivery time natively in the subscription confirmation (`...You will receive it daily at 6:00 AM in the morning.`).
- **Telegram Scope Resolution**: Implemented a startup script to programmatically wipe ghost menus from `BotCommandScopeAllPrivateChats`, `BotCommandScopeAllGroupChats`, and `BotCommandScopeAllChatAdministrators` so all users fall back to the clean Default menu set by BotFather.

## 7. Automated Scheduling & Production Readiness
- **APScheduler**: Integrated `APScheduler` into the `aiogram` startup hooks.
- **Daily Cron Job**: Configured an invisible background timer to wake up and trigger `DeliveryService.broadcast_votd()` exactly at **6:00 AM** (`Africa/Lagos` timezone) every single day.
- **Code Cleanup**: Removed all temporary `/broadcast_votd` and `/nuke_menu` testing commands from the codebase to ensure a secure, production-ready state.

---

*Date: June 13, 2026*

Today we added real-time, in-chat Bible reference detection, sophisticated translation management, and deployment fail-safes.

## 8. Real-Time Bible Reference Detection
- **Regex Parser Engine**: Built `bots/theo/utils/bible_ref_parser.py` using a highly robust regex to detect references in conversational text.
- **Book Alias Support**: Added comprehensive alias arrays (e.g., "1 Samuel", "1 Sam", "1sam", "i samuel") mapping to all 66 canonical books.
- **Range & Context Parsing**: Engineered the detection to seamlessly pick up verse ranges (`John 3:16-18`) and ignore arbitrary digits or paths. Case-insensitive and punctuation-tolerant.

## 9. Translation Resolution & User Preferences
- **DM Preference Storage**: Extended the `/translation` command to support Private DMs. Preferences are now saved in the existing `bot_user_state` table.
- **Group Setting Bug Fix**: Patched a critical bug in `core/telegram_runtime.py` where `register_chat` was unconditionally overwriting group settings with the default `KJV` on every message.
- **API Synchronization**: Removed `NIV` and `NKJV` (which are unsupported by `bible-api.com` due to copyright) and replaced them with fully open `WEB` and `BBE` options.
- **Silent Context Resolution**: Updated the message handler to silently map a detected text reference to the correct translation using `chat_bot_settings` (for groups) or `bot_user_state` (for DMs) before fetching.

## 10. Advanced Verse Output Formatting
- **Multi-Verse Line Numbering**: Refactored `fetch_bible_text()` in the devotional service to parse the API's JSON `verses` array. Multi-verse requests now print elegantly with numbered lines (e.g., `[1] And the third day...`).
- **Expandable Blockquotes**: Integrated Telegram's HTML `<blockquote expandable>` for long text ranges. Single verses use a standard `<blockquote>` for a professional vertical accent line, while long ranges collapse nicely with a native "Tap to expand" interface.
- **Error Handling**: Implemented graceful error replies (`"John 99:99 is not a valid Bible reference."`) when the API throws a 404, instead of failing silently.

## 11. Production & Render Deployment Fixes
- **Keep-Alive Worker Server**: Added `keep_alive.py` utilizing FastAPI and Uvicorn. This spins up a background thread web server to bind to Render's `$PORT`, bypassing the "No open ports detected" deployment failure for background worker bots incorrectly deployed as Web Services.
- **Multi-Bot Safety**: Confirmed that `core/bot_manager.py` elegantly ignores bots with missing `.env` tokens, allowing THEO to be deployed solo without crashing due to other incomplete bot scripts (Lusy, Pete, Eddy, Susy).

---

*Date: June 21, 2026*

Today we implemented the personalized user onboarding experience for Theo using the unified YouThopiaOS Supabase architecture.

## 12. Smart Personalization & Onboarding
- **Unified Identity Resolution**: Replaced the standalone database queries in the `/start` handler with the centralized `services.identity.resolve_telegram_user()` and `UserService`.
- **System-wide Engagement Tracking**: Leveraged the `engagement_level` field in the unified `users` table (which correctly defaults to `'new'`) to distinguish brand new YouTopians from returning members.
- **Dynamic Welcome Texts**: 
  - **New Users**: Receive the "Grand Welcome" containing community vision, culture, and immediate feature descriptions, wrapped in HTML `<blockquote>`.
  - **Old Users**: Receive a short, familiar "Welcome back" to prevent spamming veterans with onboarding text.
- **State Mutation Function**: Added `set_engagement_level()` to `shared/services/user_service.py` to seamlessly flip a user's status from `'new'` to `'active'` immediately after their first interaction, ensuring they are treated as active members ecosystem-wide.

## 13. Verse Interaction UI (3-Button Architecture)
- **Aiogram 3 Factory Integration**: Created `bots/theo/utils/keyboards.py` implementing Aiogram's `CallbackData` factory (`VerseAction`). This replaces fragile string-splitting logic with strongly typed, object-oriented callback data routing.
- **Dynamic Inline Keyboards**: Updated the message handler in `bots/theo/handlers/messages.py` to automatically append an inline keyboard with [Save], [Next], and [Share] buttons beneath the formatted blockquotes.
- **Unified Data Persistence**: 
  - Drafted `004_user_saved_verses.sql` to map saved verses strictly to the global `users.id` (UUID) rather than Telegram IDs, allowing cross-bot interoperability.
  - Implemented `UserService.save_verse()` to securely upsert verses without bots touching the DB.

## 14. Premium Saved Verses UI & Pagination
- **Aiogram Separator Bug Fix**: Resolved a critical crash caused by Aiogram's default `:` separator conflicting with Bible references (e.g., `John 3:16`). Configured `VerseAction(sep="|")` to ensure safe data packing.
- **Asyncio Gathering**: Upgraded the Saved Verses display engine in `router.py` to fetch multiple verses concurrently using `asyncio.gather()`, completely eliminating the slow, synchronous API loop from the legacy bot.
- **Robust Pagination**: Engineered a `SavedVersesPage` callback factory. The UI now limits output to 3 verses per page, preventing Telegram's 4096-character limit crashes, complete with dynamic inline `[⬅️ Prev]` and `[Next ➡️]` navigation buttons.
- **Premium HTML Journal Layout**: Styled the output using a beautiful mix of bold tags and blockquotes. Verses over 150 characters automatically utilize Telegram's `<blockquote expandable>` to keep the chat interface clean and compact.
- **Grid Menu Integration**: Added the `My Saved Verses` button directly into the main `ReplyKeyboardMarkup` alongside Profile and Translation settings.

## 15. Curated "Next" Verse Discovery
- **Seed Selection**: Refactored `handle_next_verse()` to abandon completely random Bible chapter selection (which often yielded irrelevant lineage verses) in favor of the 100 hand-picked `CURATED_REFERENCES` located in `seed_votd.py`.
- **Collision Prevention**: Engineered logic to prevent the "Next" button from ever landing on the exact same verse the user is currently viewing.
- **Translation Integrity**: Ensures that the newly fetched verse instantly respects the user's preferred translation (KJV, WEB, etc.) stored globally in Supabase.
- **In-Place Message Editing**: Seamlessly updates the chat bubble via `callback.message.edit_text()`, ensuring a snappy, app-like experience without clogging the user's chat history.
