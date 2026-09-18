"""Skill synonym resolution — maps variant names to canonical capabilities.

Resolves common abbreviations, alternate spellings, and informal names
to their canonical capability using the aliases JSONB field + fuzzy matching.

Search order:
  1. Exact match on canonical_name (case-insensitive)
  2. Exact match on aliases JSONB array
  3. Built-in synonym map
  4. Fuzzy match on canonical_name (SequenceMatcher >= 0.80)
"""

from __future__ import annotations

from difflib import SequenceMatcher

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.capability import Capability

# Built-in synonym map for common abbreviations (supplements DB aliases)
BUILTIN_SYNONYMS: dict[str, list[str]] = {
    "javascript": ["js", "ecmascript", "es6", "es2015", "node.js", "nodejs"],
    "typescript": ["ts"],
    "python": ["py", "python3"],
    "machine learning": ["ml", "machine-learning"],
    "artificial intelligence": ["ai", "a.i."],
    "computer vision": ["cv", "image recognition"],
    "natural language processing": ["nlp", "text processing"],
    "deep learning": ["dl", "neural networks", "neural nets"],
    "react": ["reactjs", "react.js"],
    "vue": ["vuejs", "vue.js"],
    "angular": ["angularjs", "angular.js"],
    "kubernetes": ["k8s"],
    "docker": ["containerization"],
    "aws": ["amazon web services"],
    "gcp": ["google cloud", "google cloud platform"],
    "azure": ["microsoft azure"],
    "ci/cd": ["cicd", "continuous integration", "continuous deployment"],
    "sql": ["structured query language"],
    "nosql": ["non-relational database"],
    "api": ["application programming interface"],
    "rest": ["restful", "rest api"],
    "graphql": ["graph ql"],
    "ui/ux": ["ui ux", "user interface", "user experience"],
}

# Reverse map: synonym → canonical name
_REVERSE_SYNONYMS: dict[str, str] = {}
for canonical, aliases in BUILTIN_SYNONYMS.items():
    for alias in aliases:
        _REVERSE_SYNONYMS[alias.lower()] = canonical

FUZZY_THRESHOLD = 0.80


class SkillSynonymService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def resolve(self, text: str) -> list[dict]:
        """Resolve a skill name to canonical capabilities.

        Returns: [{capability_id, canonical_name, match_type, confidence}]
        """
        normalized = text.strip().lower()
        if not normalized:
            return []

        # 1. Exact match on canonical_name
        q = select(Capability).where(
            func.lower(Capability.canonical_name) == normalized,
            Capability.status == "active",
        )
        result = await self.db.execute(q)
        cap = result.scalar_one_or_none()
        if cap:
            return [
                {
                    "capability_id": cap.id,
                    "canonical_name": cap.canonical_name,
                    "match_type": "exact",
                    "confidence": 1.0,
                }
            ]

        # 2. Match in aliases JSONB array — load all active capabilities
        all_caps = await self._load_active_capabilities()
        for c in all_caps:
            aliases = c.get("aliases", []) or []
            for alias in aliases:
                if isinstance(alias, str) and alias.lower() == normalized:
                    return [
                        {
                            "capability_id": c["id"],
                            "canonical_name": c["canonical_name"],
                            "match_type": "alias",
                            "confidence": 0.95,
                        }
                    ]

        # 3. Built-in synonym map
        if normalized in _REVERSE_SYNONYMS:
            canonical = _REVERSE_SYNONYMS[normalized]
            for c in all_caps:
                if c["canonical_name"].lower() == canonical:
                    return [
                        {
                            "capability_id": c["id"],
                            "canonical_name": c["canonical_name"],
                            "match_type": "builtin_synonym",
                            "confidence": 0.90,
                        }
                    ]
            # Built-in synonym matched but no capability in DB for it
            return [
                {
                    "capability_id": None,
                    "canonical_name": canonical,
                    "match_type": "builtin_synonym",
                    "confidence": 0.85,
                }
            ]

        # 4. Fuzzy match on canonical_name
        best_match = None
        best_ratio = 0.0
        for c in all_caps:
            ratio = SequenceMatcher(None, normalized, c["canonical_name"].lower()).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = c

        if best_match and best_ratio >= FUZZY_THRESHOLD:
            return [
                {
                    "capability_id": best_match["id"],
                    "canonical_name": best_match["canonical_name"],
                    "match_type": "fuzzy",
                    "confidence": round(best_ratio, 3),
                }
            ]

        return []

    async def resolve_batch(self, texts: list[str]) -> dict[str, list[dict]]:
        """Resolve multiple skill names at once. Returns {input → matches}."""
        results: dict[str, list[dict]] = {}
        for text in texts:
            results[text] = await self.resolve(text)
        return results

    async def suggest_merge(self, capability_id_a: str, capability_id_b: str) -> dict:
        """Check if two capabilities are likely duplicates.

        Returns similarity score and recommendation.
        """
        cap_a = await self.db.get(Capability, capability_id_a)
        cap_b = await self.db.get(Capability, capability_id_b)

        if not cap_a or not cap_b:
            return {
                "similarity": 0.0,
                "recommendation": "not_found",
                "reason": "One or both capabilities not found",
            }

        name_sim = SequenceMatcher(
            None,
            cap_a.canonical_name.lower(),
            cap_b.canonical_name.lower(),
        ).ratio()

        # Check alias overlap
        aliases_a = set(a.lower() for a in (cap_a.aliases or []) if isinstance(a, str))
        aliases_b = set(a.lower() for a in (cap_b.aliases or []) if isinstance(a, str))
        alias_overlap = len(aliases_a & aliases_b) if aliases_a and aliases_b else 0

        # Combined score
        combined = name_sim + (0.1 * alias_overlap)
        combined = min(combined, 1.0)

        if combined >= 0.85:
            recommendation = "likely_duplicate"
        elif combined >= 0.65:
            recommendation = "possibly_related"
        else:
            recommendation = "distinct"

        return {
            "capability_a": {
                "id": cap_a.id,
                "name": cap_a.canonical_name,
            },
            "capability_b": {
                "id": cap_b.id,
                "name": cap_b.canonical_name,
            },
            "name_similarity": round(name_sim, 3),
            "alias_overlap": alias_overlap,
            "combined_score": round(combined, 3),
            "recommendation": recommendation,
        }

    async def _load_active_capabilities(self) -> list[dict]:
        """Load all active capabilities as lightweight dicts."""
        q = select(
            Capability.id,
            Capability.canonical_name,
            Capability.aliases,
        ).where(Capability.status == "active")
        result = await self.db.execute(q)
        return [
            {"id": row.id, "canonical_name": row.canonical_name, "aliases": row.aliases}
            for row in result.all()
        ]
