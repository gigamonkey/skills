---
name: todos
description: Use this skill when the user says "do next X todo" where X is a section header in plans/TODO.md (e.g. "do next small todo", "do next medium todo"), or when the user asks "what's next" or "what's next in the TODO list" to show the next unchecked item(s). Finds the first unchecked item under that header and does it.
version: 2.0.0
---

# Do Next Todo Skill

The user wants to work on the first unchecked item in a specific section of
`plans/TODO.md`.

File operations are handled by `~/.claude/skills/wip/wip.py`. Use Bash to
invoke it:

```
python3 ~/.claude/skills/wip/wip.py <command> [args]
```

## Steps

### 1. Find the next item

If the user is asking "what's next" (just wants to see what's available):
```
python3 ~/.claude/skills/wip/wip.py todo-next --home "$(pwd)"
```
This returns `{sections: [{name, item, count}]}` — list the first unchecked
item from each non-empty section and stop.

If the user says "do next X todo" (wants to start working):
```
python3 ~/.claude/skills/wip/wip.py todo-next --home "$(pwd)" --section "<X>"
```
This returns `{file, section, item, instructions}`.

- If `item` is null, tell the user there are no unchecked items in that section.
- If `instructions` is non-empty, these are instructions about how to do work
  in this section. You **must** follow them.

A checklist item includes its checkbox line **and** any continuation lines
indented beneath it. Treat all of those lines as part of the same item.

### 2. Do the work

Carry out whatever the item describes — just as if the user had typed the
request directly. Apply any relevant skills if they match.

If there were section instructions returned in step 1, follow them when doing
the work. You may **not** ignore these instructions.

### 3. Wait for confirmation that you are done

After completing the work in Step 2, **stop and summarize** what you did, then
wait. Do not touch `plans/TODO.md` yet.

The user will tell you when the item is actually done. They may ask for further
changes or make changes themselves. As a reminder:

- If you made a PR, remind the user that items are typically marked done after
  the PR is merged, and ask how they'd like to proceed.
- If you wrote a plan, the item is not done until the user has approved the plan.

Once they tell you the item is done, mark it complete:

```
python3 ~/.claude/skills/wip/wip.py todo-done --home "$(pwd)" --item "<item text>"
```

The `--item` text is matched as a substring against unchecked items. Use enough
of the item text to uniquely identify it.

If the work produced a plan file in `plans/`, add `--plan <filename.md>`:
```
python3 ~/.claude/skills/wip/wip.py todo-done --home "$(pwd)" --item "<item text>" --plan "<filename.md>"
```
This appends a plan link to the done item and adds an "Implement the plan"
item to the `## Plans` section.
