#!/usr/bin/env python3
"""CLI for manipulating ~/hacks/wip/WIP.md deterministically.

All commands output JSON to stdout. Mutating commands auto-clean empty sections.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

WIP_PATH = Path.home() / "hacks" / "wip" / "WIP.md"

# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def read_wip():
    return WIP_PATH.read_text()


def write_wip(text):
    WIP_PATH.write_text(text)


def parse_projects_table(text):
    """Return list of {name, description, home} from the markdown table."""
    projects = []
    in_table = False
    for line in text.splitlines():
        if line.startswith("|") and "project" in line.lower() and "home" in line.lower():
            in_table = True
            continue
        if in_table and line.startswith("|"):
            if set(line.replace("|", "").strip()) <= {"-", " "}:
                continue  # separator row
            cols = [c.strip() for c in line.split("|")]
            # split gives ['', col1, col2, col3, '']
            cols = [c for c in cols if c is not None]
            # filter empties from leading/trailing |
            cols = line.split("|")
            cols = [c.strip() for c in cols[1:-1]]  # drop first/last empty
            if len(cols) >= 3 and cols[0]:  # skip empty sentinel row
                projects.append({
                    "name": cols[0],
                    "description": cols[1],
                    "home": cols[2],
                })
        elif in_table and not line.startswith("|"):
            break
    return projects


def find_sections(text):
    """Return list of (heading_text, start_idx, end_idx) for ## headings."""
    sections = []
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        m = re.match(r"^## (.+)$", lines[i].rstrip())
        if m:
            start = sum(len(l) for l in lines[:i])
            sections.append((m.group(1).strip(), start, i))
        i += 1
    # set end positions
    result = []
    for idx, (heading, char_start, line_idx) in enumerate(sections):
        if idx + 1 < len(sections):
            char_end = sections[idx + 1][1]
        else:
            char_end = len(text)
        result.append((heading, char_start, char_end, line_idx))
    return result


def get_section_content(text, heading):
    """Return (start, end, content) for a ## heading, or None."""
    for h, start, end, _ in find_sections(text):
        if h == heading:
            # content starts after the heading line
            heading_end = text.index("\n", start) + 1
            return heading_end, end, text[heading_end:end]
    return None


def parse_items(content):
    """Parse bullet items from section content. Returns list of (text, start_offset, end_offset)."""
    items = []
    lines = content.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        if lines[i].startswith("- "):
            item_start = sum(len(l) for l in lines[:i])
            item_lines = [lines[i]]
            j = i + 1
            # continuation lines are indented
            while j < len(lines) and lines[j].startswith("  ") and not lines[j].startswith("- "):
                item_lines.append(lines[j])
                j += 1
            raw = "".join(item_lines).strip()
            # Strip leading "- " for the text
            item_text = raw[2:] if raw.startswith("- ") else raw
            item_end = sum(len(l) for l in lines[:j])
            items.append((item_text, item_start, item_end))
            i = j
        else:
            i += 1
    return items


def remove_text_range(text, abs_start, abs_end):
    """Remove a range and collapse excess blank lines."""
    result = text[:abs_start] + text[abs_end:]
    # collapse triple+ newlines to double
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result


def cleanup_empty_sections(text):
    """Remove ## project sections that have no items. Preserve In progress and Uncategorized."""
    protected = {"In progress", "Uncategorized"}
    changed = True
    while changed:
        changed = False
        for heading, start, end, _ in find_sections(text):
            if heading in protected:
                continue
            heading_end = text.index("\n", start) + 1
            content = text[heading_end:end]
            items = parse_items(content)
            if not items:
                text = text[:start] + text[end:]
                text = re.sub(r"\n{3,}", "\n\n", text)
                changed = True
                break
    return text


def ensure_trailing_newline(text):
    if text and not text.endswith("\n"):
        text += "\n"
    return text


# ---------------------------------------------------------------------------
# Section insertion point helpers
# ---------------------------------------------------------------------------

def find_insert_before_uncategorized(text):
    """Return char position just before ## Uncategorized (for creating new project sections)."""
    for heading, start, _, _ in find_sections(text):
        if heading == "Uncategorized":
            return start
    return len(text)


def find_first_project_section_start(text):
    """Return char position of the first ## heading that isn't 'In progress'."""
    for heading, start, _, _ in find_sections(text):
        if heading != "In progress":
            return start
    return len(text)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_list_projects(args):
    text = read_wip()
    projects = parse_projects_table(text)
    print(json.dumps(projects, indent=2))


def cmd_resolve_project(args):
    text = read_wip()
    projects = parse_projects_table(text)
    cwd = os.path.abspath(os.path.expanduser(args.cwd))
    for p in projects:
        home = os.path.abspath(os.path.expanduser(p["home"]))
        if cwd == home or cwd.startswith(home + os.sep):
            print(json.dumps({"project": p["name"], "home": p["home"]}))
            return
    print(json.dumps({"project": "", "home": ""}))


def cmd_status(args):
    text = read_wip()
    result = {"in_progress": [], "next": [], "uncategorized": []}

    # In progress items
    sec = get_section_content(text, "In progress")
    if sec:
        _, _, content = sec
        for item_text, _, _ in parse_items(content):
            m = re.match(r"^\*\*(.+?)\*\*\s*(.*)", item_text, re.DOTALL)
            if m:
                result["in_progress"].append({
                    "project": m.group(1),
                    "text": m.group(2).strip(),
                })
            else:
                result["in_progress"].append({"project": "", "text": item_text})

    # Project sections
    projects = parse_projects_table(text)
    project_names = {p["name"] for p in projects}
    for heading, start, end, _ in find_sections(text):
        if heading in ("In progress", "Uncategorized") or heading not in project_names:
            continue
        if args.project and heading != args.project:
            continue
        heading_end = text.index("\n", start) + 1
        content = text[heading_end:end]
        items = parse_items(content)
        if items:
            result["next"].append({"project": heading, "text": items[0][0]})

    # Uncategorized
    sec = get_section_content(text, "Uncategorized")
    if sec:
        _, _, content = sec
        for item_text, _, _ in parse_items(content):
            result["uncategorized"].append({"text": item_text})

    print(json.dumps(result, indent=2))


