# 📌 PROJECT SPECIFICATION: YouThopiaOS Multi-Bot Ecosystem

## 1. High-Level Overview

You are building a **multi-bot community operating system** for a Christian Gen Z digital community called **YOUTHOPIA BIBLE COMMUNITY**.

The system is not a single chatbot. It is a **distributed Telegram bot ecosystem** where each bot has a specialized role but all bots operate on a shared intelligence and data layer.

The system is designed as:

> A unified community OS composed of multiple Telegram bots coordinated through shared services, a centralized database, and a single deployment system.

---

## 2. Core Objective

The goal is to create:

* A scalable multi-bot architecture
* A unified user experience across all bots
* Shared memory and user identity across the system
* Modular bot responsibilities with strict separation of concerns
* A centralized intelligence and business logic layer

The system should behave like a **community operating system**, not independent bots.

---

## 3. Bot Ecosystem Structure

The system consists of 5 independent Telegram bots, each with a unique role:

### 1. Theo Bot (Bible Bot)

* Delivers daily Bible verses and devotionals
* Tracks reading consistency and spiritual engagement

### 2. Lusy Bot (Games & Engagement Bot)

* Handles quizzes, games, XP system, and gamification
* Manages user points, levels, and leaderboard

### 3. Pete Bot (Security Bot)

* Handles moderation, spam control, warnings, bans
* Maintains user behavior logs and trust scores

### 4. Ed Bot (Events Manager)

* Manages community events, reminders, registrations
* Tracks attendance and participation

### 5. Susy Bot (Welcome & Music Bot)

* Welcomes new members
* Handles social engagement and music/session interactions

Each bot has:

* Its own Telegram token
* Independent identity on Telegram
* Independent runtime handler
  BUT shares backend logic and data systems.

---

## 4. Critical Architectural Principle

### IMPORTANT RULE:

Bots are NOT independent systems.

They are **interfaces into a shared backend ecosystem**.

---

## 5. System Architecture Layers

### A. Bot Layer (Interface Layer)

Location: `/bots/*`

Each bot contains only:

* Telegram API connection
* Command handlers
* Message routing
* Presentation logic (formatting responses)

Each bot must NOT contain core business logic.

---

### B. Services Layer (Core Intelligence Layer)

Location: `/services`

This is the **single source of truth for all logic**.

Contains:

* `bible_service` → Bible content logic
* `xp_service` → gamification system
* `moderation_service` → security rules
* `event_service` → event management
* `music_service` → music/welcome system

Rules:

* Must never be duplicated inside bots
* Must be reusable across all bots

---

### C. Core Layer (System Infrastructure)

Location: `/core`

Contains:

* `bot_manager.py` → starts and manages all bots
* `dispatcher.py` → routing abstraction layer
* `config.py` → environment variables and global config

This layer controls system behavior and lifecycle.

---

### D. Database Layer (Single Source of Truth)

Location: `/db`

Contains:

* `supabase_client.py` → primary database (PostgreSQL via Supabase)
* `mongo_client.py` → optional secondary storage (non-critical data)

Rules:

* All bots share the same database
* User identity must be unified across all bots
* No bot should maintain its own database state

---

### E. Entry Point

* `main.py` → starts entire system via BotManager

---

## 6. Data Architecture Principle

There must be a **single unified user identity system**:

### Shared user model:

* telegram_id
* xp_score
* trust_score
* engagement_level
* activity history

All bots must reference the same user record.

---

## 7. Cross-Bot Intelligence Concept

The system supports shared behavioral intelligence:

* Actions in one bot affect behavior in others
* Example:

  * XP gained in Lusy affects profile used in Theo
  * Moderation actions in Pete affect access across all bots
  * Engagement history influences welcome messages in Susy

This creates a **cross-bot personality system per user**.

---

## 8. Deployment Model

* Single codebase (monorepo)
* Single deployment service (Render or equivalent)
* Multiple bot instances running in one runtime environment
* Async bot manager orchestrates all bots
* To have one Render service to deploy all 5 bots intead of a 5 different render service for each both


---

