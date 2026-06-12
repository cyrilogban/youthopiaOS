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
- **Sidebar Integration**: Added `/subscribe` and `/unsubscribe` commands to `THEO_COMMANDS` in `bots/theo/bot.py` so they natively appear in Telegram's sidebar menu.
- **Admin Security**: Added strict permissions in `bots/theo/router.py`. If the commands are used in a group chat, Theo verifies that the sender is an Administrator or Creator before toggling the subscription.
- **Database Resolution**: Handled missing `user_subscriptions` table by providing the raw SQL to update the Supabase schema cache.

## 6. Automated Scheduling
- **APScheduler**: Integrated `APScheduler` into the `aiogram` startup hooks.
- **Daily Cron Job**: Configured an invisible background timer to wake up and trigger `DeliveryService.broadcast_votd()` exactly at **6:00 AM** (`Africa/Lagos` timezone) every single day.
- **Manual Testing**: Added a hidden `/broadcast_votd` command so admins can manually trigger the broadcast and receive a success/failure summary report without waiting for the morning schedule.
