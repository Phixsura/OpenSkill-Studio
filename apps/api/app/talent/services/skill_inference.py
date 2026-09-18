"""AI-powered skill inference from text (ADR-015 world-class upgrade C1).

Extracts capabilities from free text (resumes, job descriptions, project
descriptions) with confidence scores and maps to the existing capability
ontology using fuzzy string matching.

Algorithm:
  1. Tokenize → extract candidate noun-phrases via regex
  2. Match each candidate against Capability.canonical_name, aliases, slug
     - exact match → confidence boost
     - alias match → confidence boost (slightly lower)
     - fuzzy match (SequenceMatcher ≥ 0.70) → proportional confidence
  3. Unmatched but frequent terms → suggest as new capabilities
  4. Score by term frequency × match quality
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from difflib import SequenceMatcher

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.capability import Capability

# Minimum fuzzy-match ratio to consider a match
FUZZY_THRESHOLD = 0.70

# Common stop-phrases that should not be treated as skills
_STOP_PHRASES = frozenset(
    {
        "experience",
        "skills",
        "responsibilities",
        "requirements",
        "qualifications",
        "education",
        "work",
        "team",
        "company",
        "role",
        "position",
        "job",
        "description",
        "years",
        "ability",
        "communication",
        "environment",
        "strong",
        "knowledge",
        "good",
        "excellent",
        "proficient",
        "understanding",
        "familiar",
        "working",
        "preferred",
        "required",
        "minimum",
        "plus",
        "etc",
        "including",
        "related",
        "relevant",
        "demonstrated",
    }
)

# Regex to extract candidate phrases (1-4 word noun phrases)
_PHRASE_RE = re.compile(
    r"\b([A-Z][a-z]+(?:\s+[A-Za-z]+){0,3})\b"
    r"|"
    r"\b([a-z]+(?:[-_][a-z]+)+)\b"  # hyphenated/underscore terms like "machine-learning"
    r"|"
    r"\b([A-Z]{2,}(?:\s+[A-Z][a-z]*)*)\b"  # acronyms like "NLP", "AI Product Design"
)


SOURCE_TYPES = frozenset(
    {
        "resume",
        "job_description",
        "project_description",
        "free_text",
    }
)


@dataclass(frozen=True, slots=True)
class InferredSkill:
    """A single inferred skill from text analysis."""

    capability_id: str | None  # None if unmatched/suggested
    capability_name: str
    confidence: float
    source_excerpt: str
    match_type: str  # exact, alias, fuzzy, inferred


def _extract_candidates(text: str) -> list[tuple[str, int]]:
    """Extract candidate skill phrases with their frequency count."""
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text.strip())

    phrases: dict[str, int] = {}
    for m in _PHRASE_RE.finditer(text):
        phrase = (m.group(1) or m.group(2) or m.group(3) or "").strip()
        if not phrase or len(phrase) < 2:
            continue
        # Normalize
        normalized = phrase.lower().replace("-", " ").replace("_", " ").strip()
        if normalized in _STOP_PHRASES or len(normalized) < 3:
            continue
        phrases[normalized] = phrases.get(normalized, 0) + 1

    # Sort by frequency descending
    return sorted(phrases.items(), key=lambda x: -x[1])


def _find_excerpt(text: str, term: str, window: int = 60) -> str:
    """Find a snippet of text around where the term appears."""
    lower_text = text.lower()
    idx = lower_text.find(term.lower())
    if idx == -1:
        # Try first word
        first_word = term.split()[0] if " " in term else term
        idx = lower_text.find(first_word.lower())
    if idx == -1:
        return text[:window] + "…" if len(text) > window else text

    start = max(0, idx - window // 2)
    end = min(len(text), idx + len(term) + window // 2)
    excerpt = text[start:end].strip()
    if start > 0:
        excerpt = "…" + excerpt
    if end < len(text):
        excerpt = excerpt + "…"
    return excerpt


async def infer_skills_from_text(
    db: AsyncSession,
    text: str,
    source_type: str,
    *,
    max_results: int = 20,
) -> tuple[list[InferredSkill], float]:
    """Extract and match skills from free text.

    Returns (inferred_skills, processing_time_ms).
    """
    start = time.monotonic()

    if source_type not in SOURCE_TYPES:
        raise ValueError(
            f"Invalid source_type: {source_type}. Must be one of {sorted(SOURCE_TYPES)}"
        )

    # Step 1: Extract candidate phrases
    candidates = _extract_candidates(text)
    if not candidates:
        elapsed = (time.monotonic() - start) * 1000
        return [], elapsed

    # Step 2: Load all active capabilities for matching
    result = await db.execute(
        select(Capability).where(Capability.status.in_(("active", "deprecated")))
    )
    capabilities = list(result.scalars().all())

    # Build lookup structures
    name_map: dict[str, Capability] = {}  # lowercase name → cap
    alias_map: dict[str, Capability] = {}  # lowercase alias → cap
    slug_map: dict[str, Capability] = {}  # slug → cap

    for cap in capabilities:
        name_map[cap.canonical_name.lower()] = cap
        slug_map[cap.slug] = cap
        for alias in cap.aliases or []:
            if isinstance(alias, str):
                alias_map[alias.lower()] = cap

    # Step 3: Match each candidate
    results: list[InferredSkill] = []
    seen_cap_ids: set[str] = set()

    for phrase, freq in candidates:
        # Frequency-based confidence boost (1 mention = base, 3+ = +0.15)
        freq_boost = min(freq - 1, 3) * 0.05

        # Try exact match on canonical_name
        if phrase in name_map:
            cap = name_map[phrase]
            if cap.id in seen_cap_ids:
                continue
            seen_cap_ids.add(cap.id)
            results.append(
                InferredSkill(
                    capability_id=cap.id,
                    capability_name=cap.canonical_name,
                    confidence=min(0.95 + freq_boost, 1.0),
                    source_excerpt=_find_excerpt(text, phrase),
                    match_type="exact",
                )
            )
            continue

        # Try alias match
        if phrase in alias_map:
            cap = alias_map[phrase]
            if cap.id in seen_cap_ids:
                continue
            seen_cap_ids.add(cap.id)
            results.append(
                InferredSkill(
                    capability_id=cap.id,
                    capability_name=cap.canonical_name,
                    confidence=min(0.85 + freq_boost, 1.0),
                    source_excerpt=_find_excerpt(text, phrase),
                    match_type="alias",
                )
            )
            continue

        # Try slug match
        slug_candidate = phrase.replace(" ", "-")
        if slug_candidate in slug_map:
            cap = slug_map[slug_candidate]
            if cap.id in seen_cap_ids:
                continue
            seen_cap_ids.add(cap.id)
            results.append(
                InferredSkill(
                    capability_id=cap.id,
                    capability_name=cap.canonical_name,
                    confidence=min(0.85 + freq_boost, 1.0),
                    source_excerpt=_find_excerpt(text, phrase),
                    match_type="alias",
                )
            )
            continue

        # Try fuzzy match against all names + aliases
        best_ratio = 0.0
        best_cap: Capability | None = None
        for cap in capabilities:
            ratio = SequenceMatcher(None, phrase, cap.canonical_name.lower()).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_cap = cap
            # Also check aliases
            for alias in cap.aliases or []:
                if isinstance(alias, str):
                    a_ratio = SequenceMatcher(None, phrase, alias.lower()).ratio()
                    if a_ratio > best_ratio:
                        best_ratio = a_ratio
                        best_cap = cap

        if best_ratio >= FUZZY_THRESHOLD and best_cap and best_cap.id not in seen_cap_ids:
            seen_cap_ids.add(best_cap.id)
            results.append(
                InferredSkill(
                    capability_id=best_cap.id,
                    capability_name=best_cap.canonical_name,
                    confidence=min(round(best_ratio * 0.8 + freq_boost, 2), 1.0),
                    source_excerpt=_find_excerpt(text, phrase),
                    match_type="fuzzy",
                )
            )
        elif freq >= 2 and len(phrase) >= 4:
            # Unmatched but mentioned multiple times → suggest as potential new skill
            results.append(
                InferredSkill(
                    capability_id=None,
                    capability_name=phrase.title(),
                    confidence=round(min(0.3 + freq_boost, 0.6), 2),
                    source_excerpt=_find_excerpt(text, phrase),
                    match_type="inferred",
                )
            )

    # Sort by confidence descending, limit
    results.sort(key=lambda s: s.confidence, reverse=True)
    elapsed = (time.monotonic() - start) * 1000
    return results[:max_results], round(elapsed, 2)
