# Susy - Welcome & Music Bot Roadmap

## Core Objective
Susy is the welcoming face and social heartbeat of the **YOUTHOPIA BIBLE COMMUNITY**. While Theo handles the Word, Pete handles Security, and Lusy handles Games, **Susy is responsible for community onboarding, cultural orientation, and music.**

## 1. The Legacy Susy (What We Found)
In the old code, Susy had two main jobs:
1. **The Welcome Committee:** Listened to the `new_chat_members` event and automatically generated a welcome message. (Included `/welcome_on` and `/welcome_off` admin controls).
2. **The DJ:** Hosted Voice Chat music sessions with commands like `/play`, `/queue`, `/skip`, `/pause`, `/resume`, and `/stop`.

## 2. The New Architecture Challenge
In the new **YouThopiaOS**, High King Pete now intercepts `new_chat_members` to enforce a Deep Link CAPTCHA. Because Pete immediately mutes new members to block spam, Susy cannot blindly welcome them into the group at the same time (it would cause a messy overlap).

## 3. The New Implementation Plan

### Phase 1: The Onboarding Guide (Integration with Pete)
* **The Solution:** Susy will act as a beautiful, interactive Welcome Guide in DMs.
* **The Flow:** 
  1. A user joins the group. Pete mutes them and asks them to verify.
  2. The user verifies in Pete's DMs. Pete unlocks them and posts a success message in the group.
  3. We will add a button to Pete's success message (or the group chat) that says: *"Meet your first friend, Susy!"*
  4. When they DM Susy (`/start`), she launches a beautiful **Onboarding Walkthrough**, explaining the community culture, how to use the other bots, and giving them their first Trust Score boost.

### Phase 2: The DJ (Voice Chat Music)
* We will port over her `/play`, `/pause`, and `/skip` capabilities.
* **Technical Note:** Since modern Telegram Voice Chat bots require specific user-bot (Pyrogram/Telethon) integrations or libraries like `pytgcalls`, we will need to rebuild this carefully to run alongside the main `aiogram` loop without blocking it.

## Build Order / Next Steps
- [ ] Create basic bot skeleton in `bots/susy/bot.py` and `bots/susy/router.py`.
- [ ] Connect Susy to `core/telegram_runtime.py` and `main.py` bot arrays.
- [ ] Build the interactive **Welcome Guide Flow** (Welcome, Culture, Rules, Bot Introductions).
- [ ] Wire the shared Supabase `UserService` so Susy can register users and grant them initial XP/Trust Points upon completing orientation.
- [ ] Investigate `pytgcalls` or similar libraries for Phase 2 Music Integration.
