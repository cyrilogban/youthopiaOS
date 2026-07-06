# Lusy Progress Tracker

This document tracks the active development of Lusy's Game Engine and Dashboard.

## Milestone 1: The Foundation & Dashboard
- [x] Configure `bot.py` and register base commands (`/start`, `/help`, `/yp`)
- [x] Build 4-Button Persistent DM Dashboard (`Play Games`, `Leaderboard`, `My YP & Stats`, `About Lusy`)
- [x] Create `About Lusy` logic and cross-bot ecosystem links (Theo, Pete, Eddy, Susy)
- [x] Implement `/yp` and `My YP & Stats` to pull profile level and total XP from Supabase
- [x] Rebrand global frontend terminology from "XP" to "YP" (YouTopian Points)

## Milestone 2: Universal Game Engine (Supabase)
- [x] Design universal schema `lusy_questions` to hold JSON payloads for any game type
- [x] Design `lusy_game_history` to track answers, prevent repeats, and feed leaderboard
- [x] Generate and execute SQL Migration (`005_lusy_games.sql`)
- [x] Create local Python seeder script to easily inject questions into Supabase
- [x] Secure local seed scripts by ignoring them in Git (`seed_*.py` in `.gitignore`)

## Milestone 3: Game Implementation (Bible Quiz)
- [x] Build `quizzes.py` router
- [x] Connect `Play Games` button to game mode selector
- [x] Build Multiple Choice Quiz Engine using Telegram Native Polls
- [x] Map Poll Answer callbacks to verify correctness and award YP securely
- [x] Prevent double-XP cheating by saving active poll state to `bot_user_state`
- [x] Build Competitive Group Quiz engine (locking, in-memory voting, timeout closure, summary cards, and winner podium display)
- [x] Implement difficulty-based native poll timers (easy: 60s, medium: 30s, hard: 20s) with native lock expiration (both DMs and groups) to prevent cheating

## Milestone 4: Next Immediate Tasks
- [x] Implement `[ 🏆 Leaderboard ]` button to fetch Top 10 YouTopians from DB
- [x] Build second game type: Verse Completion (Fill-in-the-Blank) fully integrated with the native poll engine and timers
- [x] Build third game type: Trivia Race (Speed Round) using real-time inline buttons, elimination lockout, reaction speed calculation, and group/solo support

---
*Note: This file is ignored by Git and stays completely local for the development team.*
