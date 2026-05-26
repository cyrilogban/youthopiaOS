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

Recommended:

```plaintext id="7v6b5x"
Python 3.12+
```

Minimum:

```plaintext id="4e3r2t"
Python 3.11+
```

---

# 3. Telegram Framework

## AIogram (MANDATORY)

Framework:

```plaintext id="8k9j2m"
aiogram
```

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

Libraries:

```plaintext id="h6n4v1"
asyncio
```

Used for:

* running multiple bots simultaneously
* background jobs
* shared orchestration

BotManager should use:

```python id="drdj3m"
asyncio.gather()
```

to launch all bots.

---

# 5. Environment Configuration

## Python-dotenv

Package:

```plaintext id="w2m7s8"
python-dotenv
```

Purpose:

* Load `.env`
* Store tokens securely
* Manage environment variables

Required secrets:

```plaintext id="4v9k2d"
THEO_BOT_TOKEN
LUSY_BOT_TOKEN
PETE_BOT_TOKEN
ED_BOT_TOKEN
SUSY_BOT_TOKEN
SUPABASE_URL
SUPABASE_KEY
```

Rules:

* Never hardcode tokens
* `.env` ignored via `.gitignore`

---

# 6. Database Stack

Primary database:

## Supabase (PostgreSQL)

Python client:

```plaintext id="1j3s8a"
supabase
```

Purpose:

* unified user data
* XP system
* moderation logs
* event records
* shared identity
* analytics

Supabase is the **single source of truth**.

Reasons:

* PostgreSQL reliability
* hosted backend
* auth-ready
* realtime capabilities
* low operational cost

---

## Optional Secondary Database

Optional:

## MongoDB

Package:

```plaintext id="q7d2x9"
pymongo
```

Use ONLY if necessary.

Possible use cases:

* logs
* flexible documents
* non-critical caching

Rule:

Supabase remains authoritative.

Mongo is optional.

---

# 7. API / Web Runtime

For Render deployment:

## FastAPI

Package:

```plaintext id="u9f1k3"
fastapi
```

ASGI server:

```plaintext id="j2m6t8"
uvicorn
```

Purpose:

* health endpoint
* uptime monitoring
* webhooks (future)
* internal API
* Render service compatibility

Example:

```plaintext id="x5r7p2"
GET /health
```

Returns:

```plaintext id="g9h4m1"
OK
```

This keeps deployment healthy.

---

# 8. HTTP Requests

Package:

```plaintext id="k1w5v8"
requests
```

Purpose:

* external APIs
* scripture APIs
* integrations

Optional future replacement:

```plaintext id="p4s8d6"
httpx
```

for async networking.

---

# 9. Logging

Use:

Python built-in

```plaintext id="n3q7x2"
logging
```

Purpose:

* bot startup logs
* moderation logs
* deployment debugging
* system observability

Must be centralized.

No random `print()` debugging in production.

---

# 10. Scheduler / Background Jobs

For periodic tasks:

Preferred:

```plaintext id="l5z2r7"
APScheduler
```

Package:

```plaintext id="e8t3u1"
apscheduler
```

Use cases:

* daily Bible delivery
* reminders
* scheduled events
* cleanup jobs

Avoid:

```plaintext id="b6y9k4"
while True + sleep
```

in production.

---

# 11. Dependency Management

Use:

```plaintext id="r2m5v7"
requirements.txt
```

Generated with:

```bash id="s0h4x8"
pip freeze > requirements.txt
```

Single dependency file for entire ecosystem.

---

# 12. Version Control

Platform:

## Git + GitHub

Repository:

```plaintext id="q1w2e3"
youthopiaOS
```

Rules:

* one repo
* one deployment target
* feature-based commits
* `.env` excluded

---

# 13. Deployment Platform

Primary deployment:

## Render

Model:

Single web service

Runs:

* FastAPI
* BotManager
* all Telegram bots

Goal:

* minimize hosting cost
* one runtime
* one deployment pipeline

---

# 14. Recommended VS Code Extensions

Suggested:

```plaintext id="c4v8n2"
Python
Pylance
GitLens
dotenv
Error Lens
```

Optional:

```plaintext id="m7t1x5"
Thunder Client
```

for API testing.

---

# 15. Installation Requirements

Create virtual environment:

PowerShell:

```powershell id="z8j3m6"
python -m venv venv
```

Activate:

```powershell id="x2p9k4"
venv\Scripts\activate
```

---

Install core stack:

```powershell id="v5s1d8"
pip install aiogram
pip install python-dotenv
pip install supabase
pip install fastapi
pip install uvicorn
pip install requests
pip install apscheduler
```

Optional Mongo:

```powershell id="h3k7n1"
pip install pymongo
```

Generate dependencies:

```powershell id="w8m4r2"
pip freeze > requirements.txt
```

---

# 16. Final Stack Summary

Core stack:

```plaintext id="y6u2i9"
Python
AIogram
Asyncio
Supabase
FastAPI
Uvicorn
dotenv
APScheduler
Git/GitHub
Render
```

Optional:

```plaintext id="t1r4e7"
MongoDB
PyMongo
```

---

# Final Design Principle

The stack is intentionally selected to support:

> A scalable, async, multi-bot community operating system running under a single deployment and unified backend architecture.
