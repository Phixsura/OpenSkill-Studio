"""Content versioning — track revisions of content objects."""
from __future__ import annotations
import hashlib
import time


def create_revision(content_id: str, body: str, author: str, message: str = "") -> dict:
    rev_hash = hashlib.sha256(body.encode()).hexdigest()[:10]
    return {"content_id": content_id, "revision": rev_hash, "author": author,
            "message": message, "size": len(body), "created_at": time.time()}


def diff_revisions(old_body: str, new_body: str) -> dict:
    old_lines = old_body.splitlines()
    new_lines = new_body.splitlines()
    added = len(new_lines) - len(old_lines) if len(new_lines) > len(old_lines) else 0
    removed = len(old_lines) - len(new_lines) if len(old_lines) > len(new_lines) else 0
    changed = sum(1 for a, b in zip(old_lines, new_lines) if a != b)
    return {"added_lines": added, "removed_lines": removed,
            "changed_lines": changed, "total_changes": added + removed + changed,
            "old_size": len(old_body), "new_size": len(new_body)}


def revision_history(revisions: list[dict]) -> dict:
    authors = list({r["author"] for r in revisions})
    return {"revisions": revisions, "total": len(revisions),
            "authors": authors, "author_count": len(authors),
            "latest": revisions[-1]["revision"] if revisions else None}
