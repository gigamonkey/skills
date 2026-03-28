---
name: todos
description: Use this skill when the user says "do next todo", "what's next", or "what's next in the TODO list" to show or work on the next item in plans/TODO.md. Finds the next item from ## In progress (resuming) or ## Up next (starting fresh).
version: 3.0.0
---

# Do Next Todo Skill

The user wants to work on the next item in `plans/TODO.md`.

File operations are handled by `~/.claude/skills/wip/wip.py`. Use Bash to
invoke it:

```
python3 ~/.claude/skills/wip/wip.py <command> [args]
```

## Steps

### 1. Find the next item

```
python3 ~/.claude/skills/wip/wip.py todo-next --home "$(pwd)"
```

Interpret the result:

- **`item` is non-null** — move it to `## In progress`:
  ```
  python3 ~/.claude/skills/wip/wip.py todo-start --home "$(pwd)"
  ```
  Then proceed to Step 2 with the item text.

- **`item: null`** — tell the user the queue is empty and stop.

### 2. Do the work

Carry out whatever the item describes — just as if the user had typed the
request directly. Apply any relevant skills if they match.

### 3. Wait for confirmation that you are done

After completing the work in Step 2, **stop and summarize** what you did, then
wait. Do not touch `plans/TODO.md` yet.

The user will tell you when the item is actually done. Notes:

- If you made a PR, remind the user that items are typically marked done after
  the PR is merged, and ask how they'd like to proceed.
- If you wrote a plan, the item is not done until the user has approved the plan.

Once they tell you the item is done, mark it complete:

```
python3 ~/.claude/skills/wip/wip.py todo-done --home "$(pwd)" --item "<item text>"
```

The `--item` text is matched as a substring. Use enough to uniquely identify it.

If the work produced a plan file in `plans/`, add `--plan <filename.md>`:
```
python3 ~/.claude/skills/wip/wip.py todo-done --home "$(pwd)" --item "<item text>" --plan "<filename.md>"
```

If the response has `plan_followup_needed: true`, ask the user where the
"Implement the plan" follow-up should go:

> "Where should 'Implement the plan in plans/X' go?"
> - Local `## Up next` (work on it soon)
> - WIP.md backlog for this project (work on it later)

Then call the appropriate command:
- Local: `python3 ~/.claude/skills/wip/wip.py todo-add --home "$(pwd)" --item "Implement the plan in plans/<filename.md>"`
- WIP: `python3 ~/.claude/skills/wip/wip.py add --project <name> --item "Implement the plan in plans/<filename.md>"`
