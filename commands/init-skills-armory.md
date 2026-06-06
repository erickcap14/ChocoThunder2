---
description: Create a standalone my-skills-armory repository in the project parent directory, scaffold it for Claude Code skills, and prepare it to push to GitHub.
---

# Init Skills Armory

Create a `my-skills-armory` repository one level above the current project. This becomes a portable, GitHub-ready collection of your custom Claude Code skills.

---

## Instructions

### Step 1: Resolve Paths

Determine the parent directory of the current working directory. The armory will be created at `<parent>/my-skills-armory`.

Example: if the current project is at `/Users/alice/Projects/my-app`, the armory goes at `/Users/alice/Projects/my-skills-armory`.

---

### Step 2: Check for Existing Armory

Check if `<parent>/my-skills-armory` already exists:

```bash
test -d <parent>/my-skills-armory
```

**If it exists:** skip Steps 2 and 3 entirely. Tell the user the armory already exists and you're working with it. Jump straight to Step 4 (offer to copy skills).

**If it does not exist:** create it and continue with Step 3.

```bash
mkdir -p <parent>/my-skills-armory
```

---

### Step 3: Scaffold the Structure

Create the following files and directories inside `my-skills-armory/`:

#### `README.md`
```markdown
# My Skills Armory

A personal collection of custom [Claude Code](https://claude.ai/code) skills and slash commands.

## Structure

- `skills/` — Skill definition files (`.md`). Each file is a slash command.

## How to Use

Install a skill into Claude Code by copying a file from `skills/` to:
- **Global** (all projects): `~/.claude/skills/<skill-name>.md`
- **Project-only**: `.claude/commands/<skill-name>.md`

## Adding a New Skill

1. Create `skills/<my-skill>.md` with a `description:` frontmatter field.
2. Write the instructions Claude should follow when the skill is invoked.
3. Commit and push.
```

#### `.gitignore`
```
.DS_Store
*.local
```

#### `skills/` directory
Create an empty `skills/` directory with a `.gitkeep` placeholder so it commits cleanly.

---

### Step 4: Offer to Copy Existing Skills

Ask the user:
> "Would you like to copy your existing skills from this project into the armory? I can copy all `.md` files from `commands/` here."

If yes, copy all `.md` files from the current project's `commands/` directory into `my-skills-armory/skills/`, skipping any that are project-specific scaffolding (like `bootstrap.md` and `convert.md`). For each file copied, tell the user its name.

If no, skip this step.

---

### Step 5: Git Init and Commit

Check if `.git` already exists inside the armory:

```bash
test -d <parent>/my-skills-armory/.git
```

**If `.git` exists:** skip `git init`. Just stage and commit any new files added in Step 4:
```bash
cd <parent>/my-skills-armory
git add .
git commit -m "feat: add skills from <project-name>" 2>/dev/null || echo "nothing new to commit"
```

**If `.git` does not exist:** initialize and make the first commit:
```bash
cd <parent>/my-skills-armory
git init && git branch -m master main
git add .
git commit -m "chore: initialize skills armory"
```

---

### Step 6: GitHub Setup Instructions

Tell the user:

> **Your skills armory is ready at:** `<parent>/my-skills-armory`
>
> **To push to GitHub:**
>
> 1. Create a new repo at [github.com/new](https://github.com/new). Name it `my-skills-armory`. Set visibility (public = shareable with others, private = personal only).
> 2. Back in your terminal, run:
>    ```bash
>    cd <parent>/my-skills-armory
>    git remote add origin git@github.com:<your-username>/my-skills-armory.git
>    git push -u origin main
>    ```
>
> **To add a new skill going forward:**
> ```bash
> # Copy your skill file in
> cp ~/.claude/skills/my-skill.md my-skills-armory/skills/
> cd my-skills-armory && git add . && git commit -m "feat: add my-skill" && git push
> ```

---

### Completion

Confirm:
- Directory created: ✓
- Files scaffolded: ✓
- Git initialized with initial commit: ✓
- Skills copied (if requested): ✓

Remind the user they can invoke `/init-skills-armory` again in a different project to check if the armory already exists and offer to sync new skills into it.
