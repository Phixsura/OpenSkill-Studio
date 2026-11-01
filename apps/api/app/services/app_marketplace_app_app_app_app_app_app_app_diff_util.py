"""Diff viewer utility — compute and display text diffs."""
from __future__ import annotations


def compute_diff(old_text: str, new_text: str) -> dict:
    old_lines = old_text.split("\n")
    new_lines = new_text.split("\n")
    diff_lines = []
    max_lines = max(len(old_lines), len(new_lines))
    added = removed = unchanged = 0
    for i in range(max_lines):
        old = old_lines[i] if i < len(old_lines) else None
        new = new_lines[i] if i < len(new_lines) else None
        if old == new:
            diff_lines.append({"type": "unchanged", "line": i + 1, "content": old or ""})
            unchanged += 1
        elif old is None:
            diff_lines.append({"type": "added", "line": i + 1, "content": new or ""})
            added += 1
        elif new is None:
            diff_lines.append({"type": "removed", "line": i + 1, "content": old})
            removed += 1
        else:
            diff_lines.append({"type": "removed", "line": i + 1, "content": old})
            diff_lines.append({"type": "added", "line": i + 1, "content": new})
            added += 1
            removed += 1
    return {"lines": diff_lines, "added": added, "removed": removed,
            "unchanged": unchanged, "total_changes": added + removed,
            "summary": f"+{added} -{removed}"}
