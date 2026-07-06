# EDDY (@iamedyybot) - PRODUCT ROADMAP

## Mission Statement
> **Keep the community organized so members never miss important moments.**
Ed is the heartbeat of the YouThopia Bible Community. Rather than acting as a simple "create event" bot, Ed is a fully autonomous scheduling engine that runs the daily community rhythms and handles all operations, reminders, and attendance tracking.

---

## 📅 THE DAILY AUTOMATION SCHEDULE
Ed will be hardcoded to manage the official YouThopia 9:00 PM - 10:00 PM WAT daily schedule.

- **Monday:** Motivational Monday (Growth & Personal Development)
- **Tuesday:** Discussion Tuesday (Bible Study & Live Calls)
- **Wednesday:** Wisdom Wednesday (Doctrine Dives) / *Last Wednesday: Book Review*
- **Thursday:** Throwback Thursday (Testimonies & Reflection)
- **Friday:** Fun Friday (Memes, Polls & Lusy Integration)
- **Saturday:** Prayer & Reflection (Support & Prayers)
- **Sunday:** Community Hangout (Live Q&A & Virtual Hangouts)

---

## 🚀 DEVELOPMENT MILESTONES

### Milestone 1: The Foundation (Data & Routing)
- [ ] Ensure `events` and `event_participants` Supabase tables exist.
- [ ] Create `bots/eddy/router.py` to handle basic commands (`/start`, `/help`).
- [ ] Register Eddy's commands in the Telegram sidebar menu.

### Milestone 2: The Autonomous Schedule Engine (Cron Jobs)
- [ ] Install and configure `APScheduler` for background tasks.
- [ ] **The 8:00 PM Pre-Alert:** Ed wakes up 1 hour early every day to post the daily themed announcement with an Inline Keyboard (`[✅ Coming]`).
- [ ] **The 9:00 PM Trigger:** Ed posts the "Starting Now!" message.
- [ ] **Dynamic Logic:** Write logic to automatically detect the *last Wednesday of the month* for the Book Review swap.

### Milestone 3: The RSVP & Attendance Tracker
- [ ] Write Callback Query handlers for the `[✅ Coming]` button.
- [ ] Save RSVPs silently to Supabase (`EventService.register_participant`).
- [ ] Track attendance for points (to feed into Lusy's XP ecosystem later).

### Milestone 4: Ad-Hoc Admin Event Creator (FSM)
- [ ] Create the `/new_event` command (Admin Only).
- [ ] Use a State Machine to ask the Admin: *Title? Date? Time? Description?*
- [ ] Save custom events to Supabase and broadcast them alongside the automated daily schedule.

### Milestone 5: Cross-Bot Integration
- [ ] **Friday Hand-off:** At 9:00 PM on Fridays, Ed triggers Lusy to begin the community games.
- [ ] **Voice Chat Links:** On Tuesdays and Sundays, Ed automatically pins the Voice Chat link to the group.
