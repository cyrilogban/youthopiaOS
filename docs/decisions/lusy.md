# Lusy: Decisions & Technical Documentation

This document records architectural decisions, data schemas, and internal procedures for managing the Lusy Games Engine.

---

## 1. The Supabase Game Engine vs Python Code
**Decision:** The game logic stays in Python. The game content stays in Supabase.
**Reason:** This prevents hardcoding thousands of strings into the bot code and allows the database to instantly scale to 100,000 questions without the bot requiring a restart or redeployment.

## 2. Seed Files & Security
**Decision:** All `seed_*.py` files are strictly ignored by Git via `.gitignore`.
**Reason:** Because the seed files contain the literal answers to every quiz question in the database, pushing them to a public GitHub repository would allow players to cheat and artificially farm YouTopian Points (YP). 

## 3. How to Seed New Quiz Questions
To add bulk questions to the database locally, use the `bots/lusy/utils/seed_questions.py` script.

Inside the script is a `SAMPLE_QUESTIONS` array. You can paste 50+ questions into this array using the exact JSON template below:

```python
{
    "game_type": "multiple_choice",   # Always "multiple_choice" for now
    "category": "Old Testament",      # Grouping tag (e.g., "Prophets", "Jesus")
    "difficulty": "medium",           # MUST BE: "easy", "medium", "hard", or "expert"
    "content": {
        "text": "Which prophet was swallowed by a great fish?",
        "options": ["Elijah", "Elisha", "Jonah", "Isaiah"] # Exactly 4 options
    },
    "correct_answer": "Jonah",        # Must perfectly match one of the 4 options above
    "explanation": "Jonah 1:17",      # (Optional) Shown after user guesses
    "base_xp": 15,                    # Easy=10, Medium=15, Hard=20
    "is_active": True
}
```

### Understanding Difficulty Routing
When a user clicks `[ Medium (15 YP) ]` in Telegram, Lusy executes `services.supabase.find_many()`, passing a filter for `"difficulty": "medium"`. Supabase returns only the medium questions, and Lusy randomly selects one to send as a Telegram Native Poll. 

Because of this routing, you must strictly name the difficulty as `"easy"`, `"medium"`, or `"hard"` inside your JSON dictionary so it properly maps to the button clicked.

To inject the questions into the live database, run:
`python bots/lusy/utils/seed_questions.py`

## 4. YouTopian Points (YP) & Level Progression System
**Core Architecture:**
1. **`users` Table (Authoritative state):**
   * Stores `total_xp` (total YP) and the user's current `level`.
2. **`xp_transactions` Table (Audit log):**
   * Every time a user receives YP, a new row is appended here capturing the `amount`, `bot_name` (e.g., `"lusy"`), and the `source` action details (e.g., `"Bible Quiz: b2c95fb8-..."`).
3. **`user_levels` Table (Lookup cache):**
   * Caches `total_xp` and `level` keyed by `user_id` with an upsert constraint, allowing fast leaderboard queries.

**Level Progression Formula:**
Level progression is linear and managed centrally by the XP engine:
$$\text{Level} = \max\left(1, \frac{\max(0, \text{total\_xp})}{100} + 1\right)$$
Every 100 YP scales the user up by 1 Level (e.g., 0-99 YP is Level 1, 100-199 YP is Level 2, etc.). When a user answers a poll correctly, the bot fetches their profile, computes the new YP and level, and updates all three tables concurrently.

## 5. Competitive Group Quiz & Concurrency Management
**Decision:** Group quizzes are structured as a competitive race with strict synchronization locks and winner announcements.

**Key Mechanics:**
1. **Concurrency Lock (`ACTIVE_GROUP_QUIZZES`):**
   * The bot maps `group_chat_id` to the current `poll_id`. 
   * If a user attempts to start a new quiz while a quiz is already active in that group chat, the command is blocked to prevent chat spam and poll overlap.
2. **Dynamic Participant Scoring:**
   * Unlike private chats where state is tracked in the database, group quizzes store participant votes in-memory.
   * This allows multiple users to answer the same poll simultaneously without overwriting each other's state.
3. **Poll Expiration & Closure (`stop_poll`):**
   * The active quiz is closed when **5 participants** have answered or when a **5-minute timeout** fallback is reached.
   * On expiration, the bot stops the poll (making it gray/unclickable), logs all participants to history, distributes YP rewards to winners in Supabase, and publishes a single winner summary message (`🏆 Quiz Completed!`) with medals.
   * The lock is then released, permitting the next quiz to start.

## 6. Interactive Dashboard & Leaderboard Commands
**Decision:** The main menu and leaderboard commands are designed to be accessible and interactive across private DMs and group chats.

