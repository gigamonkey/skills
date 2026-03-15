---
name: update-claude-md
description: Use this skill to update CLAUDE.md based on git changes since it was last modified. Triggers when the user asks to "update CLAUDE.md", "sync CLAUDE.md with recent changes", or "refresh the project instructions".
version: 1.0.0
---

# Update CLAUDE.md Skill

This skill reviews recent git changes to the codebase and updates `CLAUDE.md` to reflect anything that is now out of date or missing.

## Steps

### 1. Find when CLAUDE.md was last updated

```bash
git log --oneline -1 -- CLAUDE.md
```

Save the commit hash from this output.

### 2. See what has changed since then

```bash
git log --oneline <last-claude-md-commit>..HEAD
```

Then get a broad view of what files changed:

```bash
git diff --stat <last-claude-md-commit>..HEAD
```

### 3. Examine relevant diffs

For any changed files that might affect CLAUDE.md documentation (architecture, commands, conventions, new modules, config files, dependencies, etc.), read the relevant diffs:

```bash
git diff <last-claude-md-commit>..HEAD -- <path>
```

Focus on:
- `package.json` / `pom.xml` — dependency or script changes
- `Makefile` — new or changed build/dev commands
- `schema.sql` — data model changes
- New or deleted files in `modules/`, `java/src/`, `courses/`, `client-js/`, `markup/`, `lisp/`
- `index.js` — new routes or middleware
- Any new top-level directories

### 4. Identify gaps and outdated content in CLAUDE.md

Read the current `CLAUDE.md` and compare it to what you found. Look for:
- Commands that no longer exist or have changed
- New commands or workflows that aren't documented
- Architecture sections that describe removed or renamed modules
- New modules, directories, or patterns that aren't mentioned
- Outdated descriptions of how things work

### 5. Update CLAUDE.md

Edit `CLAUDE.md` to fix anything that is out of date and add anything meaningful that is missing. Follow these guidelines:

- **Be conservative**: only add things that are genuinely useful for a new contributor or AI assistant to know. Don't document every file.
- **Keep it accurate**: if you're not sure whether something changed, re-read the relevant source files before updating.
- **Match existing style**: follow the heading hierarchy and tone of the existing document.
- **Don't bloat it**: remove outdated content rather than leaving stale notes alongside corrections.

### 6. Summarize what you changed

After editing, briefly describe what you updated and why, so the user can review your reasoning.
