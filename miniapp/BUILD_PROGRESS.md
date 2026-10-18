# YouThopiaOS Mini App — Build Progress & Engineering Journal

> **Living document.** Updated after each build phase so the entire team has a crystal-clear understanding of every design decision, architectural shift, turning point, and technical breakthrough.
> **Scope:** `miniapp/` only — the React TypeScript Telegram Mini App, its design system, screens, and its interaction with the gateway.
> **Standalone bot progress lives in `bots/BUILD_PROGRESS.md`.**
> **Last updated:** 2026-10-18

---

## 1. Executive Summary & Vision

The **YouThopiaOS Mini App** is a unified, visual Telegram Mini App running inside Telegram's native webview for the **YOUTHOPIA BIBLE COMMUNITY**.

- **App Title:** `YOUTHOPIA BIBLE COMMUNITY`
- **Slogan:** `Sharing God's Love All The Way`
- **Core Architecture:** 3-Tier Decoupled Architecture (`React Mini App` ↔ `FastAPI Gateway` ↔ `Supabase Postgres DB`).
- **The 5 Assisting Telegram Bots (identity per `shared/config/bot_registry.py`):**
  1. **Theodore / Theo (`@theobiblebot`)**: Daily Verses (VOTD), Scripture Search & Multi-Translation (KJV, ASV, WEB, BBE).
  2. **Lucy / Lusie (`@lusiequizbot`)**: Bible Trivia, 4 Quiz Modes, XP Progression & Global Leaderboard.
  3. **Peter / Pete (`@petemodbot`)**: Community Shield, Captcha Guard, Trust Score (100/100) & Member Verification.
  4. **Edmund / Edie (`@ediecalendarbot`)**: Community Schedule, Weekly Gatherings, Birthdays & Calendar RSVP.
  5. **Susan / Susie (`@susiehelpsbot`)**: Community Hostess, Newcomer Tour, Topic Directory & FAQs.

---

## 2. Technical Architecture & Data Flow

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│ TELEGRAM ECOSYSTEM (Mobile / Desktop)                                             │
│                                                                                   │
│  [ @theobiblebot ]  [ @lusiequizbot ]  [ @petemodbot ]  [ @ediecalendarbot ]  [ @susiehelpsbot ] │
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

### Module 8: The 5-Bot Command Menu & Launch Architecture (Bot-Side — see bots/BUILD_PROGRESS.md) ✅
- Record of this bot-side milestone lives in `bots/BUILD_PROGRESS.md`. Mini App takeaway: members always enter through inline `[ Open App ]` cards and BotFather menu buttons that transmit 100% authenticated `initData`.

---

### Module 9: Group Chat Traction & Scripture Detection Resilience (Bot-Side — see bots/BUILD_PROGRESS.md) ✅
- Record of this bot-side milestone lives in `bots/BUILD_PROGRESS.md`.

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

### Module 11: Modern UI Overhaul & Rank Integration (Foundation Refresh) ✅
- **Complete Overhaul:** Rebuilt all 5 tabs with modern cards, hover lift, live Supabase data, and skeletons; fixed strict TypeScript definitions (`88abd0f`).
- **Rank Integration:** Added the reusable `RankBadge` component; `/profile` and `/api/leaderboard` now return `rank_title`, `rank_tier`, `rank_badge_color`, and `rank_emoji` resolved from the 4-tier / 9-rank hierarchy (YouTopian Seeker → Ambassador) — rendered in the profile sheet, leaderboard, and growth surfaces.
- **Community Stats Era:** Briefly shipped a live community stats endpoint consumer, an impact banner (`8a7bbd8`) and a glass capsule marquee ticker (`9fb7222`, later emoji-free at `abee800`). Superseded by the redesign; `/api/community/stats` remains live for a future surface.
- **Identity Alignment:** All references migrated to `shared/config/bot_registry.py` — formal names (Theodore, Lucy, Edmund, Peter, Susan), short names (Theo, Lusie, Edie, Pete, Susie), and canonical handles.

---

### Module 12: The Living Devotional Redesign ✅
- **Brief:** Executed the `MINIAPP_UI_REDESIGN_HANDOFF.md` product brief — evolve from "five bot dashboards in one shell" into **one calm, devotional-first community product**.
- **Member-Centered Navigation:** The bottom dock now reads **Today / Word / Play / Gather / More**, with the `TabId` structure retained (no routing rewrite).
- **Today:** Page-level greeting, large editorial Verse-of-the-Day card ("Read in Word" action), growth card (XP, rank badge, progress bar, "Play today's challenge"), and next-moment feature rows.
- **Word:** Immersive serif Scripture with a segmented translation control (KJV/ASV/WEB/BBE), synced live to gateway settings; saved verses/reading plans slots reserved for the future.
- **Play:** Featured daily challenge, four game modes framed as playable destinations with XP reward pills and `t.me` deep links, leaderboard demoted to secondary Top-5 context.
- **Gather:** Calendar-first — next gathering hero card with Edie RSVP deep link, remaining events below, event/birthday management via Edie.
- **More:** Rebuilt as the community handbook — profile & preferences pointers, Peter security summary, the 5-assistant directory with registry names/handles, 3-step quick start aligned to the new destinations, FAQ accordion, and community group links. No magenta page-block, no emojis.
- **Brand Alignment:** Shell header now carries the kicker `YOUTHOPIA BIBLE COMMUNITY` and tagline `Sharing God's Love All The Way`.
- **Retirements:** `CommunityTicker.tsx` removed (orphaned consumer of community stats).
- **Design Tokens:** Warm off-white canvas, deep purple anchor (`#5f2cab`), editorial cards, quiet chips, feature rows, standardized skeletons and pill system — one dominant platform palette per the brief's color-usage rules.

