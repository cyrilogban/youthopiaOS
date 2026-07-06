# Theo Bot — Feature Roadmap

> Private development tracker for Theo's devotional & identity features.
> Part of Phase 4 in the main YouThopiaOS roadmap.

---

## Current Status

### ✅ Completed
- [x] Theo bot starts, polls Telegram, auto-registers groups to Supabase
- [x] `/start` command — shared, registers group + greeting
- [x] `/profile` command — shared, resolves identity, shows level/XP/trust
- [x] `/translation` command — saves Bible translation preference (kjv, asv, niv, nkjv) to `chat_bot_settings`
- [x] `/subscribe` command — saves `daily_devotional` subscription to `chat_subscriptions`
- [x] Supabase schema supports chats, memberships, settings, subscriptions
- [x] Shared services fully wired (ChatService, UserService, XPService, IdentityResolver)
- [x] Foundation tests pass (`test_unified_foundation.py`)

---

## Feature 1: DevotionalService + `/read` Command
> **Priority: 🔴 Critical — Everything else depends on this**
> **Files:** `bots/theo/services/devotional_service.py`, `bots/theo/router.py`

The core content pipeline. Without this, Theo has no devotional content to serve.

- [ ] Research and select a Bible API (e.g., API.Bible, bible-api.com, or similar)
- [ ] Implement `DevotionalService` class in `bots/theo/services/devotional_service.py`
  - [ ] `fetch_verse(reference, translation)` — fetch a specific verse/passage by reference
  - [ ] `get_daily_reading()` — determine today's reading (e.g., from a reading plan or curated list)
  - [ ] `generate_devotional(reading, translation)` — compose a devotional object (verse text + reflection prompt)
  - [ ] Handle API errors gracefully (timeouts, rate limits, fallback content)
- [ ] Wire `/read` command in `router.py` to actually call `DevotionalService`
  - [ ] Fetch the group's preferred translation from `chat_bot_settings`
  - [ ] Call `DevotionalService.get_daily_reading()` + `fetch_verse()`
  - [ ] Format and send the result (basic formatting first, full Formatter later)
- [ ] Support reading by reference: `/read John 3:16` (optional, stretch)

**Depends on:** Nothing — this is the foundation  
**Unlocks:** Formatter, DeliveryService, Scheduler, `/unsubscribe`

---

## Feature 2: Formatter — Beautiful Devotional Messages
> **Priority: 🟡 High — Makes Theo's output professional**
> **Files:** `bots/theo/utils/formatter.py`

Transforms raw devotional data into beautifully formatted Telegram messages.

- [ ] Implement `format_devotional(devotional)` — main formatting function
  - [ ] Verse card layout with book name, chapter, verse numbers
  - [ ] Translation label (e.g., "KJV" badge)
  - [ ] Reflection/prayer prompt section
  - [ ] Date header for daily readings
- [ ] Implement `format_verse(verse_text, reference, translation)` — standalone verse formatting
- [ ] Implement `format_reading_plan_progress(current, total)` — progress indicator
- [ ] Use Telegram's MarkdownV2 or HTML parse mode for rich formatting
- [ ] Handle long passages gracefully (split into multiple messages if needed)

**Depends on:** Feature 1 (DevotionalService)  
**Unlocks:** Better UX for `/read`, DeliveryService messages

---

## Feature 3: DeliveryService + Scheduler — Automated Daily Devotionals
> **Priority: 🟡 High — The signature Theo experience**
> **Files:** `bots/theo/services/delivery_service.py`, `core/scheduler.py`

Push daily devotionals to all subscribed groups automatically.

- [ ] Implement `core/scheduler.py` — APScheduler integration
  - [ ] Initialize AsyncIOScheduler with job store
  - [ ] `add_daily_job(func, hour, minute, timezone)` — schedule a daily task
  - [ ] `start()` / `stop()` lifecycle methods
  - [ ] Wire into BotManager startup
- [ ] Implement `DeliveryService` in `bots/theo/services/delivery_service.py`
  - [ ] `deliver_daily_devotional()` — the scheduled job function
    - [ ] Query `chat_subscriptions` for all enabled `daily_devotional` subscriptions
    - [ ] For each subscribed group: get translation preference, fetch devotional, format, send
    - [ ] Handle per-group errors (bot kicked, chat deleted, API failure) without blocking others
    - [ ] Log delivery results to analytics/telemetry
  - [ ] `deliver_to_chat(chat_id, devotional)` — send a formatted devotional to one chat
