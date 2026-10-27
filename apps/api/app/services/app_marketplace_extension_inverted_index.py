"""Inverted Index — full-text search with TF-IDF scoring.

Implements:
- Tokenization with normalization (lowercase, punctuation strip)
- Inverted index: term → [(doc_id, positions)]
- TF-IDF scoring for relevance ranking
- Boolean queries: AND, OR
- Phrase queries (consecutive positions)
- Highlight matching terms
"""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import math
from collections import defaultdict


@dataclass
class SearchResult:
    doc_id: str
    score: float
    highlights: list[str] = field(default_factory=list)


STOP_WORDS = frozenset(["the", "a", "an", "is", "are", "was", "were", "in",
                         "on", "at", "to", "for", "of", "and", "or", "but",
                         "not", "with", "this", "that", "it", "be", "as"])

TOKEN_RE = re.compile(r'[a-z0-9]+')


class InvertedIndexService:
    def __init__(self, use_stopwords: bool = True):
        self._index: dict[str, dict[str, list[int]]] = defaultdict(dict)  # term → {doc_id → [positions]}
        self._docs: dict[str, str] = {}  # doc_id → original text
        self._doc_lengths: dict[str, int] = {}
        self._use_stopwords = use_stopwords

    def _tokenize(self, text: str) -> list[str]:
        tokens = TOKEN_RE.findall(text.lower())
        if self._use_stopwords:
            tokens = [t for t in tokens if t not in STOP_WORDS]
        return tokens

    def index_document(self, doc_id: str, text: str) -> int:
        """Index a document. Returns number of terms indexed."""
        tokens = self._tokenize(text)
        self._docs[doc_id] = text
        self._doc_lengths[doc_id] = len(tokens)

        # Clear previous entries for this doc
        for term in list(self._index.keys()):
            self._index[term].pop(doc_id, None)

        # Build postings with positions
        for pos, token in enumerate(tokens):
            if doc_id not in self._index[token]:
                self._index[token][doc_id] = []
            self._index[token][doc_id].append(pos)

        return len(set(tokens))

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        """Search with TF-IDF scoring."""
        terms = self._tokenize(query)
        if not terms:
            return []

        scores: dict[str, float] = defaultdict(float)
        num_docs = len(self._docs)

        for term in terms:
            postings = self._index.get(term, {})
            if not postings:
                continue
            # IDF = log(N / df)
            idf = math.log(num_docs / len(postings)) if num_docs > 0 else 0

            for doc_id, positions in postings.items():
                # TF = count / doc_length
                tf = len(positions) / max(1, self._doc_lengths[doc_id])
                scores[doc_id] += tf * idf

        results = []
        for doc_id in sorted(scores, key=scores.__getitem__, reverse=True)[:limit]:
            highlights = self._highlight(doc_id, terms)
            results.append(SearchResult(doc_id=doc_id, score=round(scores[doc_id], 4),
                                        highlights=highlights))
        return results

    def search_and(self, terms: list[str]) -> list[str]:
        """Boolean AND: documents containing ALL terms."""
        if not terms:
            return []
        term_tokens = [t.lower() for t in terms]
        result_sets = []
        for term in term_tokens:
            postings = self._index.get(term, {})
            result_sets.append(set(postings.keys()))
        if not result_sets:
            return []
        return sorted(set.intersection(*result_sets))

    def search_or(self, terms: list[str]) -> list[str]:
        """Boolean OR: documents containing ANY term."""
        result = set()
        for term in terms:
            postings = self._index.get(term.lower(), {})
            result.update(postings.keys())
        return sorted(result)

    def search_phrase(self, phrase: str) -> list[str]:
        """Phrase query: terms must appear consecutively."""
        terms = self._tokenize(phrase)
        if len(terms) < 2:
            return self.search_and(terms)

        # Get docs containing all terms
        candidates = self.search_and(terms)
        results = []

        for doc_id in candidates:
            # Check consecutive positions
            positions_list = [self._index[t].get(doc_id, []) for t in terms]
            # For each starting position of first term, check if phrase matches
            for start_pos in positions_list[0]:
                match = True
                for offset, term_positions in enumerate(positions_list[1:], 1):
                    if start_pos + offset not in term_positions:
                        match = False
                        break
                if match:
                    results.append(doc_id)
                    break

        return results

    def _highlight(self, doc_id: str, terms: list[str], context: int = 5) -> list[str]:
        text = self._docs.get(doc_id, "")
        words = text.split()
        highlights = []
        for i, word in enumerate(words):
            if word.lower().strip(".,!?;:") in terms:
                start = max(0, i - context)
                end = min(len(words), i + context + 1)
                snippet = " ".join(words[start:end])
                highlights.append(f"...{snippet}...")
                if len(highlights) >= 3:
                    break
        return highlights

    def get_term_frequency(self, term: str) -> int:
        """Number of documents containing term."""
        return len(self._index.get(term.lower(), {}))

    @property
    def doc_count(self) -> int:
        return len(self._docs)

    @property
    def term_count(self) -> int:
        return len(self._index)
