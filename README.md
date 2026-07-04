# YouThopiaOS

`YouThopiaOS` is a modular, Python-powered, multi-bot Telegram ecosystem designed to run multiple specialized bots under a single architecture, shared intelligence layer, and centralized deployment pipeline.

Rather than treating bots as isolated scripts, YouThopiaOS approaches community automation as an integrated operating system where independent bots work together through shared services, unified user identity, and centralized infrastructure.

---

## 🎯 Vision
YouThopiaOS exists to create a scalable and intelligent digital ecosystem for community management, engagement, discipleship, moderation, and automation.

The project is designed around one central philosophy:
> **Multiple specialized bots. One ecosystem. One intelligence layer.**

---

## 📖 Background & Evolution
The bots inside YouThopiaOS were originally developed as separate standalone Telegram systems with distinct responsibilities and infrastructure.

Over time, maintaining multiple isolated deployments, duplicated logic, and fragmented databases introduced operational overhead and scalability limitations.

YouThopiaOS is the architectural evolution of those systems. It consolidates previously independent bots into a single coordinated platform while preserving their individual identities and responsibilities.

This transition enables:
* 🌐 **Shared Infrastructure** — Consolidated compute resources and unified configurations.
* 📉 **Reduced Operational Costs** — Single deployment instance instead of five.
* 👥 **Unified User Experience** — Unified user profiles and stats shared across bots.
* 🧠 **Cross-Bot Intelligence** — Services can coordinate actions seamlessly.
* 🛠️ **Centralized Maintenance** — Global updates applied in a single repository.

---

## 🤖 Bot Ecosystem
Each bot retains its own Telegram token, Telegram identity, and independent interaction model, but all operate through a shared backend architecture.

### 📖 Theo Bot *(Bible & Scripture Engagement)*
* 📌 Daily Bible delivery (Verse of the Day)
* 📌 Scripture engagement & reading consistency tracking
* 📌 Devotionals and faith-based interactions

### 🎮 Lusy Bot *(Gamification & Engagement)*
* 📌 Custom games (Bible Challenge, Verse Completion, Verse Scramble, Trivia Race)
* 📌 Global user XP, levels, and leaderboard stats
* 📌 Automated participation reward distribution

### 🛡️ Pete Bot *(Moderation & Security)*
* 📌 Group spam control and warning workflows
* 📌 Administrative ban & kick automation
* 📌 Community safety logs and trust scores

### 📅 Ed Bot *(Events & Reminders)*
* 📌 Community event scheduling, registrations, and reminders
* 📌 Announcement broadcast coordination
* 📌 Attendance and participation analytics

### 💬 Susy Bot *(Hospitality & Onboarding)*
* 📌 Member welcome flow and onboarding guides
* 📌 Social engagement support
* 📌 Interactive music and session integration

---

## 🏗️ Layered Architecture

```text
       [ 📱 Bot Interface Layer ] (aiogram command routers & presentation)
                   │
                   ▼
      [ 📦 Shared Services Layer ] (business logic, XP, event scheduling)
                   │
                   ▼
     [ 🗄️ Database Access Layer ] (Supabase PostgreSQL / MongoDB Client)
```

### 📱 1. Bot Layer
* **Location:** `/bots`
* **Purpose:** Handles Telegram-specific interaction, message routing, and response formatting.
* *Note: Bots contain interface logic only. No business logic or database queries reside here.*

### 🧠 2. Core Layer
* **Location:** `/core`
* **Purpose:** Bot orchestration runtime, lifecycle management, and shared config loaders.

### 📦 3. Services Layer
* **Location:** `/services`
* **Purpose:** Centralized business rules (e.g. `xp_service`, `moderation_service`). Reusable across all bot instances.

### 🗄️ 4. Database Layer
* **Location:** `/db`
* **Purpose:** Single source of truth for persistence. Shares user state and community stats across all bot interfaces.

---

## 📂 Folder Blueprint
```text
youthopiaOS/
├── bots/                  # Bot presentation interfaces
│   ├── theo/              # 📖 Scripture & Devotional Bot
│   ├── lusy/              # 🎮 Games, Quizzes, & XP Bot
│   ├── pete/              # 🛡️ Anti-Spam & Moderation Bot
│   ├── ed/                # 📅 Event & Reminders Bot
│   └── susy/              # 💬 Hospitality & Greeting Bot
├── shared/                # Core libraries & utilities
│   ├── db/                # Supabase & MongoDB clients
│   ├── services/          # Shared logic (users, analytics)
│   └── utils/             # Formatters, checkers, time utils
├── core/                  # Bot Manager startup orchestration
├── main.py                # Runtime entry point
└── requirements.txt       # Dependencies
```

---

## 💻 Tech Stack
* 🐍 **Python** (Asyncio runtime core)
* 🤖 **AIogram** (Telegram Bot Framework)
* ⚡ **Supabase** (Postgres DB, API Client)
* 🚀 **FastAPI / Uvicorn** (Webhook management APIs)
* ⏰ **APScheduler** (Event reminders and cron tasks)

---

## 📥 Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/cyrilogban/youthopiaOS.git
   cd youthopiaOS
   ```
2. **Setup virtual environment:**
   ```powershell
   python -m venv venv
   venv\Scripts\activate  # Unix/macOS: source venv/bin/activate
   ```
3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

---

## 🔒 Environment Configuration
Create a `.env` file in the root directory:
```env
THEO_BOT_TOKEN=your_token
LUSY_BOT_TOKEN=your_token
PETE_BOT_TOKEN=your_token
ED_BOT_TOKEN=your_token
SUSY_BOT_TOKEN=your_token

SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```
> [!WARNING]
> Never commit secrets. Ensure `.env` is listed inside `.gitignore`.

---

## 🚀 Deployment
* **Target:** Render
* **Configuration:** Single web service container running all 5 bots concurrently alongside FastAPI webhooks in a unified process.

---

## 💡 Core Principles
* **Single Source of Truth** — Shared logic exists once, never duplicated.
* **Separation of Concerns** — UI handlers focus purely on presentation.
* **Modular Design** — New bots or services drop in with minimal friction.
* **Cost Efficiency** — Multi-bot execution inside a single host runtime.

---

## 🗺️ Roadmap
* ✦ Shared cross-bot user profiles & analytics
* ✦ Global reputational scoring system
* ✦ Web-based administrator dashboard

---

## 🤝 Contribution & Collaboration
This is a faith tool for community use to support Christian digital communities for the furtherance of the gospel in digital ecosystems. It is open to Christian developers who want to collaborate, contribute, and improve the ecosystem.

* 🛠️ **Want to write code?** Check open issues, fork the repo, and submit a Pull Request!
* 💡 **Suggestions & Feedback:** We'd love to hear how we can improve our games, devotional tools, or moderation controls to serve the community better.

---

## 💜 About YOUTHOPIA BIBLE COMMUNITY
YouThopiaOS is built for the **YOUTHOPIA BIBLE COMMUNITY** ecosystem — a Christ-centered digital community focused on faith, spiritual growth, personal development, and meaningful connection.

**SHARING GOD'S LOVE ALL THE WAY 💜🎉**