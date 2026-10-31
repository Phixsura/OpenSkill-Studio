"""Text diff — character-level diff between two strings."""

import html


def compute_text_diff(*, old: str, new: str) -> dict:
    old_words = old.split()
    new_words = new.split()
    added = [w for w in new_words if w not in old_words]
    removed = [w for w in old_words if w not in new_words]
    unchanged = [w for w in old_words if w in new_words]
    similarity = round(len(unchanged) / max(len(set(old_words + new_words)), 1) * 100, 1)
    return {
        "added": [html.escape(w) for w in added],
        "removed": [html.escape(w) for w in removed],
        "unchanged_count": len(unchanged),
        "added_count": len(added),
        "removed_count": len(removed),
        "similarity_pct": similarity,
        "has_changes": len(added) > 0 or len(removed) > 0,
    }
