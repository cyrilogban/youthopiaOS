# Lusy: Community Games & Engagement Roadmap

**Mission:** Make learning God's Word and participating in the community fun and rewarding. Lusy is not just a "Bible quiz bot," she is the community's entertainment and gamification engine.

## Core Philosophy: The Game Platform
The game logic stays in Python. The content stays in Supabase.
This separation makes the system infinitely scalable.

---

## Phase 1: The Foundation (Currently Active)
- [x] **User System:** Telegram ID, Username, XP, Level (Stored in Supabase via OS)
- [x] **Universal Game Engine:** Generic flow (`lusy_questions` and `lusy_game_history` tables)
- [x] **XP Engine:** Shared XP calculation (`shared.services.xp`)
- [x] **Core Game Type:** Multiple Choice Bible Quiz Engine using Telegram Native Polls
- [x] **Dashboard:** Persistent 4-button menu (`Play Games`, `Leaderboard`, `My YP & Stats`, `About Lusy`)

## Phase 2: Expanding Game Types
- [ ] **Verse Completion:** "Complete this verse: For God so loved the ________"
- [ ] **Emoji Bible Puzzle:** 👑🦁 -> Daniel
- [ ] **True or False:** Statement -> True/False -> Explanation
- [ ] **Bible Character Guess:** "I built a huge ark." -> Noah
- [ ] **Guess the Miracle / Parable**

## Phase 3: Community & Competition
- [ ] **Top 10 Leaderboard:** Render a visually appealing leaderboard of top YouTopians.
- [ ] **Team Competitions:** Split members into teams (Team Paul, Team Esther).
- [ ] **Fastest Finger:** Bot posts a question in the main group, first correct answer gets 50 YP.

## Phase 4: Daily Challenges & Streaks
- [ ] **Daily Challenge:** E.g., Read Psalm 23, Memorize a verse, Pray for 5 minutes.
- [ ] **Streak System:** 7-day, 30-day, 100-day streaks for participation.
- [ ] **Memory Verse Challenge:** Bot sends a verse, hours later asks the user to type it from memory.

## Phase 5: Achievements & Economy
- [ ] **Trophies:** 🏆 Bible Scholar, 🏆 Quiz Master, 🏆 Prayer Warrior, 🏆 Community Champion
- [ ] **XP Economy Integration:** Earn YP for attending events, daily logins, reading challenges.

## Phase 6: Future Capabilities
- [ ] **Admin Dashboard:** Command (`/add_question`) or UI for Admins to add questions to Supabase without code.
- [ ] **Bible Crossword & Word Search:** Advanced visual puzzles.
- [ ] **Seasonal Events:** Christmas Quiz Week, Easter Challenge, Bible Marathon.
