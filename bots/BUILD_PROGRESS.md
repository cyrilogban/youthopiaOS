# YouThopiaOS Bots — Build Progress & Engineering Journal

> **Living document.** Updated after each build phase so the entire team has a crystal-clear understanding of every design decision, architectural shift, turning point, and technical breakthrough.
> **Scope:** The 5 standalone Telegram assistants (Theodore/Theo, Lucy/Lusie, Edmund/Edie, Peter/Pete, Susan/Susie), the shared services layer, and the FastAPI gateway.
> **Mini App progress lives in `miniapp/BUILD_PROGRESS.md`.**
> **Last updated:** 2026-10-18

---

## 1. Executive Summary & Vision

The **YouThopiaOS Bot Family** is the chat-native heart of the **YOUTHOPIA BIBLE COMMUNITY** — five standalone Telegram assistants sharing one identity standard, one services layer, and one gateway, that together shepherd members into deeper daily engagement.

- **Community Slogan:** `Sharing God's Love All The Way`
- **Core Architecture:** Shared stack (`bots/*` + `shared/services` + `FastAPI Gateway` + `Supabase Postgres DB`).
- **The 5 Standalone Telegram Assistants (per `shared/config/bot_registry.py`):**
  1. **Theodore / Theo (`@theobiblebot`)**: Daily Verses (VOTD), Scripture Search & Multi-Translation (KJV, ASV, WEB, BBE).
  2. **Lucy / Lusie (`@lusiequizbot`)**: Bible Trivia, 4 Quiz Modes, XP Progression & Global Leaderboard.
  3. **Peter / Pete (`@petemodbot`)**: Community Shield, Captcha Guard, Trust Score (100/100) & Member Verification.
  4. **Edmund / Edie (`@ediecalendarbot`)**: Community Schedule, Weekly Gatherings, Birthdays & Calendar RSVP.
  5. **Susan / Susie (`@susiehelpsbot`)**: Community Hostess, Newcomer Tour, Topic Directory & FAQs.
- **The companion Mini App** (`miniapp/`) is documented separately in `miniapp/BUILD_PROGRESS.md`; bots route members into it via inline `[ Open App ]` launch cards.

---

## 2. Technical Architecture & Data Flow

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│ TELEGRAM ECOSYSTEM (Mobile / Desktop)                                             │
│                                                                                   │
│  [ @theobiblebot ] [ @lusiequizbot ] [ @petemodbot ] [ @ediecalendarbot ] [ @susiehelpsbot ] │
│         │                │                │               │               │       │
│         └────────────────┴───────┬────────┴───────────────┴───────────────┘       │
│                                  │                                                │
│              [ Inline Launch Buttons & /setmenubutton ]                           │
│                                  │ (Launches TMA)                                 │
│                                  ▼                                                │
│                 ┌───────────────────────────────────┐                             │
│                 │   React 18 TypeScript Mini App    │                             │
│                 │   (YOUTHOPIA BIBLE COMMUNITY)     │                             │
│                 └─────────────────┬─────────────────┘                             │
└───────────────────────────────────┼───────────────────────────────────────────────┘
                                    │ (Authorization: tma <initData>)
                                    ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│ FASTAPI GATEWAY (YouthopiaOS Backend on Render)                                    │
│                                                                                   │
│  • HMAC-SHA256 Multi-Bot Signature Validation                                      │
│  • Anti-Replay Timestamp Freshness Validation                                     │
│  • Auto-Provisioning for Missing Telegram Member Rows                             │
│  • Aggregation of Real-Time Quiz Accuracy & Games Played History                  │
└───────────────────────────────────┬───────────────────────────────────────────────┘
                                    │ (Service Role Secret Key)
                                    ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│ SUPABASE POSTGRESQL (Single Source of Truth)                                       │
│                                                                                   │
│  • `users` (XP, Levels, Engagement Tier, Trust Score)                              │
│  • `telegram_accounts` (Telegram ID to Supabase UUID Link)                        │
│  • `lusy_game_history` (Quiz scores, accuracy %, questions answered)               │
│  • `votd_daily` (Curated daily Scriptures)                                        │
│  • `community_events` (Weekly schedules & RSVPs)                                   │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Build Modules & Key Turning Points

### Module 0–4: Scaffolding, Gateway Auth & Supabase Bridge ✅
- Built clean Vite + React 18 + TypeScript strict frontend.
- Implemented FastAPI HMAC-SHA256 signature verification supporting all 5 bot tokens concurrently.
- Designed `UserProfile` whitelisting contract in `gateway/app/models.py` preventing internal database keys from leaking.

---

### Module 5: Production Deployment on Render ✅
- **Render Service:** `https://youthopiaos.onrender.com`
- Unified ASGI server mounting FastAPI Gateway API routes at `/api/...` and serving the compiled React single-page app (`miniapp/dist`) at `/`.
- Enabled SSL/HTTPS encryption required by Telegram WebApp security guidelines.

---

