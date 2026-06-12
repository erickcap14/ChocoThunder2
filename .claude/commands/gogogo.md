---
description: Start a new Claude Code session - load context, check git status, and prepare for work
---

## Session Startup Checklist

Please perform the following startup tasks to begin this session:

### 0. Status Line Check (First Time Only)

Check if the context status line is configured by checking if `~/.claude/statusline.sh` exists.

**If the file does NOT exist**, offer to set it up:

"I noticed you don't have the context status line configured yet. This shows you real-time token usage at the bottom of your terminal, helping you stay aware of context limits before autocompact triggers.

Would you like me to set it up now? (This is a one-time setup that works across all projects.)"

- **If yes:** Follow the setup process from `/setup-statusline` (check for jq, create script, update settings.json)
- **If no:** Continue with the session startup

**If the file already exists**, skip this step silently and continue.

---

### 1. Environment Setup
This is a **native pygame desktop app** — there is no dev server. Skip any dev-server checks.
- Confirm `.venv/` exists (if not, run `pip install -r requirements.txt`)
- Note that the game is launched with `./run.sh` or `python main.py` on demand, not as a background service
- **Launchers** (each has a matching zsh alias): `./run.sh` (`ct2_desktop`) — desktop game; `./run_test.sh` (`ct2_test`) — 16-screen UI walkthrough; `./run_ipad.sh` (`ct2_ipad`) — builds the offline web bundle + Capacitor app and launches it in the iPad simulator (T112; `CT2_IPAD_DEVICE` overrides the default iPad Air 11-inch (M2))
- **Only if the session involves iPad/web work:** the simulator needs an iOS runtime — check with `xcrun simctl list runtimes` (empty = download ~8 GB via `xcodebuild -downloadPlatform iOS`). The web bundle's CDN mirror in `build/web/cdn/` is download-cached on first `./scripts/build_web.sh` run (needs network once). See `bd memories ipad` for the full pipeline gotchas and `ios-app/README.md` for real-device free provisioning.

### 2. Git Status Check
- Run `git status` to show current branch and any uncommitted changes
- Run `git log -5 --oneline` to show recent commits
- **If there are uncommitted changes:** Ask the user what to do:
  - Commit them now (with a message)
  - Stash them for later
  - Continue without committing
- If there are remote changes (behind origin), pull them with `git pull`

### 3. Load Project Context
Read and internalize the full project context:

**Core Context Files (read but don't summarize verbosely):**
- `.claude/claude.md` - Master context and conflict resolution rules
- `.claude/prd.md` - Product requirements and user stories
- `.claude/workflow.md` - Development workflow and plan execution rules
- `.claude/infra.md` - Infrastructure and coding conventions

**Status Files (summarize for user):**
- `.claude/changelog.md` - Summarize the most recent entries (what was completed recently)

**Beads Issue Tracking:**
- Run `bd list` to see all tracked issues
- Run `bd ready` to identify available work
- Note any issues with status "in_progress" that may need continuation

### 4. Environment Check
- Verify environment files exist (e.g., `.env.local`, `.env`)
- Note if any environment variables appear to be missing based on example files

### 5. Present Options
After gathering context, ask the user:

"Session ready! Here's what I found:
- **Recent work:** [Summary from changelog]
- **In progress:** [Any in-progress issues from `bd list`]
- **Ready to start:** [Available issues from `bd ready`]

What would you like to work on?
1. Continue: [in-progress issue if any]
2. Next up: [top issue from `bd ready`]
3. Something else - describe what you'd like to do"