def cmd_add(args):
    text = read_wip()
    project = args.project
    item = args.item

    sec = get_section_content(text, project)
    if sec:
        heading_end, end, content = sec
        # Insert before the end of the section
        insert_pos = end
        # Walk backwards past trailing whitespace to find good insertion point
        bullet = f"- {item}\n\n"
        text = text[:insert_pos].rstrip("\n") + "\n\n" + bullet + text[insert_pos:].lstrip("\n")
    else:
        # Create section before Uncategorized
        insert_pos = find_insert_before_uncategorized(text)
        section = f"## {project}\n\n- {item}\n\n"
        text = text[:insert_pos] + section + text[insert_pos:]

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = ensure_trailing_newline(text)
    write_wip(text)
    print(json.dumps({"ok": True, "project": project, "item": item}))


def cmd_dispatch(args):
    text = read_wip()
    project = args.project

    sec = get_section_content(text, project)
    if not sec:
        print(json.dumps({"error": f"No section found for project '{project}'"}))
        sys.exit(1)

    heading_end, end, content = sec
    items = parse_items(content)
    if not items:
        print(json.dumps({"error": f"No items in '{project}' section"}))
        sys.exit(1)

    item_text, item_start, item_end = items[0]

    # Parse section hint from parenthesized suffix
    section_hint = ""
    hint_match = re.search(r"\((\w[\w\s-]*)\)\s*$", item_text)
    if hint_match:
        section_hint = hint_match.group(1).strip()
        clean_text = item_text[:hint_match.start()].strip()
    else:
        clean_text = item_text

    # Remove item from project section
    abs_start = heading_end + item_start
    abs_end = heading_end + item_end
    text = remove_text_range(text, abs_start, abs_end)

    # Add to In progress
    in_progress = get_section_content(text, "In progress")
    if in_progress:
        ip_heading_end, ip_end, ip_content = in_progress
        insert_pos = ip_end
        bullet = f"- **{project}** {clean_text}\n\n"
        text = text[:insert_pos].rstrip("\n") + "\n\n" + bullet + text[insert_pos:].lstrip("\n")
    else:
        # Create In progress after table, before first project section
        insert_pos = find_first_project_section_start(text)
        section = f"## In progress\n\n- **{project}** {clean_text}\n\n"
        text = text[:insert_pos] + section + text[insert_pos:]

    text = cleanup_empty_sections(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = ensure_trailing_newline(text)
    write_wip(text)

    print(json.dumps({
        "ok": True,
        "project": project,
        "item": clean_text,
        "section_hint": section_hint,
    }))


def cmd_done(args):
    text = read_wip()
    project = args.project

    sec = get_section_content(text, "In progress")
    if not sec:
        print(json.dumps({"error": "No 'In progress' section found"}))
        sys.exit(1)

    heading_end, end, content = sec
    items = parse_items(content)

    # Filter to items matching this project
    matches = []
    for i, (item_text, item_start, item_end) in enumerate(items):
        m = re.match(r"^\*\*(.+?)\*\*", item_text)
        if m and m.group(1) == project:
            matches.append((i, item_text, item_start, item_end))

    if not matches:
        print(json.dumps({"error": f"No in-progress items for '{project}'"}))
        sys.exit(1)

    if len(matches) == 1:
        idx = 0
    elif args.index is not None:
        idx = args.index
    else:
        # Multiple matches — return them for disambiguation
        items_list = []
        for i, (_, item_text, _, _) in enumerate(matches):
            m = re.match(r"^\*\*(.+?)\*\*\s*(.*)", item_text, re.DOTALL)
            items_list.append({"index": i, "text": m.group(2).strip() if m else item_text})
        print(json.dumps({"needs_disambiguation": True, "items": items_list}))
        return

    if idx < 0 or idx >= len(matches):
        print(json.dumps({"error": f"Invalid index {idx}, have {len(matches)} items"}))
        sys.exit(1)

    _, item_text, item_start, item_end = matches[idx]
    abs_start = heading_end + item_start
    abs_end = heading_end + item_end
    text = remove_text_range(text, abs_start, abs_end)

    text = cleanup_empty_sections(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = ensure_trailing_newline(text)
    write_wip(text)

    m = re.match(r"^\*\*(.+?)\*\*\s*(.*)", item_text, re.DOTALL)
    clean = m.group(2).strip() if m else item_text
    print(json.dumps({"ok": True, "project": project, "item": clean}))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="WIP.md CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-projects")

    rp = sub.add_parser("resolve-project")
    rp.add_argument("--cwd", required=True)

    st = sub.add_parser("status")
    st.add_argument("--project", default="")

    add = sub.add_parser("add")
    add.add_argument("--project", required=True)
    add.add_argument("--item", required=True)

    disp = sub.add_parser("dispatch")
    disp.add_argument("--project", required=True)

    done = sub.add_parser("done")
    done.add_argument("--project", required=True)
    done.add_argument("--index", type=int, default=None)

    args = parser.parse_args()

    cmds = {
        "list-projects": cmd_list_projects,
        "resolve-project": cmd_resolve_project,
        "status": cmd_status,
        "add": cmd_add,
        "dispatch": cmd_dispatch,
        "done": cmd_done,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