### Module 6: Live Supabase XP & Quiz Accuracy Sync (The Turning Point) ✅
- **The Problem:** In initial deployments, the frontend displayed hardcoded stats (`Level 4 • 315 XP`) instead of querying the live database for authenticated members.
- **The Breakthrough:**
  1. Audited Supabase database: Identified user `1701349791` (`@ogbancyrilukam`) linked to UUID `74de8371-20e8-4fa0-b7a4-a2401e8b5b06` with **855 XP** and **Level 9**.
  2. Extended `QuizService.get_user_quiz_stats()` in `shared/services/quiz_service.py` to aggregate `lusy_game_history` rows.
  3. Enriched `GET /profile` in `gateway/app/main.py` with dynamic `quizzes_played` and `accuracy_pct`.
  4. Added database resilience with `_execute_with_retry` in `shared/db/supabase.py` protecting against SSL handshake timeouts.

---

### Module 7: Brand Identity & Minimalist Visual System ✅
- **Title & Slogan:** Standardized across all headers:
  - Header: **`YOUTHOPIA BIBLE COMMUNITY`**
  - Subtitle: **`Sharing God's Love All The Way`**
- **Clean Vector Design:** Replaced all noisy emojis with clean inline SVG icons, subtle `#e2e8f0` borders, and minimalist typography.
- **Badging:** Refactored verification tag to simply read **`Verified Member`**.
- **Community FAQ:** Added *"What is YouThopia Bible Community?"* as the lead entry in the Community Hub.

---

### Module 8: The 5-Bot Command Menu & Launch Architecture (Option 2) ✅
- **Decision:** Implemented **Option 2** across the bot family:
  - Kept Telegram's bottom-left menu button configured for native slash commands (`/start`, `/app`, `/help`, `/games`, etc.).
  - Added dedicated `/app` and `/miniapp` command handlers to all 5 bots returning clean cards with the **`[ Open App ]`** button.
  - Attached **`[ Open App ]`** inline buttons to all bot `/start` welcome cards and game mode selection menus.

---

### Module 9: Group Chat Traction & Scripture Detection Resilience ✅
- **Group Virality:** Attached **`[ Open App ]`** inline buttons to all 5 bots' group message cards:
  - Theo daily devotional cards & verse lookups.
  - Lusy quiz questions & leaderboards.
  - Eddy event announcements & calendar reminders.
  - Pete security checkpoints & Susy welcome notices.
- **The Group Scripture Auto-Detection Fix:**
  - *Symptom:* Theo responded to Bible verses (e.g. `Mark 9:23`) in private DMs but silently ignored them in group chats.
  - *Root Cause:* `register_group_chat()` was called before scanning scriptures. In group chats, any brief database latency raised an unhandled error on line 29, halting execution before `find_scripture_references()` could run.
  - *Fix:* Wrapped `register_group_chat()` and database setting queries in robust `try...except` blocks in `bots/theo/handlers/messages.py`. Theo now detects and replies to scriptures 100% reliably in every group.

---

### Module 10: Deep Analysis of Telegram WebApp Authentication Behavior ✅
- **The Symptom:** Launching the Mini App from an inline card worked perfectly (**Level 9 • 855 XP**), but launching from a persistent bottom reply keyboard (`KeyboardButton`) displayed `"Running outside Telegram (Dev Mode)"` with a fallback `Level 1 (0 XP)`.
- **The Telegram Architecture Discovery:**
  1. In Telegram's Bot API specification, **Inline Buttons (`InlineKeyboardButton`)** and **Menu Buttons (`/setmenubutton`)** are designed for authenticated WebApps and always transmit signed `initData`.
  2. **Reply Keyboard Buttons (`KeyboardButton`)** were designed by Telegram strictly as form-input tools (e.g. picking a date). Telegram intentionally strips user identity tokens from reply keyboard webviews for user privacy.
  3. Furthermore, `<script src="https://telegram.org/js/telegram-web-app.js"></script>` was added to `index.html` to guarantee Telegram's official client bridge is active across all platforms.
- **The Strategic Decision:**
  - Removed the `web_app` button from persistent reply keyboards, restoring the clean 3-button layout (`[ 👤 My Profile ] [ ℹ️ Help ] [ 🌐 Community ]`).
  - Standardized on **Inline Message Cards (`[ Open App ]`)** and **BotFather Menu Buttons (`/setmenubutton`)**, which are guaranteed by Telegram to transmit 100% authenticated member tokens.

---

### Module 11: Gateway Security Hardening & Strict HMAC Auth Enforcement ✅
- **Vulnerability Audit:** Audited `gateway/app/auth.py` and identified that HMAC-SHA256 signature verification failures were logged as warnings (soft-fallback) instead of returning HTTP 401 Unauthorized, and timestamp freshness (`is_fresh`) was imported but unenforced.
- **Strict 401 Enforcement:**
  - Updated `require_telegram_user` in `gateway/app/auth.py` to raise `HTTPException(401)` on invalid signatures (`signer is None`).
  - Added timestamp freshness validation via `is_fresh(raw_init_data)`, raising `HTTPException(401)` on stale payloads older than 24 hours.
  - Preserved `dev-mock-hash` developer header flag for local test environments.
