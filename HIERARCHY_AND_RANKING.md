# YouThopiaOS Community Hierarchy & Ranking System

This document explains the **4-Tier, 9-Rank Community Hierarchy** in YouThopiaOS: what it is, why it was designed this way, how it works across the entire codebase, and how it connects our 5 Telegram bots with the React Mini App.

---

## 1. Overview & Community Vision

The YouThopia hierarchy translates spiritual growth, active participation, and community leadership into a clear, tangible progression ladder.

### The 4 Tiers & 9 Official Ranks

| Tier | Rank ID | Official Title | Emoji | Badge Color | Requirement / Mode | Purpose & Character |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **Tier 1: Entry Level** | `seeker` | **YouTopian Seeker** | 🌸 | `#D98A95` | 0 YP / Initial Join | A newcomer exploring faith and the YouThopia community. |
| | `gathered_one` | **YouTopian Gathered One** | 🌾 | `#D2B48C` | 50 YP / Onboarding Tour | A verified member welcomed into the flock. |
| **Tier 2: Active Contributors** | `spark` | **YouTopian Spark** | ⚡ | `#88C9E8` | 100 YP (Level 2) | Consistent participation in quizzes & daily verses. |
| | `luminary` | **YouTopian Luminary** | 💡 | `#85D6A5` | 500 YP (Level 5) | A shining light who shares Scripture and stays active. |
| | `witness` | **YouTopian Witness** | 📜 | `#B8CB80` | 1,000 YP (Level 10) | A seasoned Bible student living and witnessing the Word. |
| **Tier 3: Mentors & Builders** | `refiner` | **YouTopian Refiner** | 🔨 | `#B0A8E8` | 2,500 YP (Lvl 15) or Admin | Mentoring newer members and refining community discussions. |
| | `pillar` | **YouTopian Pillar** | 🏛️ | `#D4628E` | 5,000 YP (Lvl 25) or Admin | A foundational anchor supporting community ministries. |
| **Tier 4: Core Leadership** | `elite` | **YouTopian Elite** | 👑 | `#8EA5D0` | 10,000 YP or Admin Appointed | Group administrators, moderators, and team leads. |
| | `ambassador` | **YouTopian Ambassador** | 🌍 | `#B88B97` | 25,000 YP or Founder Appointed | Global visionaries and executive community directors. |

---

## 2. System Architecture & Data Flow

```mermaid
flowchart TD
    subgraph UserAction["User Ecosystem Action"]
        A1["Quiz with Lusy"]
        A2["Devotional with Theo"]
        A3["Onboarding with Susy"]
        A4["Admin /setrank Command"]
    end

    subgraph ServiceLayer["Shared Backend Engine"]
        XP["XPService.award_xp()"]
        RankSvc["RankService.resolve_rank()"]
        UserSvc["UserService"]
    end

    subgraph Database["Supabase Single Source of Truth"]
        DB_Users[("users Table\n(total_xp, level, manual_rank_id)")]
    end

    subgraph Consumers["Presentation Endpoints"]
        Bots["5 Telegram Bots\n(/profile, /leaderboard, /start)"]
        Gateway["FastAPI Gateway\n(GET /profile, GET /api/leaderboard)"]
        MiniApp["React/Vite Mini App\n(<RankBadge /> on Home, Quiz, Modal)"]
    end

    A1 --> XP
    A2 --> XP
    A3 --> XP
    A4 --> DB_Users

    XP --> DB_Users
    DB_Users --> RankSvc
    RankSvc --> Bots
    RankSvc --> Gateway
    Gateway --> MiniApp
```

---

## 3. Detailed Component Implementation

### A. Central Hierarchy Engine (`shared/services/rank_service.py`)
`RankService` is a pure, centralized resolver. It defines each rank as an immutable `RankDefinition` dataclass containing:
* `id`: Machine identifier (`seeker`, `spark`, `elite`, etc.)
* `title`: Human-readable name (`YouTopian Spark`)
* `tier`: Grouping tier (`Entry Level`, `Active Contributors`, etc.)
* `min_xp`: Minimum YP threshold for automatic ladder advancement
* `bg_color` & `text_color`: Exact hex styling tokens from the design specification
* `emoji`: Representative icon (`🌸`, `⚡`, `👑`, etc.)
* `description`: Character motto
* `requires_manual_approval`: Flag (`True` for Tier 4 `elite` and `ambassador`)

**Resolution Logic with Algorithmic Ceiling:**
```python
@classmethod
def resolve_rank(cls, total_xp: int = 0, manual_rank_id: str | None = None) -> RankDefinition:
    # 1. Check if user has an admin-appointed leadership override
    if manual_rank_id:
        custom = cls.get_rank_by_id(manual_rank_id)
        if custom:
            return custom

    # 2. Automated XP ladder capped at Pillar (Tier 3)
    current_rank = RANKS[0]
    for rank in RANKS:
        if rank.requires_manual_approval:
            break
        if total_xp >= rank.min_xp:
            current_rank = rank
        else:
            break
    return current_rank
```