**Key Design Elements:**
1. **DM Welcome Dashboard (Reply Keyboard):**
   * The bot utilizes a persistent `ReplyKeyboardMarkup` grid at the bottom of the screen (`🎮 Play Games`, `Leaderboard`, `My YP & Stats`, `About Lusy`). 
   * This provides consistent, quick-access bottom menu navigation that remains visible and clickable throughout the user's DM session.
2. **Global Leaderboard Handler (`/leaderboard`):**
   * The `/leaderboard` command is exposed in both private DMs and group chats.
   * When queried, it searches the `users` database table. It applies a `.gt("total_xp", 0)` filter to automatically screen out inactive players, bot/service user entries (e.g. `@iamtheobot`), and mock accounts with 0 YP.
   * Results are sorted descending and formatted with visual place-indicators (🥇, 🥈, 🥉, etc.).

## 7. Ignored Test Assets
**Decision:** All scratch execution scripts (matching `*_scratch.py` and `check_users_scratch.py`) are strictly blacklisted from Git.
**Reason:** This prevents developers from accidentally committing database query scripts, credential exposure files, or temporary local diagnostics tools into public version control.

## 8. Self-Destructing Group Instructions
**Decision:** When a group quiz starts, the bot pushes a brief instructions/rules sheet directly below the poll, which automatically deletes (self-destructs) after **20 seconds**.
**Reason:** Keeps the group history completely clean, uncluttered, and readable, while providing immediate guidance to new players. Bots can delete their own messages in groups without needing administrative permissions.

## 9. Gamified Stats Display (Profile Cards)
**Decision:** The stats display command (`/yp` or `My YP & Stats` button) generates a structured profile card.
**Key Components:**
* **Title Tier:** Automatically assigns tiers based on level (e.g. `Novice` for Level 1, `Scripture Sage` for Levels 2-4, `Wisdom Warrior` for Levels 5-9, etc.).
* **XP Progress Bar:** Renders a 10-block visual progress indicator (`[████░░░░░░]`) calculated via `total_xp % 100`.
* **Accuracy Metrics:** Queries `lusy_game_history` to calculate and print the user's career success rate (Accuracy %) and total quizzes played.

## 10. Clean-Slate Bulk Seeding (150 Questions)
**Decision:** The database seed script (`seed_questions.py`) was expanded to house a bank of **150 Bible trivia questions** (50 Easy, 50 Medium, 50 Hard) and redesigned to clear previous questions before performing chunked bulk insertions.
**Reason:** Exterminates duplicate or corrupt test questions from previous builds and avoids network/payload timeouts when interacting with Supabase.

## 11. Dual-Layout Welcome Interface (Emoji-Free)
**Decision:** The DM `/start` greeting displays both a floating `InlineKeyboardMarkup` grid and initializes a persistent `ReplyKeyboardMarkup` menu at the bottom of the screen.
* **Text Adjustment:** The play button text was changed from `🎮 Play Games` to `Start Bible Quiz`.
* **Visual Styling:** Emojis were completely stripped from all welcome buttons across both keyboards to achieve a cleaner, less cluttered user interface.
* **Routing:** Message listeners were updated to handle raw text matches for `Start Bible Quiz` alongside legacy commands.

## 12. Cross-Bot Currency Alignment & Live Presence Timestamps
**Decision:** Standardized the community points nomenclature across the entire codebase and fixed presence tracking.
* **Unified YP Currency:** Replaced all leftover references to the legacy `XP` naming convention with the new `YP` (YouTopian Points) moniker inside `@iamtheobot`, `@iampetebot`, `@iamsusiebot`, and `@iamedyybot`.
* **presence tracking (`last_seen_at`):** Patched the identity resolver (`user_service.py`) to update the `last_seen_at` column in `telegram_accounts` to the current UTC time during identity resolution. This ensures the user's "Last Seen" profile field updates dynamically to "Today" rather than remaining frozen at their initial registration date.

## 13. Future Architecture: Unified Control Center & Web Portal
**Proposal:** Designate **Susy** (`@iamsusiebot`) as the user-facing "Control Center" bot, serving as a unified portal that aggregates profile statistics, calendar RSVPs, daily verse subscriptions, and moderation records.
**Implementation Pillars:**
1. **Centralized Bot Dashboard (Susy):**
   * Susy's profile command will pull data across all five bots: YP Balance (Lusy), Trust Score (Pete), Verse Subscription Status (Theo), and active Event RSVPs (Eddy).
2. **Telegram Web App Integration (TWA Web Portal):**
   * Add a `🌐 Open Web Portal` inline button to Susy's dashboard.
   * This button will load a responsive, secure web application (e.g., built with Next.js/React and hosted on Vercel) directly inside Telegram's built-in WebApp iframe.
   * **Web Features:** High-fidelity animations, visual level progress gauges, career quiz analytics (success rates over time), and calendar-view event RSVP checkers.
3. **Unified Database Authority:**
   * Leverage the existing Supabase centralized architecture to keep the bots and Web Portal synced in real-time.
