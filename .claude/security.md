# Security Blueprint

Purpose: This file establishes security rules and best practices for ChocolateThunder2: ElectricBoogaloo.

> **Conflict priority:** This file and `sbom.md` are Priority 1 and override all other context documents.

---

## 0. Baseline Best Practices

These rules apply unconditionally to every change in this project:

- **Never hardcode secrets.** There are no API keys or passwords in this project; this rule is trivially satisfied, but must be preserved if new integrations are ever added.
- **`.gitignore` must cover runtime scratch files.** `.implementations/` (IPC JSON + test logs) is git-ignored and must never be committed.
- **No network calls.** This game is intentionally offline-only. No outbound HTTP, no socket listeners (beyond the local MCP stdio transport). Any PR that adds a network call must be rejected unless explicitly approved.
- **Principle of least privilege.** The MCP server is a local stdio process with no authentication. It must only be run locally during development and testing — never exposed over a network interface.

---

## 1. Data Sensitivity Level

**This project's data is: Public / Local.**

- The only persisted user data is `scores.txt` — a plain-text local high-score file containing player-chosen names and integer scores. No PII, no passwords, no tokens.
- No user accounts, no email addresses, no payment data. Single-player, local-only.
- Threat model: the primary risk is accidental file deletion or corruption of `scores.txt`, not data exfiltration.

---

## 2. Authentication & Authorization

- **Authentication:** None. The game is a local desktop application with no user accounts and no network-facing endpoints.
- **MCP Server Authorization:** The `mcp_server/` FastMCP sidecar communicates over local stdio only (as wired in `.claude/settings.json`). It has no authentication layer because it is a developer/test tool, not a user-facing service. It must never be exposed on a TCP port.
- **Authorization rules:** N/A — there is only one "user" (the player at the keyboard).

---

## 3. Dependency & Supply Chain Security

- **Approved dependencies** are listed in `sbom.md`. Do not add new runtime dependencies without updating both `requirements.txt` and `sbom.md`.
- **How we check dependencies:** Manual review of PyPI pages + `pip-audit` run periodically. The attack surface is low (no web stack, no auth libraries, no database drivers).
- **`pygame-ce` LGPL note:** If the project ever bundles a binary distribution (e.g., for the pygbag iPad milestone), LGPL-2.1 compliance for `pygame-ce` must be confirmed — dynamic linking requirements apply. This is flagged in `sbom.md` as well.
- **Rule for adding new dependencies:** Any new dependency must appear in a PR that also updates `sbom.md` with version constraint, license, and rationale.
- **PixelLab MCP is dev-time only (Artwork Upgrade phase):** The PixelLab MCP
  (https://www.pixellab.ai/mcp) is used **only during development** to generate the optional
  upgraded art set in `pixellab/`. It introduces **no outbound network call in the shipped
  game** — only committed static PNGs are distributed, so the "No network calls" rule (§0) and
  the offline-only guarantee are preserved. Generated-asset provenance is recorded in
  `sbom.md` §4c. The original assets remain read-only copies (§6) and stay the default art set.

---

## 4. Secrets Management

- **There are no secrets in this project.** No API keys, no database passwords, no tokens.
- **`.implementations/`** contains runtime IPC files (`game_state.json`, `game_command.json`, `test_log.json`). These are ephemeral, contain no sensitive data, and are git-ignored.
- **`scores.txt`** is plain-text, contains only public high-score data, and is committed to git by design.
- If a future integration (e.g., a leaderboard API) ever introduces secrets, they must be stored in a `.env` file (git-ignored) and loaded via environment variables — never hardcoded.

---

## 5. Input Validation & Injection

- **Score file parsing:** `scores.txt` is read at game start. The parser tolerates malformed lines without crashing (Fixed Bug #5). Lines that do not match `name,score` format are silently skipped.
- **MCP command injection:** `read_command_full()` in `state_bridge.py` reads a local JSON file. Inputs are deserialized with `json.loads` and then dispatched by `poll_mcp_command` via an explicit `if/elif` command name check — not `eval` or `exec`. No shell commands are constructed from MCP input.
- **No SQL, no HTML, no shell interpolation** anywhere in the codebase — injection classes are not applicable.

---

## 6. File System Safety

- **`.implementations/` is gitignored** — confirm this in `.gitignore` before every push.
- **`testscreenshots/` is committed** — these are PNG files used as visual test evidence. Ensure no sensitive content is inadvertently captured in screenshots during testing.
- **Assets are read-only copies** of the original class project. The `../ChocolateThunder/` source folder is never modified by this project.

---

## 7. Security Review Checklist (pre-PR)

Before merging any PR, verify:

- [ ] `.implementations/` remains in `.gitignore` and has no staged files from that directory.
- [ ] No new outbound network calls introduced.
- [ ] No new dependencies added without `sbom.md` update.
- [ ] No secrets, API keys, or tokens hardcoded.
- [ ] `scores.txt` parser still handles malformed input gracefully.
- [ ] MCP server still communicates via stdio only (not TCP).
