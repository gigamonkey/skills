---
name: wip
description: >
  Use this skill when the user says "add to wip: ...", "wip add: ...",
  "what's next in wip", "wip status", "show wip", "dispatch wip",
  "dispatch next wip item", or "{project} wip is done". Manages the
  global WIP.md TODO list at ~/hacks/wip/WIP.md — adding items,
  showing what's next, dispatching items to per-project TODO.md files,
  and marking in-progress items as done.
version: 2.0.0
---

# WIP Skill

Manages the global work-in-progress list at `~/hacks/wip/WIP.md`.

File operations are handled by `~/.claude/skills/wip/wip.py`. All commands
output JSON. Use Bash to invoke it:

```
python3 ~/.claude/skills/wip/wip.py <command> [args]
```

## Determining the current project

Run:
```
python3 ~/.claude/skills/wip/wip.py resolve-project --cwd "$(pwd)"
```
Returns `{"project": "<name>", "home": "<path>"}` or empty strings if no match.

## Commands

### 1. Add to WIP

**Trigger:** "add to wip: ...", "wip add: ..."

1. Determine the target project:
   - If the user specifies a project by name, use that.
   - Otherwise, resolve from cwd.
   - If neither matches, use "Uncategorized".
2. Run:
   ```
   python3 ~/.claude/skills/wip/wip.py add --project <name> --item "<text>"
   ```
3. Copy the item text verbatim. Do not rewrite or refine.
4. Confirm what was added and where.

### 2. What's next in WIP

**Trigger:** "what's next in wip", "wip status", "show wip"

1. Run:
   ```
   python3 ~/.claude/skills/wip/wip.py status [--project <name>]
   ```
   Omit `--project` to show all projects, or pass the current project name.
2. The output has `in_progress`, `next`, and `uncategorized` arrays.
3. Present the results conversationally — show in-progress items first, then
   next items per project, then uncategorized.

### 3. Dispatch WIP item

**Trigger:** "dispatch wip", "dispatch next wip item"

This moves the next item from WIP.md into a per-project TODO.md so the
project's `todos` skill can work on it.

1. Determine the current project (from cwd or user specification).
2. Run:
   ```
   python3 ~/.claude/skills/wip/wip.py dispatch --project <name>
   ```
   This removes the first item from the project section, moves it to
   `## In progress`, and returns `{item, section_hint, project}`.
3. Look up the project's home directory from the dispatch response or
   `list-projects`. Then add the item to the project's TODO.md:
   ```
   python3 ~/.claude/skills/wip/wip.py todo-add \
     --home <project_home> --section "<section_hint>" --item "<item_text>"
   ```
   Omit `--section` if no hint was returned (defaults to first section).
4. Tell the user what was dispatched and where (project, TODO file path, and
   section).

### 4. Mark WIP done

**Trigger:** "{project} wip is done", "wip done for {project}"

1. Run:
   ```
   python3 ~/.claude/skills/wip/wip.py done --project <name>
   ```
2. If the response has `"needs_disambiguation": true`, show the items list
   to the user and ask which one is done. Then re-run with `--index <n>`.
3. If there's an error (no items), tell the user.
4. On success, confirm what was removed.

## Notes

- When adding items, copy the text verbatim. Do not rewrite or refine — the
  user will edit if needed.
- The script handles section cleanup automatically (removing empty project
  sections, preserving `## In progress` and `## Uncategorized`).
