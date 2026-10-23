"""Search index manager — manage full-text search indexes."""
from __future__ import annotations

_index: dict[str, dict] = {}


def index_document(doc_id: str, content: str, metadata: dict | None = None) -> dict:
    words = set(content.lower().split())
    _index[doc_id] = {"id": doc_id, "content": content, "words": words,
                       "metadata": metadata or {}, "word_count": len(words)}
    return {"indexed": True, "id": doc_id, "word_count": len(words)}


def search(query: str, limit: int = 10) -> dict:
    terms = set(query.lower().split())
    results = []
    for doc_id, doc in _index.items():
        matches = terms & doc["words"]
        if matches:
            score = len(matches) / len(terms)
            results.append({"id": doc_id, "score": round(score, 2),
                            "matched_terms": sorted(matches)})
    results.sort(key=lambda r: -r["score"])
    return {"results": results[:limit], "total_matches": len(results), "query": query}


def index_stats() -> dict:
    total_words = sum(d["word_count"] for d in _index.values())
    return {"total_documents": len(_index), "total_words": total_words,
            "avg_words": round(total_words / max(len(_index), 1), 1)}


def clear_index() -> None:
    _index.clear()
