"""Diff viewer — unified diff parser and renderer."""

import html


def parse_unified_diff(*, diff_text: str) -> dict:
    lines = diff_text.splitlines()
    hunks: list[dict] = []
    current_hunk: dict | None = None
    additions = removals = 0
    for line in lines:
        if line.startswith("@@"):
            if current_hunk:
                hunks.append(current_hunk)
            current_hunk = {"header": line, "lines": []}
        elif current_hunk is not None:
            kind = "add" if line.startswith("+") else "remove" if line.startswith("-") else "context"
            if kind == "add":
                additions += 1
            elif kind == "remove":
                removals += 1
            current_hunk["lines"].append({"content": html.escape(line), "type": kind})
    if current_hunk:
        hunks.append(current_hunk)
    return {"hunks": hunks, "additions": additions, "removals": removals,
            "total_changes": additions + removals}
