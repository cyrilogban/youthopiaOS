# YouThopiaOS Unified System Instruction

This file is a private local planning document for early architecture decisions. It is intentionally ignored by Git and should not be committed while the unified system is still being designed.

## Refined Project Instruction

Design and implement YouThopiaOS as a modular multi-bot Telegram operating system for YOUTHOPIA BIBLE COMMUNITY.

The system must unify multiple independent Telegram bot interfaces under one shared backend, one identity model, one primary Supabase database, and one runtime entry point.

YouThopiaOS is not a collection of separate bots. It is one ecosystem, one identity system, and multiple bot interfaces.

## Existing Context

Theo already exists as a standalone Telegram bot running on Render.

The current Theo bot already uses Supabase and MongoDB. That existing setup is useful context, but it is not the final architecture for the unified system.

The new system should be built cleanly from the early stage. The existing Theo deployment may be stopped when needed so the unified architecture can be created properly across all bots.

Legacy Theo data should not control the new schema design. If old Theo data needs to be preserved, it can be mapped into the new unified schema after the schema is stable.

## Core Goal

Build a modular multi-bot system where:

- all bots share a single user identity system
- all authoritative persistent state is stored in Supabase
- MongoDB is used only for logs, raw events, telemetry, and temporary unstructured data
- all bots operate under one orchestration system
- the whole system is deployed as a single runtime through `main.py`

## Bots In The System

Theo is the Bible and devotional bot.

Lusy is the games, quizzes, XP, and leaderboard bot.

Pete is the moderation and security bot.

Eddy is the events and scheduling bot. The internal code folder may remain `ed` unless the project is renamed consistently.

Susy is the onboarding, engagement, and music bot.

Each bot keeps its own Telegram token and public identity, but all bots share the same backend identity and data systems.

## Architecture Principle

Bots are independent in interface but unified in data, identity, orchestration, and persistence.

Bot folders are interface layers. They should contain Telegram handlers, presentation formatting, command routing, and bot-specific helper logic.

Bots must not directly access databases.

All database access must go through the shared database layer and shared services.

## Single Source Of Truth Rule

Supabase is the only authoritative database for persistent application state.

Supabase owns:

- user profiles
- global Telegram identity
- XP and levels
- roles and permissions
- moderation state
- event participation
- bot-specific user state
- global analytics summaries
- cross-bot ecosystem state

MongoDB is secondary and non-authoritative.

MongoDB may only be used for:

- raw logs
- raw bot events
- debugging payloads
- unstructured telemetry
- temporary operational traces

MongoDB must not become the source of truth for user identity, XP, permissions, events, or moderation decisions.

## Group Tracking Decision

Theo's old standalone system used MongoDB to track Telegram groups and subscribed groups.

That MongoDB data included operational group state such as:

- Telegram `chat_id`
- whether Theo was enabled in a group
- group title
- preferred Bible translation
- whether the group was official
- whether the group was subscribed to deliveries

In the unified YouThopiaOS system, this kind of data is no longer treated as telemetry.

It controls real bot behavior, so it is authoritative application state.

Therefore, current group state must live in Supabase.

Supabase owns:

- which Telegram chats/groups exist
- which bots are active in each group
- whether a bot is enabled, disabled, left, or kicked
- group-level bot settings
- Theo translation preferences
- official group flags
- devotional subscriptions
- future Lusy, Pete, Eddy, and Susy group settings

MongoDB may still store raw historical group events, but it must not be the source of truth for current group status.

MongoDB may store:

- raw Telegram updates
- bot added to group events
- bot removed from group events
- group title change payloads
- delivery attempt logs
- delivery failure logs
- debugging payloads

The rule is:

```text
Supabase = what is true now
MongoDB = what happened over time
```

This replaces Theo's old MongoDB `groups` and `subscribed_groups` role with Supabase tables such as:

- `telegram_chats`
- `bot_chat_memberships`
- `chat_bot_settings`
- `chat_subscriptions`

Existing Theo MongoDB group data can later be treated as migration source data.

It should not define the final schema.

## Target Architecture

```text
YouThopiaOS/
|
├── bots/
|   ├── theo/
|   ├── lusy/
|   ├── pete/
|   ├── ed/ or eddy/
|   ├── susy/
|
├── core/
|   ├── bot_manager.py
|   ├── identity.py
|   ├── permissions.py
|   ├── config.py
|
├── shared/
|   ├── db/
|   |   ├── supabase.py
|   |   ├── mongo.py
|   |
|   ├── services/
|   |   ├── user_service.py
|   |   ├── xp_service.py
|   |   ├── event_service.py
|   |
|   ├── utils/
|   ├── logging/
|
├── main.py
├── requirements.txt
├── .env
├── .gitignore
```

## Database Design Direction

The unified Supabase schema should be designed from scratch.

The first schema priority is a single shared user identity system. Every bot action should be connected back to the same global user record.

