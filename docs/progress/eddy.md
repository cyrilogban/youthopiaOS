# EDDY PROGRESS TRACKER

This document tracks the live development progress of the Eddy bot.

### Milestone 1: The Foundation (Data & Routing)
- [x] Verify `events` and `event_participants` Supabase tables
- [x] Create `bots/eddy/router.py`
- [x] Register `/start` and `/help` commands
- [x] Register Eddy's commands in `bot.set_my_commands()`

### Milestone 2: The Autonomous Schedule Engine (Cron Jobs)
- [x] Install `apscheduler`
- [x] Build the 8:00 PM Pre-Alert Cron Job
- [x] Build the 9:00 PM Trigger Cron Job
- [x] Add Last Wednesday of the Month logic for Book Reviews

### Milestone 3: The RSVP & Attendance Tracker
- [x] Add Inline Keyboard buttons (`✅ Coming`, `❓ Maybe`, `❌ Can't Attend`)
- [x] Implement Callback Query handler for RSVPs
- [x] Connect RSVPs to Supabase

### Milestone 4: Ad-Hoc Admin Event Creator (FSM)
- [x] Create `/new_event` command (Admin restricted)
- [x] Build Aiogram State Machine (Title -> Date -> Description)
- [x] Build logic to save to Supabase
- [x] Add Prompt to broadcast to the Main Group with RSVP buttons

### Milestone 5: Cross-Bot Integration
- [x] Trigger Lusy games on Friday at 9:00 PM
- [x] Add `/reminders` logic (Toggle notifications)
- [x] (Bonus) Sync with Theo for Wednesday Devotionals

### Technical Notes & Architecture
- **Admin Custom Events (`/new_event`)**: Secured by checking `ADMIN_OWNER_ID` / `ADMIN_IDS`. Automatically saves to the Supabase `events` table.
- **Automated Reminders (8:45 PM)**: The cron job scans the `bot_user_state` table to respect user notification preferences.
- **Reminder Toggle**: The `[ 🔔 Reminders ]` button toggles a `reminders_enabled` boolean inside the `state` jsonb column of `bot_user_state` where `bot_name = 'eddy'`.
- **Lusy Sync**: Ed explicitly tags `@iamlusybot` at 9:00 PM on Fridays, which acts as a webhook trigger for Lusy's placeholder games menu.
