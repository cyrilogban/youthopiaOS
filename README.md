# Theo (YouThopiaOS)

**Theo** (@theobiblebot) is an AI theological guide, daily scripture companion, and devotional ecosystem built for Telegram and the web.

Theo helps individuals and groups engage with Scripture through automated daily Verse of the Day (VOTD) delivery, dynamic multi-translation lookups, smart passage detection, and a rich Telegram Mini App powered by the YouVersion Platform.

> **Note on Project Scope:**
> This repository is **Theo only**. The previous 5-bot community ecosystem (Susy, Ed, Pete, and Lusy) was safely archived on November 24, 2026. See [docs/ARCHIVE.md](file:///c:/Users/HP%20240/Desktop/YOUTHOPIA%20BIBLE%20COMMUNITY/YouThopiaOS/docs/ARCHIVE.md) for restoration instructions and the permanent archive tag `archive/multi-bot-2026-11-24`.

---

## Features

### 1. Telegram Bot (@theobiblebot)
- **Daily Devotional Delivery:** Automated Verse of the Day broadcasts every morning at 6:00 AM WAT via APScheduler.
- **Passive Scripture Detection:** Automatically detects Bible citations in chat (e.g. `John 3:16`, `Psalm 23:1-6`) and returns formatted scripture cards with one-tap bookmarking and translation comparisons.
- **Multi-Translation Engine:** Quick toggling across King James (KJV), American Standard (ASV), World English Bible (WEB), and Basic English (BBE).
- **Personal & Group Subscriptions:** Subscriptions for individual DMs and group chats with customizable group translation defaults.
- **Bookmarks & Saved Verses:** Fast in-chat gallery of bookmarked passages with interactive pagination.

### 2. Telegram Mini App
- **Living Devotional Feed:** Daily scripture cards, Affirmation of the Day, and Prayer of the Day.
- **YouVersion Platform Integration:** Embedded Scripture explorer across major translations.
- **Verse Actions:** Heart (love), save, and native Telegram share sheet integration.
- **Personal Preferences:** Translation selector and daily reminder delivery toggles.

---

## Architecture Overview

```text
       [ Telegram Bot (@theobiblebot) ]   [ React Telegram Mini App ]
                         │                                │
                         ▼                                ▼
       [ FastAPI Gateway & Bot Runtime ] ──► [ Core Engine & Schedulers ]
                                        │
                                        ▼
                      [ Supabase PostgreSQL & Bible APIs ]
```

- **Runtime:** Single FastAPI & Uvicorn application serving the Mini App SPA and hosting the aiogram async polling bot in the background.
- **Database:** Supabase PostgreSQL for persistence (profiles, subscriptions, saved verses, feed items).
- **External APIs:** Bible-API.com and YouVersion Platform React SDK.

---

## Project Structure

```text
YouThopiaOS/
├── bots/
│   └── theo/              # Theodore bot handlers, services, and keyboards
├── gateway/
│   └── app/               # FastAPI trust boundary, auth, and REST endpoints
├── miniapp/               # React + TypeScript + Vite Telegram Mini App
│   └── src/
│       ├── components/    # Reusable UI, BibleTab, VerseCard, FeedPost
│       └── routes/theo/   # TheoHome, TheoSaved, TheoProfile
├── core/                  # Bot orchestration and lifecycle management
├── shared/                # Supabase database client, user/feed services
├── docs/
│   └── ARCHIVE.md         # Archived bots reference & revival guide
└── main.py                # Process entry point (Uvicorn + Bot runner)
```

---

## Quickstart

### 1. Requirements
- Python 3.11+
- Node.js 18+ & npm

### 2. Environment Variables
Create a `.env` file in the root directory:
```env
THEO_BOT_TOKEN=your_telegram_bot_token
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_or_service_key
YOUVERSION_APP_KEY=your_youversion_app_key
```

### 3. Setup & Run Locally
```bash
# Backend & Bot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Frontend Mini App (optional for dev)
cd miniapp
npm install
npm run dev
```

---

## Deployment
Deployed on **Render** as a single web service. The `render-build.sh` script installs Python dependencies, compiles the Mini App via Vite, and mounts the compiled frontend at the root `/` of the FastAPI web server.
