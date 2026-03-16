---
name: todos
description: Use this skill when the user says "do next X todo" where X is a section header in plans/TODO.md (e.g. "do next small todo", "do next medium todo"). Finds the first unchecked item under that header and does it.
version: 1.0.0
---

# Do Next Todo Skill

The user wants to work on the first unchecked item in a specific section of
`plans/TODO.md`.

## Steps

### 1. Read TODO.md

It will either be in the root directory or under `plans/`. If they both exist
prefer the one in `plans/`.

**Always read TODO.md fresh using the Read tool before selecting an item.** Do
not rely on any previously seen version of the file — it may have been updated
since the last time you read it. The correct item to work on is determined by
the file's current contents at the moment you read it.

Read the file and find the first `- [ ]` item under the section header matching
what the user asked for (e.g. "Small", "Medium", "Large"). The match is
case-insensitive. If the user didn't specify a section header, e.g. "do the next
todo", then just pick the first `- [ ]` item from the top of the file.

If there are no unchecked items in the named section, tell the user and don't do
anything else. Do *not* do items from another section if the user specified a
section.

### 2. Do the work

Carry out whatever that item describes — just as if the user had typed the
request directly. Apply any relevant skills if they match.

If there is text in the section before the list of items, it is instructions
about how to do the work. Follow these when doing the work. You may **not**
ignore these intructions.

### 3. Wait for confirmation that you are done

Unless the per-section instructions told you you could mark an item complete on
your own, After you think you are done, let the user know. They will tell you
when the item is actually done. They may ask for further changes or make changes
themself. If you made a PR, the item is not done until the PR is merged. If you
wrote a plan, the item is not done until the user has approved the plan.

Once they tell you the item is done you MUST update `plans/TODO.md` as follows:

1. **Move the item**: Remove the item from its current section and add it to the
   `## Done` section. Read the text at the beginning of the `## Done` section to
   find out where in the list you should put the newly completed item. When you
   move it change the checkbox from `- [ ]` to `- [x]`.

2. **If needed, add new item to Plans**: If the work produced a plan file in
   `plans/`, there are two sub steps you MUST complete:

    1. Append ` (plan: [filename](plans/filename.md))` to the end of the
       original todo item.

    2. Add an unchecked item at the END of the `## Plans` section that says
       “Implement the plan in plans/…” with the name of the plan file filled in
       and linked.

The first step is required every time you are told an item is finished. Do not
leave a completed item in its original section. And the second step is required
if you wrote a plan.