---

### B. 24-Hour Multi-Bot Scout & Founder Gating (`bots/eddy/services/scheduler.py`)
To prevent gaming and ensure Tier 4 leaders represent genuine spiritual maturity and trust:
* **The Algorithmic Ceiling:** Automated XP progression stops at **Tier 3 (Pillar)**. Even with 100,000 YP, no user can automatically become **Elite** or **Ambassador**.
* **Daily 24h Background Sweep (`02:00 AM WAT`):** Eddy's scheduler runs `sweep_daily_rank_nominations(bot)` every 24 hours.
* **Scouting Criteria:** Members with $\ge 10,000\text{ YP}$, $\ge 95\text{ Pete Trust Score}$, and active engagement are scouted.
* **Founder Nomination Card:** Eddy sends a private alert directly to the Founder (`ADMIN_OWNER_ID`):
  ```text
  👑 Leadership Nomination Scout (24h Daily Sweep)

  👤 Candidate: Cyril Ogban (@cyril | ID: 12345678)
  ⭐ Total XP: 14,500 YP (Capped at 🏛️ Pillar ceiling)
  🛡️ Pete Trust Score: 100/100
  🏅 Eligible Rank: 👑 YouTopian Elite (Core Leadership)

  👉 To Appoint:
  /setrank @cyril elite
  ```

---

### C. Gateway REST API (`gateway/app/models.py` & `main.py`)
* **`UserProfile` Model:** Includes `rank_title`, `rank_tier`, `rank_badge_color`, and `rank_emoji`.
* **`LeaderboardItem` Model:** Delivers rank metadata alongside score rankings so the Mini App never needs to calculate ranks client-side.
* **`GET /profile` & `GET /api/leaderboard`:** Resolve user records through `RankService.resolve_rank(total_xp, manual_rank_id)`.

---

### D. Telegram Bot Harmonization
1. **Shared Profile Card (`shared/utils/ui.py`):**
   * Invoked across Theo, Susy, Pete, Lusy, and Eddy for `/profile` commands.
   * Renders:
     ```text
     👤 Cyril Ogban
     🏅 Rank: ⚡ YouTopian Spark (Lvl 2)
     ━━━━━━━━━━━━━━━━
     ⭐ XP: 150 YP
     🛡️ Trust Score: 100/100
     ━━━━━━━━━━━━━━━━
     ```
2. **Lusy Bot Quizzes (`bots/lusy/router.py`):**
   * Replaced legacy placeholder titles (`Novice`, `High Priest`) with `services.ranks.resolve_rank()`.
   * Group leaderboard cards display `🥇 Cyril Ogban (⚡ YouTopian Spark) - 150 YP`.
3. **Susy Onboarding Tour (`shared/utils/ui.py`):**
   * On completing the 3-page orientation tour, awards **+50 YP** and crowns the user as **🌾 YouTopian Gathered One**.

---

### E. React Mini App Integration
1. **`<RankBadge />` Component (`miniapp/src/components/RankBadge.tsx`):**
   * Reusable pill badge component supporting sizes `sm`, `md`, and `lg`.
   * Computes automatic high-contrast foreground text based on background color luminance.
2. **Home Tab (`miniapp/src/components/tabs/HomeTab.tsx`):**
   * Greets users with their full name and displays `<RankBadge />` beside their server-verified status.
3. **Quiz Tab (`miniapp/src/components/tabs/QuizTab.tsx`):**
   * Displays the player's current rank status inside the XP banner.
   * Renders `<RankBadge size="sm" />` beside each player in the top-10 global leaderboard.
4. **Profile Modal (`miniapp/src/App.tsx`):**
   * Renders the user's full rank badge and tier details inside the account modal.

---

### F. Admin Command Governance (`core/admin_commands.py`)
Administrators can appoint members to Tier 3 and Tier 4 leadership ranks using:
```text
/setrank @username <rank_id>
/setrank <telegram_id> <rank_id>
/setrank <rank_id>  (as a reply to any user message)
```

* **Interactive Autocomplete in Groups:** `/setrank` is registered in `BotCommandScopeAllChatAdministrators()` across Pete, Theo, Lusy, Susy, and Eddy, so it automatically appears in the suggested command popup when an admin types `/` inside any community group.

**Valid Rank Arguments:**
* `seeker`, `gathered_one`, `spark`, `luminary`, `witness`, `refiner`, `pillar`, `elite`, `ambassador`
* `auto`: Clears the override and returns the member to automatic XP progression.
