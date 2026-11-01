"""Search index — in-memory full-text search with ranking."""

import html
import re
from collections import defaultdict


class SearchIndex:
    def __init__(self):
        self._docs: dict[str, dict] = {}
        self._inverted: dict[str, set[str]] = defaultdict(set)

    def index(self, *, doc_id: str, title: str, body: str, tags: list[str] | None = None) -> None:
        tokens = self._tokenize(f"{title} {body}")
        self._docs[doc_id] = {"title": title, "body": body, "tags": tags or []}
        for token in tokens:
            self._inverted[token].add(doc_id)

    def search(self, *, query: str, limit: int = 10) -> dict:
        tokens = self._tokenize(query)
        scores: dict[str, int] = defaultdict(int)
        for token in tokens:
            for doc_id in self._inverted.get(token, set()):
                scores[doc_id] += 1
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        results = []
        for doc_id, score in ranked:
            doc = self._docs[doc_id]
            results.append({"id": doc_id, "title": html.escape(doc["title"]),
                             "snippet": html.escape(doc["body"][:120]),
                             "score": score, "tags": doc["tags"]})
        return {"results": results, "total": len(results), "query": query}

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [w.lower() for w in re.findall(r"\w+", text) if len(w) > 1]
