---
name: wip
description: >
  Use this skill when the user says "add to wip: ...", "wip add: ...",
  "what's next in wip", "wip status", "show wip", "dispatch wip",
  "dispatch next wip item", "{project} wip is done", or "check wip
  progress" / "sync wip done". Manages the global WIP.md TODO list at
  ~/hacks/wip/WIP.md — adding items, showing what's next, dispatching
  items to per-project TODO.md files, marking in-progress items as
  done, and syncing completed items from per-project TODOs.
version: 2.1.0
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
     --home <project_home> --item "<item_text>"
   ```
   This always adds to `## Up next` (creating it if needed).
4. Tell the user what was dispatched and where (project, TODO file path).

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

### 5. Check progress

**Trigger:** "check wip progress", "sync wip done", "clear done wip items"

1. Run:
   ```
   python3 ~/.claude/skills/wip/wip.py check-progress
   ```
2. The output has `clearable` (items whose text matches a `[x]` done item in
   the project's TODO.md) and `unresolved` (items that couldn't be checked,
   with a reason).
3. If there are clearable items, show them to the user with the matched TODO
   done item for confirmation.
4. For each confirmed item, remove it from `## In progress`:
   ```
   python3 ~/.claude/skills/wip/wip.py done --project <name>
   ```
   If multiple in-progress items exist for the same project, use `--index`.
5. Report what was cleared and mention any unresolved items.

## Notes

- When adding items, copy the text verbatim. Do not rewrite or refine — the
  user will edit if needed.
- The script handles section cleanup automatically (removing empty project
  sections, preserving `## In progress` and `## Uncategorized`).
