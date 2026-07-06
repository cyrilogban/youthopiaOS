# High King Peter (Pete) - Technical & Design Decisions

This document records the major architectural, security, and design decisions made while building Pete, the security and moderation bot for the YouThopiaOS framework.

*This file is restricted to local development and is explicitly ignored by Git to prevent internal moderation rules from leaking publicly.*

---

## 1. The Hub Merger (Phase 1)
**Decision:** Integrate Pete into the unified YouThopiaOS `BotManager` instead of running him as an isolated application.
**Reasoning:** 
- Allows Pete to directly read and write to the global `SupabaseGateway` without duplicating database connection logic.
- Let's Pete seamlessly interact with the global `users` table and adjust the `trust_score` metric, meaning his punishments actively alter how other bots (like Theo or Lusy) view the user.
- Shares the `IsAdminFilter` and `register_group_chat` middleware for efficient database writes.

## 2. The Justice Commands & Trust Economy
**Decision:** Hardcode specific `trust_delta` penalties to administrative slash commands.
**Reasoning:** 
- Standardizing penalties ensures justice is blind and consistent, regardless of which admin issues the command.
- `/warn` = -10 Points
- `/mute` = -20 Points
- `/kick` = -30 Points
- `/ban`  = -50 Points
- The `ModerationService` abstracts this logic and writes an immutable record into the `moderation_actions` table so admins can always audit why a user's trust score dropped.

## 3. The Word Banishment Filter (Regex Bounds)
**Decision:** Upgraded the legacy profanity substring check to use Regular Expression Word Boundaries (`\b`).
**Reasoning:** 
- The legacy Pete bot used naive substring matching. Because `"a"` was accidentally in the `FORBIDDEN_WORDS` list, the bot risked banning users for typing any word with an 'a'.
- Even without typos, substring matching causes the "Scunthorpe Problem" (e.g., banning "passion" because it contains "ass").
- By using `re.compile(r'\b(?:' + '|'.join(...) + r')\b')`, Pete efficiently scans every message for exact profanity matches in milliseconds without false positives.

## 4. The Spam & Invite Link Detector
**Decision:** Hardcode the filter to block specific rival chat domains (`t.me`, `telegram.me`, `chat.whatsapp.com`) but implement an **Admin Bypass Exception**.
**Reasoning:** 
- Banning all URLs is too aggressive for a Bible Community (users need to share YouTube sermons, YouVersion Bible links, Google Docs). We exclusively target known chat-stealing domains.
- Admins often need to share official YouThopia WhatsApp or Telegram links. Before punishing a user, Pete makes an API call to `message.chat.get_member(message.from_user.id)` to verify their rank. Admins bypass the penalty.

## 5. The Flood Engine Memory Architecture
**Decision:** Track user message timestamps in local volatile memory (`collections.defaultdict`) instead of the Supabase database.
**Reasoning:** 
- Writing every single message timestamp to a remote Postgres database (Supabase) just to check if they sent 5 messages in 4 seconds would throttle the API and cause massive latency.
- Storing a rolling window of timestamps in RAM is ultra-fast, auto-cleans itself (we only keep timestamps `< 4` seconds old), and is completely ephemeral.

## 6. Perimeter Defense: The Deep Link Gateway (Anti-Bot Captcha)
**Decision:** Instead of dropping the Captcha UI button directly into the main group chat, force the user to click a Deep Link (`t.me/PeteBot?start=verify_chatid`) that moves the verification process into Pete's private DMs.
**Reasoning:** 
- Telegram does not allow bots to DM a user first. The Deep Link forces the user to manually trigger the DM conversation by pressing "Start".
- Moving the Captcha button into the DM prevents the main group chat from becoming cluttered with "Prove you are human" messages every time a new member joins.
- Pete utilizes an in-memory `PENDING_CAPTCHAS` dictionary to remember the `message_id` of the original Deep Link message in the main group. Once the user clicks the Captcha in the DM, Pete deletes the original group message to leave zero trace of the bot defense system.

## 7. Mute Duration Parsing
**Decision:** Allow admins to specify flexible time durations (`/mute 1h`, `/mute 30m`, `/mute 7d`) by utilizing Regex parsing and `datetime.timedelta`.
**Reasoning:**
- Not every offense deserves an indefinite mute.
- Aiogram's `restrict` method naturally accepts an `until_date` argument. By calculating the future timestamp locally in Python, Pete can instruct Telegram's servers to automatically lift the mute when the time expires, eliminating the need for cron jobs or database background workers.

## 8. The Escalating Threshold (5-Warning Ban)
**Decision:** Execute automated punishments (Mute on 3 warnings, Ban on 5 warnings) directly after the database returns the user's warning count.
**Reasoning:**
- Instead of just warning users infinitely, Pete calculates the user's warning count via `get_user_warnings_count` instantly after every infraction.
- If the count reaches 3, Pete triggers `await message.chat.restrict(...)`. If it reaches 5, Pete escalates immediately to `await message.chat.ban(...)` and permanently removes the bad actor.

## 9. Repetitive Copy-Paste Memory
**Decision:** Store the actual lower-case string content of users' messages in a rolling 60-second RAM buffer (`USER_MESSAGE_CONTENT`).
**Reasoning:**
- Spam bots don't always fire off 5 messages in 4 seconds (which triggers the Flood Engine). Sometimes they slowly paste the exact same text every 10 seconds.
- By keeping a lightweight 60-second history of what users are typing, Pete can mathematically compare the strings. If `same_text_count >= 3`, Pete instantly deletes the message and penalizes them for spam.
- Just like the Flood Engine, this is entirely stored in volatile memory (`defaultdict`) to avoid thrashing the Postgres database with every single chat message.
