# Archived Multi-Bot Ecosystem & Restoration Guide

This repository was transitioned from a 5-bot community ecosystem to a **Theo-only** standalone product on November 24, 2026.

The complete multi-bot history, code, tests, and configuration are permanently preserved at git tag:
```bash
archive/multi-bot-2026-11-24
```

---

## 1. Archived Bots Roster & Removal Commits

| Bot | Handle | Commit Hash | Role | Revive When |
|---|---|---|---|---|
| **Susan (Susy)** | `@susiehelpsbot` | `130edf3` | Welcome & Onboarding | If a welcoming or onboarding flow is needed again. |
| **Edmund (Edie / Eddy)** | `@ediecalendarbot` | `bb03bef` | Events & Reminders | If community events, calendar schedules, and reminders are needed again. |
| **Peter (Pete)** | `@petemodbot` | `c33e91d` | Safety & Moderation | If Cyril builds a moderation tool, or if a community needs moderation again. |
| **Lucy (Lusie)** | `@lusiequizbot` | `2a301ed` | Quizzes & Gamification | If quizzes and gamification are wanted again, for example as a general feature. |

*Additional archive commits:*
- Community verification scripts: `8a63bd9`
- Mini App paused bot routes & components: `c3264f9`
- Runtime & configuration to Theo-only: `6c6ca36`

---

## 2. How to Restore an Archived Bot

You can restore any single bot independently without rolling back the entire repo.

### Option A: Restore a specific bot's files directly from the archive tag
```bash
# Example: Restore Pete
git checkout archive/multi-bot-2026-11-24 -- bots/pete/

# Example: Restore Susy
git checkout archive/multi-bot-2026-11-24 -- bots/susy/ tests/test_susy.py

# Example: Restore Ed
git checkout archive/multi-bot-2026-11-24 -- bots/eddy/

# Example: Restore Lusy
git checkout archive/multi-bot-2026-11-24 -- bots/lusy/ scripts/fix_scramble_hints.py
```

Then re-enable the bot in `core/config.py`:
```python
BOT_NAMES = ("theo", "<restored_bot_name>")
```

### Option B: Undo a specific bot's removal commit
```bash
# Undo Pete's archival:
git revert c33e91d

# Undo Susy's archival:
git revert 130edf3

# Undo Ed's archival:
git revert bb03bef

# Undo Lusy's archival:
git revert 2a301ed
```

### Option C: Undo all cleanup commits (full reversal)
```bash
git revert 6c6ca36..130edf3
```

---

## 3. Database Safety Notice
**No database tables or columns were removed or modified.** All tables previously utilized by Susy, Ed, Pete, and Lusy remain intact in Supabase with all existing records preserved.

---

## 4. Future Cleanup Candidates (Do Not Act Without Approval)
The following shared code and database tables are currently kept in place for stability, but are unused by Theo's core functionality:

### Shared Python Services
- `shared/services/event_service.py` (Used by Edie for events)
- `shared/services/quiz_service.py` (Used by Lusy for quiz tracking)
- `shared/services/moderation_service.py` (Used by Pete for moderation actions)

### Supabase Database Tables (Untouched)
- `lusy_questions`, `lusy_game_sessions`, `lusy_game_history`, `quizzes`
- `community_events`, `event_attendees`, `user_birthdays`
- `moderation_actions`, `warning_records`, `appeals`, `chat_locks`