## 9. Key Design Constraints

### MUST FOLLOW:

* Shared logic ONLY in `/services`
* Shared DB access ONLY in `/db`
* System control ONLY in `/core`
* Bot folders are presentation-only layers
* No duplication of business logic across bots

### MUST AVOID:

* Copying XP logic into multiple bots
* Separate databases per bot
* Independent business logic inside bots
* Tight coupling between bots

---

## 10. System Philosophy

This system is designed as:

> A unified, modular, multi-agent community operating system where bots act as specialized interfaces over a shared intelligence and memory layer.

It is NOT:

* A collection of separate bots
* A simple chatbot project
* Independent Telegram scripts

It is:

* A coordinated digital ecosystem
* A structured community intelligence platform

---

## 11. Folder Structure Summary

```plaintext
youthopiaOS/
│
├── bots/
│   │
│   ├── theo/
│   │   ├── handlers/
│   │   │   ├── commands.py
│   │   │   ├── messages.py
│   │   │
│   │   ├── services/
│   │   │   ├── bible_service.py
│   │   │   ├── devotional_service.py
│   │   │   ├── delivery_service.py
│   │   │
│   │   ├── utils/
│   │   │   ├── formatter.py
│   │   │
│   │   ├── bot.py
│   │
│   ├── lusy/
│   │   ├── handlers/
│   │   │   ├── games.py
│   │   │   ├── quizzes.py
│   │   │
│   │   ├── services/
│   │   │   ├── game_service.py
│   │   │   ├── quiz_service.py
│   │   │   ├── xp_service.py
│   │   │
│   │   ├── utils/
│   │   │   ├── scoring.py
│   │   │
│   │   ├── bot.py
│   │
│   ├── pete/
│   │   ├── handlers/
│   │   │   ├── moderation.py
│   │   │   ├── admin.py
│   │   │
│   │   ├── services/
│   │   │   ├── moderation_service.py
│   │   │   ├── anti_spam_service.py
│   │   │   ├── warning_service.py
│   │   │
│   │   ├── utils/
│   │   │   ├── filters.py
│   │   │
│   │   ├── bot.py
│   │
│   ├── ed/
│   │   ├── handlers/
│   │   │   ├── events.py
│   │   │   ├── reminders.py
│   │   │
│   │   ├── services/
│   │   │   ├── event_service.py
│   │   │   ├── reminder_service.py
│   │   │
│   │   ├── utils/
│   │   │   ├── scheduler_helpers.py
│   │   │
│   │   ├── bot.py
│   │
│   ├── susy/
│   │   ├── handlers/
│   │   │   ├── welcome.py
│   │   │   ├── music.py
│   │   │
│   │   ├── services/
│   │   │   ├── welcome_service.py
│   │   │   ├── music_service.py
│   │   │
│   │   ├── utils/
│   │   │   ├── greeting_formatter.py
│   │   │
│   │   ├── bot.py
│
├── shared/
│   │
│   ├── db/
│   │   ├── supabase_client.py
│   │   ├── mongo_client.py
│   │
│   ├── config/
│   │   ├── settings.py
│   │   ├── env_loader.py
│   │
│   ├── logging/
│   │   ├── logger.py
│   │
│   ├── utils/
│   │   ├── helpers.py
│   │   ├── time_utils.py
│   │   ├── validators.py
│   │
│   ├── services/
│   │   ├── user_service.py
│   │   ├── analytics_service.py
│   │   ├── notification_service.py
│
├── core/
│   │
│   ├── bot_manager.py
│   ├── dispatcher.py
│   ├── scheduler.py
│
├── tests/
│   ├── test_theo.py
│   ├── test_lusy.py
│   ├── test_pete.py
│   ├── test_ed.py
│   ├── test_susy.py
│
├── main.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md

---

## 12. Final Summary Statement

The system is a **multi-bot, shared-state, modular community operating system** designed to unify multiple Telegram bots under a single intelligence and data layer, enabling consistent user identity, shared behavior tracking, and coordinated community experiences across all bots.
SHARING GOD'S LOVE ALL THE WAY 💜🎉