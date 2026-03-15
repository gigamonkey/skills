---
name: do-next-todo
description: Use this skill when the user says "do next X todo" where X is a section header in plans/TODO.md (e.g. "do next small todo", "do next medium todo"). Finds the first unchecked item under that header and does it.
version: 1.0.0
---

# Do Next Todo Skill

The user wants to work on the first unchecked item in a specific section of `plans/TODO.md`.

## Steps

### 1. Read plans/TODO.md

Read the file and find the first `- [ ]` item under the section header matching what the user asked for (e.g. "Small", "Medium", "Large"). The match is case-insensitive. If the user didn't specify a section header, e.g. "do the next todo", then just pick the first `- [ ]` item from the top of the file.

If there are no unchecked items in the named section, tell the user and don't do anything else. Do *not* do items from another section if the user specified a section.

### 2. Do the work

Carry out whatever that item describes — just as if the user had typed the request directly. Apply any relevant skills if they match. For items in the Medium, Large, and Plans sections, do the work in a git worktree.

### 3. Wait for confirmation that you are done

After you think you are done, let the user know. They will tell you when the item is actually done. They may ask for further changes or make changes themself. If you made a PR, the item is not done until the PR is merged. If you wrote a plan, the item is not done until the user has approved the plan.

Once they tell you the item is done you MUST update `plans/TODO.md` as follows:

1. **Move the item**: Remove the item from its current section and append it at the **very end** of the `## Done` section — after all existing `- [x]` entries. The `## Done` section is a chronological log; the most recently completed item must always be last. Do not insert it at the top or middle of `## Done`. When you move it change the checkbox from `- [ ]` to `- [x]`.

2. **If needed, add new item to Plans**: If the work produced a plan file in `plans/`, there are two sub steps you MUST complete:

    1. Append ` (plan: plans/filename.md)` to the end of the original todo item.

    2. Add an unchecked item at the END of the `## Plans` section that says “Implement the plan in plans/…” with the name of the plan file filled in.

The first step is required every time you are told an item is finished. Do not leave a completed item in its original section. And the second step is required if you wrote a plan.
