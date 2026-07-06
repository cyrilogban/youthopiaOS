# 📌 YouThopiaOS Stack & Requirements Specification

## 1. Project Overview

YouThopiaOS is a **Python-based multi-bot Telegram ecosystem** designed to run multiple specialized Telegram bots inside a **single codebase and deployment runtime**.

The architecture is:

* Multi-bot
* Async
* Shared-state
* Service-oriented
* Single deployment
* Centralized database

The stack is chosen to prioritize:

* scalability
* maintainability
* low hosting cost
* shared infrastructure
* Render deployment compatibility
* long-term ecosystem growth

---

# 2. Core Programming Language

## Python 3.12+ (preferred)

Python is the primary language.

Reasons:

* Mature Telegram ecosystem
* Strong async support
* Excellent backend tooling
* Easy deployment
* Good AI/tooling ecosystem
* Existing developer familiarity

Recommended: Python 3.12+
Minimum: Python 3.11+

---

# 3. Telegram Framework

## AIogram (MANDATORY)

AIogram is the standard Telegram framework for this system.

Reasons:

* Async-first architecture
* Better suited for multi-bot orchestration
* Modern Telegram API support
* Cleaner routing system
* Scales better than Telebot

Rules:

* All bots use AIogram
* No Telebot mixing
* No multiple Telegram frameworks

Single framework across ecosystem.

---

# 4. Async Runtime

Python async runtime is required.

Library: `asyncio`

Used for:

* running multiple bots simultaneously
* background jobs
* shared orchestration

BotManager should use `asyncio.gather()` to launch all bots.

---

# 5. Environment Configuration

## Python-dotenv

Package: `python-dotenv`

Purpose:

* Load `.env`
* Store tokens securely
* Manage environment variables

Required secrets:

* THEO_BOT_TOKEN
* LUSY_BOT_TOKEN
* PETE_BOT_TOKEN
* ED_BOT_TOKEN
* SUSY_BOT_TOKEN
* SUPABASE_URL
* SUPABASE_KEY

Rules:

* Never hardcode tokens
* `.env` ignored via `.gitignore`

---

# 6. Database Stack

## Supabase (PostgreSQL) — Primary

Python client: `supabase`

Purpose:

* unified user data
* XP system
* moderation logs
* event records
* shared identity
* analytics

Supabase is the **single source of truth**.

## MongoDB — Optional Secondary

Package: `pymongo`

Use ONLY if necessary for logs, flexible documents, non-critical caching.

Rule: Supabase remains authoritative. Mongo is optional.

---

# 7. API / Web Runtime

## FastAPI + Uvicorn

For Render deployment compatibility.

Purpose:

* health endpoint
* uptime monitoring
* webhooks (future)
* internal API
* Render service compatibility

---

# 8. HTTP Requests

Package: `requests` (or `httpx` for async)

Purpose: external APIs, scripture APIs, integrations.

---

# 9. Logging

Python built-in `logging` module.

Purpose: bot startup logs, moderation logs, deployment debugging, system observability.

Must be centralized. No random `print()` debugging in production.

---

# 10. Scheduler / Background Jobs

Preferred: `APScheduler`

Use cases: daily Bible delivery, reminders, scheduled events, cleanup jobs.

Avoid `while True + sleep` in production.

---

# 11. Dependency Management

Use `requirements.txt`, generated with `pip freeze > requirements.txt`.

Single dependency file for entire ecosystem.

---

# 12. Version Control

## Git + GitHub

Repository: `youthopiaOS`

Rules: one repo, one deployment target, feature-based commits, `.env` excluded.

---

# 13. Deployment Platform

## Render

Single web service running FastAPI, BotManager, and all Telegram bots.

Goal: minimize hosting cost, one runtime, one deployment pipeline.

---

# 14. Final Stack Summary

Core stack: Python, AIogram, Asyncio, Supabase, FastAPI, Uvicorn, dotenv, APScheduler, Git/GitHub, Render

Optional: MongoDB, PyMongo

---

# Final Design Principle

The stack is intentionally selected to support:

> A scalable, async, multi-bot community operating system running under a single deployment and unified backend architecture.
