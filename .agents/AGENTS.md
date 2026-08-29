# Rules

- Always provide a git commit message with the exact command to run after making any file changes.

## Interactive Learning & Co-Building Operating Rules

1. **Zero Code Without Prior Deep Theoretical Alignment:**
   - NEVER create or modify files until the user explicitly approves after receiving a complete, foundational, theoretical explanation.
   - Every single concept (HTML, CSS, JS, TypeScript, React, Vite, Webhooks, FastAPI, Telegram SDK) must be explained from first principles: *what it is*, *why it is needed*, *tradeoffs*, and *how it connects to the full architecture*.

2. **Concept First, Architecture & Tradeoffs Second, Code Last:**
   - Explain the computer science theory, design decisions, alternative choices, and potential pitfalls before proposing any code edits.

3. **Step-by-Step Modular Building:**
   - Never perform monolithic code dumps. Break features down into small, digestible, 20-50 line steps.
   - Walk through *what* is being built, *why* it is needed, and *how* each line functions.

4. **Mastery & Verification Checkpoints:**
   - At the end of each module, explain how to test, run, and inspect the code to ensure full comprehension before moving to the next step.

5. **Preserve Architectural Integrity:**
   - Maintain Supabase as the single structured source of truth.
   - Keep Telegram bots and Mini App cleanly decoupled.
   - Enforce strict TypeScript typing and clean React component patterns.

