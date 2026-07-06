# Pete - Moderation & Security Bot (Roadmap)

*This document outlines the strategic plan to port "High King Peter" from a standalone moderation bot into a fully integrated security module within YouThopiaOS.*

---

## 🛡️ Vision & Core Mandate
In YouThopiaOS, Pete is the silent guardian of the community. His role is to protect the spiritual atmosphere of the official groups by enforcing rules, filtering spam, locking chats for Bible Study, and issuing automated justice to bad actors. 

Because he is now part of the **YouThopiaOS Hub**, Pete's actions will have ecosystem-wide consequences (e.g., if Pete bans a user for spamming, that user's Trust Score drops globally, affecting how Susy and Eddy interact with them).

---

## 🏗️ Phase 1: The Hub Merger & Core Admin Commands
*Status: Pending*

**Goal:** Establish Pete's fundamental presence in the OS and give group administrators their manual moderation tools back.

- [ ] **Unified Database Mapping:** Ensure Pete reads from the centralized `users`, `groups`, and `chat_members` tables instead of isolated local databases.
- [ ] **Admin Authentication:** Implement a robust `isAdmin` service to verify Telegram rank before allowing command execution.
- [ ] **Manual Justice Commands:** 
  - `/warn <user> <reason>`
  - `/kick <user>`
  - `/ban <user>`
  - `/unban <user>`
  - `/mute <user> <duration>`
  - `/unmute <user>`
- [ ] **Chat Flow Control:** 
  - `/lock` and `/unlock` (Standard group lockdown).
  - `/biblestudy` (Specialized lock mode specifically designed to silence the chat while a teacher is ministering).

---

## ⚔️ Phase 2: The Automated Justice Engine
*Status: Pending*

**Goal:** Enable Pete to moderate the community passively 24/7 without requiring manual admin intervention.

- [ ] **Word Banishment Filter:** An active listener that intercepts and deletes messages containing forbidden language or inappropriate content.
- [ ] **Spam & Flood Detection:**
  - Detect rapid-fire messaging (Flood attack).
  - Detect highly repetitive copy-paste text.
  - Automatically delete unauthorized Telegram/WhatsApp invite links.
- [ ] **The Warning Threshold:** 
  - Log warnings globally in a `moderation_logs` table.
  - Implement automated penalties (e.g., 3 Warnings = 1 Hour Mute, 5 Warnings = Ban).

---

## 🏰 Phase 3: Perimeter Defense & Security
*Status: Pending*

**Goal:** Secure the borders of the YouThopia community against bot raids and fake accounts.

- [ ] **The Welcome Decree (Anti-Bot Captcha):** 
  - When a new user joins an official group, Pete instantly restricts their typing permissions.
  - Pete drops an inline button challenge (e.g., "Tap here to verify you are human").
  - Upon clicking, Pete restores their permissions and deletes the challenge message to keep the chat clean.
- [ ] **Global Trust Score Integration:**
  - Link Pete's warning system to the global `engagement_level` and `trust_score` mechanics in `UserService`.

---

**SHARING GOD'S LOVE ALL THE WAY 💜**
