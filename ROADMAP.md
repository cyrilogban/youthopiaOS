# YouThopiaOS Roadmap

## Phase 1: Lock Architecture And Schema [COMPLETED]
- [x] Keep `DECISIONS.md` as the private ignored decision log.
- [x] Define Supabase schema before writing feature logic.
- [x] Create SQL/table design for core tables (users, telegram_chats, etc.).
- [x] Establish MongoDB as telemetry-only.

## Phase 2: Build Shared Foundation [COMPLETED]
- [x] Implement `shared/db/supabase.py` as authoritative DB layer.
- [x] Implement `shared/db/mongo.py` as telemetry layer.
- [x] Implement core configuration (`core/config.py`).
- [x] Implement identity resolution (`core/identity.py`).
- [x] Implement permissions (`core/permissions.py`).
- [x] Implement shared services (user, xp, event, moderation, analytics, chat).

## Phase 3: Build One Runtime [COMPLETED]
- [x] Make `main.py` purely a `BotManager` runner.
- [x] Implement `BotManager` to load config, init DBs, and manage dispatchers.
- [x] Create generic `telegram_runtime.py` with `/start`, `/profile`, and group tracking.
- [x] Verify polling starts cleanly and skips bots without tokens.

## Phase 4: Bring Theo Online (Devotionals & Identity) [IN PROGRESS]
- [x] Validate basic Telegram connection & group tracking to Supabase.
- [ ] Migrate Theo's devotional scheduling logic to `bots/theo/`.
- [ ] Implement specific commands for Theo (e.g., set translation, read today).
- [ ] Connect Theo to shared identity and chat subscriptions.
- [ ] Add unit tests for Theo handlers.

## Phase 5: Bring Lusy Online (Gamification & XP) [TODO]
- [ ] Implement Lusy's core router in `bots/lusy/`.
- [ ] Build quiz/game logic using the `xp_service`.
- [ ] Create leaderboards querying Supabase `user_levels` and `xp_transactions`.
- [ ] Add unit tests for Lusy handlers and XP logic.

## Phase 6: Bring Pete Online (Moderation & Trust) [TODO]
- [ ] Implement Pete's core router in `bots/pete/`.
- [ ] Hook up Pete to `moderation_service` for warnings, mutes, and trust adjustments.
- [ ] Enforce permission checks across chats using `core/permissions.py`.
- [ ] Add unit tests for Pete handlers.

## Phase 7: Bring Eddy Online (Events & Reminders) [TODO]
- [ ] Implement Eddy's core router in `bots/eddy/`.
- [ ] Build event creation, RSVP, and attendance flows using `event_service`.
- [ ] Add automated reminder scheduling logic.
- [ ] Add unit tests for Eddy handlers.

## Phase 8: Bring Susy Online (Onboarding & Welcome) [TODO]
- [ ] Implement Susy's core router in `bots/susy/`.
- [ ] Build welcome flows for new users and initial identity creation hook.
- [ ] Implement music/session support if applicable.
- [ ] Add unit tests for Susy handlers.

## Phase 9: Final Migration & Deployment [TODO]
- [ ] Freeze the old Theo bot (currently on Render).
- [ ] Export legacy data (users, reading history, subscriptions).
- [ ] Map and migrate legacy data into the new Supabase schema.
- [ ] Deploy the new unified `BotManager` system to production.
- [ ] Perform integration smoke tests in production.
