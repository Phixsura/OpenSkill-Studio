"""Code snippet manager — store, tag, and search reusable code snippets."""
from __future__ import annotations
import html
import secrets


class CodeSnippetManager:
    def __init__(self):
        self._snippets: dict[str, dict] = {}

    def create(self, *, title: str, language: str, code: str,
               tags: list[str] | None = None) -> dict:
        sid = f"snip_{secrets.token_hex(6)}"
        self._snippets[sid] = {
            "id": sid, "title": html.escape(title),
            "language": language, "code": code,
            "tags": tags or [], "copies": 0,
        }
        return {"id": sid, "title": html.escape(title)}

    def search(self, query: str) -> list[dict]:
        q = query.lower()
        return [{"id": s["id"], "title": s["title"], "language": s["language"],
                 "tags": s["tags"], "preview": s["code"][:80]}
                for s in self._snippets.values()
                if q in s["title"].lower() or q in " ".join(s["tags"]).lower()
                or q in s["language"].lower()]

    def copy(self, sid: str) -> dict:
        s = self._snippets.get(sid)
        if not s:
            return {"error": "Snippet not found"}
        s["copies"] += 1
        return {"id": sid, "code": s["code"], "copies": s["copies"]}

    def list_by_language(self) -> dict[str, int]:
        by_lang: dict[str, int] = {}
        for s in self._snippets.values():
            by_lang[s["language"]] = by_lang.get(s["language"], 0) + 1
        return by_lang