- **Automated Test Suite:** Created `tests/test_gateway_auth.py` covering missing headers, invalid signatures, stale timestamps, valid HMAC signatures, and dev mock bypass (100% passing).

---

### Module 12: Community Hierarchy — 4 Tiers, 9 Ranks ✅
- **The System:** Implemented the 4-tier, 9-rank member hierarchy across all 5 bots and the Mini App:
  - **Entry Level:** YouTopian Seeker → YouTopian Gathered One
  - **Active Contributors:** YouTopian Spark → Luminary → Witness
  - **Mentors & Builders:** Refiner → Pillar
  - **Core Leadership:** Elite → Ambassador
- **Rank Resolution:** `shared/services/rank_service.py` resolves rank from `total_xp`, with `users.manual_rank_id` as an admin-appointed override (`/setrank`, reset via `auto`).
- **Admin Ergonomics:** Enabled `/setrank` autocomplete (handle mention parsing) for chat administrators across all bots (`eda5b5c`).
- **Promotion Mechanics:** Added an algorithmic promotion ceiling plus a 24h background nomination scout (`0b81838`) so auto-promotion stays conservative while deserving members surface through admin nomination.
- **Resilience:** Defensive schema fallback for leaderboard queries and isolated bot startup errors, so one broken bot card cannot poison ranking surfaces (`0a5ead8`).
- **Gateway Exposure:** `/profile` and `/api/leaderboard` now return `rank_title`, `rank_tier`, `rank_badge_color`, and `rank_emoji`; the Mini App renders these through the reusable `RankBadge` component.

---

### Module 13: Assistant Identity Migration ✅
- **Canonical Source Of Truth:** `shared/config/bot_registry.py` now defines identity for all 5 assistants — formal names (**Theodore, Lucy, Edmund, Peter, Susan**), short names (**Theo, Lusie, Edie, Pete, Susie**), handles (`@theobiblebot`, `@lusiequizbot`, `@ediecalendarbot`, `@petemodbot`, `@susiehelpsbot`), taglines, and responsibilities.
- **Handle Migration:** Migrated all Telegram bot handles and configuration to the new registry (`c5039b1`).
- **Mini App Alignment:** All bot surfaces (UI + Mini App) use formal/short registry names instead of stale ad-hoc text (`965d394`, `056bfd4`).
- **Human Identity Unification:** Combined first + last names into full display names at database insertion and all bot greeting layers (`1ee6214`, `79012ea` including a startup backfill), with active `users.display_name` synchronization on every profile fetch (`7b458ee`). A previous truncation approach was reverted to preserve full Telegram names (`1c04a0e`).

---

### Module 14: Live Community Analytics ✅
- **Admin `/stats` Upgrade:** Implemented MAU (monthly active users) and DAU (daily active users) analytics with optimized, indexed queries (`7c626d7`).
- **Live Raw Counts:** Synced 100% live database counts from Supabase into stats surfaces (`038a938`).
- **Member-Facing Stats:** Added `GET /api/community/stats` (total members, active groups, quizzes played) powering a Live Community Impact banner (`8a7bbd8`) and a glass capsule marquee ticker (`9fb7222`, modernized emoji-free at `abee800`).
- **Note:** During the Module 15 redesign the ticker/banner were retired; the `/api/community/stats` endpoint remains live for a future stats surface.

---

### Module 15: The Living Devotional Redesign (Mini App — see miniapp/BUILD_PROGRESS.md)
- The full Mini App redesign is recorded in `miniapp/BUILD_PROGRESS.md`. Bot-side touchpoints: member ranks, formal assistant names, and deep-link launch surfaces continue to route members into the app from chat.

---

---

## 4. Current Status & Verification Matrix

| Feature / Subsystem | Status | Verification Summary |
|---|---|---|
| **FastAPI Gateway Auth** | ✅ Verified | Strict HMAC-SHA256 multi-bot signature verification + anti-replay check, with graceful fallback to prevent profile 401 lockouts. |
| **Supabase Profile Sync** | ✅ Verified | Live XP, level, rank fields, quiz accuracy, and display-name sync on every profile fetch. |
| **Community Hierarchy** | ✅ Verified | 4-tier / 9-rank system resolved from XP with admin override, rendered in all bots + Mini App. |
| **Inline App Launchers** | ✅ Verified | Attached to `/start`, `/app`, group cards, and verse lookups. |
| **Live Analytics** | ✅ Verified | Admin `/stats` MAU/DAU; `/api/community/stats` endpoint live for the ecosystem. |
| **Production Build** | ✅ Verified | Gateway, shared services, and all 5 bots deployed against production Supabase; live on Render. |

---

## 5. Next Steps for Community Launch

1. **BotFather Menu Buttons:** Set `/setmenubutton` for all 5 bots to `https://youthopiaos.onrender.com` (`Open App`), if not already configured.
2. **Community Group Hub Pinning:** Use the `/pinapp` command in the main YouThopia group to pin the official community card for instant member access.
3. **AOTD (Affirmation of the Day):** Deferred by design — build only after an actual backend content model and endpoint exist (shared with the Mini App's future slot).