The schema should support cross-bot behavior from the start, even if some features are implemented later.

The schema must clearly separate authoritative application state from telemetry.

Supabase stores authoritative records. MongoDB stores raw events and operational traces.

## Runtime Architecture

`main.py` is the only system entry point.

`main.py` starts `BotManager`.

`BotManager` loads configuration, initializes Supabase and MongoDB clients, then starts all enabled bots concurrently.

All bots run under one Python runtime and one deployment service.

## Bot Boundary Rule

Bots must not access Supabase or MongoDB directly.

Bot handlers receive Telegram updates, validate user intent, and call shared services.

Shared services own business logic.

Shared database modules own persistence.

Bot-specific services may exist only for logic that belongs to one bot's domain, and they must still use shared services or shared database layers for persistence.

## No Legacy System Rule

The unified system should be built fresh.

Do not assume Telebot compatibility.

Do not design around partial migration logic.

Do not preserve old standalone bot architecture as the new system foundation.

The old Theo system is a source of lessons and possible data migration, not the architecture to copy.

## Build Order

1. Define the unified Supabase schema.
2. Define the global user identity model.
3. Define core roles, permissions, XP, moderation, and event tables.
4. Build shared database clients for Supabase and MongoDB.
5. Build shared services around users, XP, roles, events, analytics, and logging.
6. Build `BotManager` and `main.py`.
7. Bring each bot into the unified runtime one at a time.
8. Decide whether to migrate old Theo data after the new schema is stable.

## Success Criteria

The system is correct when:

- one command starts everything with `python main.py`
- all bots run under one runtime
- all user data is consistent in Supabase
- MongoDB only stores logs, events, telemetry, and temporary unstructured data
- bots are modular but share one identity system
- no bot directly owns database persistence

## Immediate Next Step

Before writing bot feature logic, design the Supabase schema carefully.

The schema should answer:

- What is one user across all bots?
- How do we represent a user in multiple Telegram chats?
- How do XP and levels work globally?
- How do roles and permissions work globally and per chat?
- How do moderation actions affect access across bots?
- How do events and attendance connect to user identity?
- What data belongs in Supabase, and what data is only telemetry for MongoDB?

## User Personalization and Ecosystem Onboarding

The multi-bot ecosystem creates a unique problem: when is a user "new"? 

In YouThopiaOS, "newness" is a system-wide property, not a bot-specific one. 

**The Rule:**
- **System-wide Engagement:** The `engagement_level` field in the unified `users` table determines if they are fundamentally new to the YOUTHOPIA digital sanctuary. It defaults to `'new'`.
- **Bot-specific Tracking:** `bot_user_state` is used if we need to know if an active community member is trying a specific bot for the first time.

**Implementation Standard:**
1. A bot checks `user.get("engagement_level") == "new"`.
2. If true, the bot delivers the grand community onboarding message.
3. Immediately after, the bot calls `UserService.set_engagement_level(user_id, "active")` so no other bot in the ecosystem gives them the massive welcome text again. 
4. Returning users get short, bot-specific greetings.








## Risks (Resolved ✅)

- Shared DB dependency (Addressed)
  - Refactored raw database queries into service classes; services are now fully responsible for DB interaction.
- Mixed responsibilities (Resolved)
  - All direct DB queries and business logic inside Lusy, Eddy, and Theo routers have been moved into shared service classes.
- Inconsistent config usage (Resolved)
  - Susy bot config loading consolidated to retrieve settings directly from injected services container.
- Empty/unused module (Resolved)
  - dispatcher.py documented as a future-proofing placeholder to clarify its status.
- Admin permission checks (Resolved)
  - Extracted IsAdminFilter into core/filters.py to allow standard admin checks across the entire system.
- Bot startup lifecycle complexity (Resolved)
  - Hardened Susy bot initialization with nested try-finally blocks to guarantee pyrogram/pytgcalls teardown.
- Supabase client threading (Acknowledged)
  - Acknowledged that blocking calls use asyncio.to_thread due to the synchronous nature of the client. Latency managed by centralizing query logic.

## Improvements (Completed ✅)

- Centralize config and bot lifecycle (Completed)
  - AppConfig is injected into ServiceContainer and loaded by Susy directly.
- Consolidate shared logic (Completed)
  - Created QuizService, get_leaderboard in UserService, and get_user_upcoming_events in EventService. Routers are now thin.
- Fill or remove dispatcher.py (Completed)
  - Addressed by adding status comments documenting dispatcher.py as a planned routing boundary placeholder.
- Strengthen permissions (Completed)
  - Extracted a reusable IsAdminFilter to core/filters.py.
- Improve error handling (Completed)
  - Wrapped Pyrogram and PyTgCalls startups in nested try-finally blocks for safe teardown.
- Standardize bot commands (Acknowledged)
  - Menu registration standard is kept modular per bot, with shared constants planned for localization.