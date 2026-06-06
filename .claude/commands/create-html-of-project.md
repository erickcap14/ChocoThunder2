---
description: Generate a self-contained HTML overview of this project from its file structure and .claude context files
---

# Create HTML Overview of Project

You are generating a single, self-contained HTML overview page for THIS project — the one this command is being run inside. The project may have been forked or bootstrapped from the Claude Code Starter Kit, but you must describe the ACTUAL project as it exists right now, based on its real files. Do not assume anything that the files do not say.

Be resilient throughout. If the project has no `.claude/` folder at all, still build the HTML from whatever exists (README, file structure) and clearly note which context files were missing. Never fail or refuse just because an expected file is absent — note it as "not present" and move on.

Work through the following steps in order.

## 1. Gather the project's context

Read whichever of these files exist (use the project root as your base). Read silently — do not dump full contents to the user.

- `.claude/claude.md` — master context and conflict resolution rules
- `.claude/prd.md` — product requirements and user stories
- `.claude/workflow.md` — development workflow
- `.claude/infra.md` — infrastructure, tech stack, coding standards
- `.claude/security.md` — security requirements
- `.claude/sbom.md` — software bill of materials / dependencies
- `.claude/tests.md` — testing approach
- `.claude/changelog.md` — version history
- `README.md` (project root) — if present

For each expected file, track whether it was found or "not present" so you can report this accurately in the HTML.

## 2. Map the file structure

Build an accurate picture of the project's layout. Prefer a git-aware listing, falling back to a filesystem scan:

```bash
git ls-files 2>/dev/null || find . -type f -not -path './.git/*' -not -path './node_modules/*'
```

Exclude noise: `.git/`, `node_modules/`, build/`dist`/`build`/`out` output directories, and large lock files (e.g. `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `Cargo.lock`). Do NOT dump thousands of files into the page. Instead, render a readable directory tree of the meaningful structure, summarizing or collapsing very large or deeply-nested directories (e.g. "... (N more files)").

## 3. Pull key facts from the docs

Summarize — quote sparingly, only when the exact wording matters.

- From `prd.md`: the project name, a one-sentence summary, who it is for, what the project will NOT do (non-goals), and the feature user stories.
- From `claude.md`: the list of required context files and the Conflict Resolution Matrix (the precedence order).
- From `infra.md`: the tech stack and architecture.
- From `workflow.md`: how the team works (session flow, issue tracking, etc.).

If a given doc is missing, note that the corresponding section is unavailable rather than inventing content.

## 4. Check beads (if present)

If a `.beads/` directory exists AND the `bd` command is available, capture a short backlog snapshot:

```bash
bd list
bd ready
```

Include a concise summary in the HTML (counts and a few representative items). If `.beads/` is absent or `bd` is not installed, skip this section gracefully and note it as not available.

## 5. Generate the HTML

Produce a SINGLE self-contained HTML file at the project root.

**Filename:** Slugify the project name from the PRD (lowercase, spaces and non-alphanumerics to hyphens) and append `-overview.html` — e.g. `my-cool-app-overview.html`. If no project name can be determined, fall back to `project-overview.html`.

**Hard requirements for the generated HTML:**

- Fully self-contained and works offline. ALL CSS lives in a single `<style>` tag in the `<head>`. No external stylesheets, no CDN links, no web fonts fetched over the network, no external images. Optional small amounts of vanilla JavaScript are allowed ONLY for nice-to-haves like table-of-contents scroll highlighting or copy-to-clipboard buttons — never required for the page to render or read.
- Clean, modern, professional documentation styling: a header/hero showing the project name and the one-sentence summary, a table of contents / nav (sidebar or top nav with in-page anchor links), styled code blocks (monospaced, padded, with a subtle background), and styled tables (borders, header row styling, zebra striping is fine).
- Responsive enough to read on a laptop; sensible max content width.
- **Escape all HTML-special characters** (`&`, `<`, `>`, `"`) taken from file contents before injecting them into the page, so the page renders correctly and is not broken or XSS-prone by file content. This is critical for the file tree and any quoted markdown.

**Required sections (in this order):**

a. **Overview** — what the project is and who it is for (from the PRD summary, audience, and non-goals).
b. **File Structure** — the directory tree rendered inside a styled `<pre>` block.
c. **Context Files** — a styled table listing each `.claude/` markdown context file, whether it is present, and a one-line description of its purpose.
d. **Features / User Stories** — the user stories pulled from the PRD.
e. **Tech Stack & Architecture** — summarized from `infra.md`.
f. **Workflow** — summarized from `workflow.md`.
g. **Conflict Resolution Matrix** — the precedence order from `claude.md`, rendered as a styled table.
h. **Backlog Snapshot** — the beads `bd list` / `bd ready` summary, only if available (otherwise omit or note as not available).
i. **Footer** — a note that the page was generated by the `/create-html-of-project` command, including the current date.

Write the file using your file-writing tool. Do not open a browser or attempt to render it.

## 6. Report back to the user

After writing the file, tell the user:

- The exact filename and path that was created.
- How to open it, e.g. on macOS: `open <file>` (mention `xdg-open <file>` on Linux or just double-clicking).
- A one-line note of which context files were present vs. missing, so they understand how complete the overview is.
