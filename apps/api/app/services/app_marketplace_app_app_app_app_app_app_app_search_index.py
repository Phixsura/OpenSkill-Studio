"""Platform search indexer — index and search platform resources."""
from __future__ import annotations


class SearchIndexer:
    def __init__(self):
        self._docs: dict[str, dict] = {}

    def index(self, doc_id: str, title: str, body: str, tags: list[str] | None = None, doc_type: str = "general") -> dict:
        tokens = set((title + " " + body).lower().split())
        self._docs[doc_id] = {"id": doc_id, "title": title, "body": body,
                               "tags": tags or [], "type": doc_type, "tokens": tokens}
        return {"indexed": True, "id": doc_id, "token_count": len(tokens)}

    def search(self, query: str, doc_type: str = "", limit: int = 10) -> list[dict]:
        q_tokens = set(query.lower().split())
        results = []
        for doc in self._docs.values():
            if doc_type and doc["type"] != doc_type:
                continue
            overlap = q_tokens & doc["tokens"]
            if overlap:
                score = len(overlap) / len(q_tokens)
                results.append({"id": doc["id"], "title": doc["title"],
                                "score": round(score, 3), "type": doc["type"]})
        results.sort(key=lambda r: -r["score"])
        return results[:limit]

    def stats(self) -> dict:
        by_type: dict[str, int] = {}
        for d in self._docs.values():
            by_type[d["type"]] = by_type.get(d["type"], 0) + 1
        return {"total_docs": len(self._docs), "by_type": by_type}