---

### Module 13: Resilient Launch & Error Boundary ✅
- **The Symptom:** The production build showed a blank white screen when opened in a plain browser (no Telegram environment, no dev mock).
- **Root Cause:** Synchronous throws from `@telegram-apps/sdk` calls (`init()`, `initData` access, `viewport.expand.isAvailable()`) inside React effects unmount the entire React tree.
- **The Fix (`miniapp/src/services/telegram.ts`):**
  1. Every SDK boot call is individually wrapped in `try...catch`; launch context simply stays unavailable outside Telegram.
  2. All `initData`/user reads have the official `window.Telegram.WebApp` bridge as first fallback (reply-keyboard webviews included).
- **Error Boundary:** Added `miniapp/src/components/ErrorBoundary.tsx` (wired in `main.tsx`) so any future crash renders a recoverable "Reload" card instead of a blank page.
- **Verification:** `npx tsc --noEmit` and `npm run build` pass with 0 errors; production preview renders correctly outside Telegram.

---

### Module 14: The Unified YouThopia Tour (In-App) ✅
- **Brief:** Bring the shared community tour (module designed with the 5 bots — bot-side record in `bots/BUILD_PROGRESS.md`) into the app: the same 5 pages, the same copy, the same one-time +50 YP orientation award.
- **Gateway Touchpoints (`gateway/app/main.py`):**
  1. `GET /api/community/tour` — serves the structured 5-page tour copy sourced from `shared/content/tour.py` + `BOT_REGISTRY` (public read, no auth), so app and bots can never drift.
  2. `POST /api/community/tour/complete` — marks the caller oriented and awards the one-time +50 YP / +50 Trust boost using the **same `orientation_completed` action and `onboarding_xp_{user_id}` idempotency key the bots use** — completing in the app first and a bot later (or vice versa) resolves to `already_completed`; the boost can only ever be claimed once per member across the whole ecosystem.
- **More Tab Entry (`CommunityTab.tsx`):** "Start here — The YouThopia Tour" card at the top of the handbook screen with a full-width primary "🧭 Take the tour" button.
- **Tour Overlay (`TourOverlay.tsx`):** New full-screen bottom sheet — page dots + Back/Next paging, blocks/bullets/bot-roster/community-space renderers mirroring the bot pages, and a finish screen (awarded +50 YP / confirmed-already-complete / boost-pending-next-visit).
- **First-Launch Auto-Open (`App.tsx`):** Verified members who have not yet finished orientation see the tour once per device (`youthopia_tour_seen_v1` localStorage flag); users already `onboarded` are never prompted, and both the dismiss and finish paths mark it seen.
- **Profile Refresh:** `useTelegram` now exposes `refreshProfile()`; finishing the tour immediately refreshes XP/rank in the header and passport.

---

## 4. Current Status & Verification Matrix

| Feature / Subsystem | Status | Verification Summary |
|---|---|---|
| **FastAPI Gateway Auth** | ✅ Verified | Strict HMAC-SHA256 multi-bot signature verification + anti-replay check, with graceful fallback to prevent profile 401 lockouts. |
| **Supabase Profile Sync** | ✅ Verified | Live XP, level, quiz accuracy, and display-name sync on every profile fetch. |
| **Rank & Profile Integration** | ✅ Verified | 4-tier / 9-rank fields rendered via `RankBadge` across profile, leaderboard, and growth surfaces. |
| **Living Devotional UI** | ✅ Verified | Today / Word / Play / Gather / More navigation, editorial VOTD card, More handbook screen. |
| **Resilient Launch** | ✅ Verified | Defensive SDK boot + error boundary; production preview renders outside Telegram. |
| **YouThopia Tour (In-App)** | ✅ Verified | `GET /api/community/tour` + `POST /api/community/tour/complete` live on Render; tour endpoint returns 5 pages / 5 bots / 3 spaces; suite 29/29; TS + Vite build 0 errors. |
| **Production Build** | ✅ Verified | TypeScript 0 errors, Vite bundle compiled, live on Render. |

---

## 5. Next Steps for Community Launch

1. **Real-Device Telegram Test (post-deploy):** Launch the app from a bot's Open App button and confirm the verified profile loads (not "Preview mode") — validates real `initData`, safe-area insets, and viewport expansion inside the webview.
2. **AOTD (Affirmation of the Day):** Deferred by design — build only after an actual backend content model and endpoint exist.
3. **Future Stats Surface:** `/api/community/stats` is live but currently has no frontend consumer; fold a compact stats strip into Today or More when desired.
4. **Scripture Library (Word):** Saved verses gallery, reading-plan progress, and shareable VOTD graphics remain reserved future slots.
5. **BotFather Menu Buttons:** (Bot-side task, tracked in `bots/BUILD_PROGRESS.md`) Set `/setmenubutton` for all 5 bots to `https://youthopiaos.onrender.com`.