- [ ] Register the daily job in BotManager or Theo's `run_bot()`
- [ ] Support timezone-aware scheduling (groups can set their timezone)

**Depends on:** Feature 1 (DevotionalService), Feature 2 (Formatter)  
**Unlocks:** The full "subscribe and receive" flow

---

## Feature 4: Command Handlers — Refactor + New Commands
> **Priority: 🟢 Medium — Code quality + feature completeness**
> **Files:** `bots/theo/handlers/commands.py`, `bots/theo/handlers/messages.py`, `bots/theo/router.py`

Refactor existing inline commands into proper handler files and add missing commands.

- [ ] Move `/translation`, `/subscribe`, `/read` logic from `router.py` into `handlers/commands.py`
- [ ] Keep `router.py` as a thin wiring layer (register handlers, inject dependencies)
- [ ] Implement `/unsubscribe` command — disable `daily_devotional` subscription for a group
- [ ] Implement `/plan` command — show/set the group's reading plan (stretch)
- [ ] Implement `/verse <reference>` command — fetch a specific verse on demand (stretch)
- [ ] Add basic message handling in `handlers/messages.py`
  - [ ] Auto-respond to Scripture references mentioned in chat (stretch)
  - [ ] Track engagement for XP purposes

**Depends on:** Feature 1 (DevotionalService)  
**Unlocks:** Better code organization, `/unsubscribe` flow

---

## Feature 5: Unit Tests for Theo
> **Priority: 🟢 Medium — Quality assurance**
> **Files:** `tests/test_theo.py`

Write comprehensive tests for all Theo-specific logic.

- [ ] Test `/translation` command — valid translations, invalid input, DM rejection
- [ ] Test `/subscribe` command — group subscription creation, idempotency
- [ ] Test `/read` command — successful fetch, API failure handling, missing translation fallback
- [ ] Test `DevotionalService` — verse fetching, daily reading selection, error handling
- [ ] Test `DeliveryService` — multi-group delivery, error isolation, skipping kicked bots
- [ ] Test `Formatter` — output formatting, long passage splitting, edge cases
- [ ] Use `FakeSupabaseGateway` pattern from `test_unified_foundation.py`
- [ ] Mock Bible API responses for deterministic tests

**Depends on:** Features 1-4 (test what's built)  
**Unlocks:** Confidence for deployment

---

## Feature 6: Identity + Subscription Integration
> **Priority: 🔵 Low — Polish & completeness**
> **Files:** Various shared services + Theo handlers

Ensure Theo fully leverages the shared identity system and chat subscriptions.

- [ ] Verify identity resolution works end-to-end in Theo context
- [ ] Track per-user reading history (may need new DB table: `reading_history`)
- [ ] Award XP for reading devotionals (`xp_service.award_xp()`)
- [ ] Show reading streaks in `/profile` (extend profile handler)
- [ ] Personalized devotional recommendations based on reading history (stretch)

**Depends on:** Features 1-3  
**Unlocks:** Gamification, engagement tracking, cross-bot synergy with Lusy

---

## Build Order (Recommended)

```
Feature 1: DevotionalService + /read  ←── START HERE
    ↓
Feature 2: Formatter
    ↓
Feature 3: DeliveryService + Scheduler
    ↓
Feature 4: Command Refactor + /unsubscribe
    ↓
Feature 5: Unit Tests
    ↓
Feature 6: Identity Integration
```

---

## Open Questions

1. **Which Bible API?** — API.Bible (free, many translations), bible-api.com (simple, limited), or self-hosted?
2. **Reading plan source?** — Curated list, community-submitted, or algorithmic (e.g., chronological Bible)?
3. **Devotional content** — Verse only, or verse + AI-generated reflection/prayer prompt?
4. **Delivery time** — Single global time (e.g., 6 AM UTC) or per-group configurable?
5. **Message format** — Telegram HTML or MarkdownV2? HTML is more reliable for complex layouts.
