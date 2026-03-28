---
name: wip
description: >
  Use this skill when the user says "add to wip: ...", "wip add: ...",
  "what's next in wip", "wip status", "show wip", "dispatch wip",
  or "dispatch next wip item". Manages the global WIP.md TODO list
  at ~/hacks/wip/WIP.md — adding items, showing what's next, and
  dispatching items to per-project TODO.md files.
version: 1.0.0
---

# WIP Skill

Manages the global work-in-progress list at `~/hacks/wip/WIP.md`.

## WIP.md Structure

WIP.md contains:

1. A projects table (no heading) mapping project names to descriptions and home
   directories.
2. `## {project}` sections containing bullet items for each project.
3. A `## Uncategorized` section at the bottom for items not tied to any
   project.

Items that have been dispatched to a per-project TODO are annotated with
` → dispatched` at the end of the line.

## Determining the current project

Match the current working directory against the `home` column of the projects
table in WIP.md. If the cwd is within a project's home directory (after
expanding `~`), that's the current project. If no match, the project is
unknown.

## Commands

### 1. Add to WIP

**Trigger:** "add to wip: ...", "wip add: ..."

1. Read `~/hacks/wip/WIP.md`.
2. Determine the target project:
   - If the user specifies a project by name (e.g., "add to wip for bhs-cs:
     ..."), use that project.
   - Otherwise, use the current project based on cwd.
   - If neither matches, use "Uncategorized".
3. Find the target section:
   - For a named project: find `## {project}`. If the section doesn't exist,
     create it before `## Uncategorized`.
   - For Uncategorized: find or create `## Uncategorized` at the bottom of the
     file.
4. Append the item as a `- ` bullet at the end of that section (before the
   next section heading).
5. Confirm what was added and where.

### 2. What's next in WIP

**Trigger:** "what's next in wip", "wip status", "show wip"

1. Read `~/hacks/wip/WIP.md`.
2. For the current project (or all projects if not in a project directory, or
   if the user asks for all), show the first non-dispatched item from each
   project section.
3. If there are items in Uncategorized, mention those too.

### 3. Dispatch WIP item

**Trigger:** "dispatch wip", "dispatch next wip item"

This moves the next item from WIP.md into a per-project TODO.md so the
project's `todos` skill can work on it.

1. Read `~/hacks/wip/WIP.md`.
2. Determine the current project from cwd (or the user can specify one).
3. Find the first non-dispatched item (i.e., a line starting with `- ` that
   does NOT end with `→ dispatched`) in that project's section.
4. Parse the item text for a section hint:
   - If the item ends with a section name in parentheses, e.g.,
     `Add foo endpoint (medium)`, strip the `(medium)` part and use "medium"
     as the target section name in the project's TODO.md.
   - Otherwise, the item goes into the **first section** of the project's
     TODO.md (see below).
5. Look up the project's home directory from the Projects table.
6. Read the project's TODO.md: prefer `{home}/plans/TODO.md`, fall back to
   `{home}/TODO.md`. If neither exists, create `{home}/plans/TODO.md` with a
   basic structure.
7. Find the target section in the project's TODO.md:
   - If a section hint was provided: find the first `## ` heading whose text
     matches the hint case-insensitively (after stripping `#` and whitespace).
   - If no hint: use the **first `##` heading** in the file.
   - Append `- [ ] {item text}` at the end of that section (before the next
     `## ` heading).
8. In WIP.md, annotate the original item by appending ` → dispatched` to its
   line.
9. Tell the user what was dispatched and where (project, TODO file path, and
   section).

## Notes

- Always read WIP.md fresh before any operation. Do not rely on a cached
  version.
- When adding items, copy the text verbatim (minus any section hint in
  parens). Do not rewrite or refine — the user will edit if needed.
- Multi-line items: a bullet includes its line and any continuation lines
  indented beneath it. Treat all as one item.
- The user removes completed items from WIP.md manually.
- After any operation that modifies WIP.md (add, dispatch), check for `##`
  project sections that have no items under them (empty or only blank lines
  before the next heading/EOF). Remove those empty sections. Do not remove
  `## Uncategorized` even if empty.
