"""Skill self-assessment — structured questionnaire for capability evaluation (N15).

Generates a quiz based on multiple skill dimensions, allowing users to
self-rate. Produces self_reported evidence with a structured score breakdown.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.evidence import CapabilityEvidence

ASSESSMENT_DIMENSIONS = [
    {"key": "knowledge", "label": "Theoretical Knowledge", "weight": 0.2},
    {"key": "practice", "label": "Practical Application", "weight": 0.3},
    {"key": "autonomy", "label": "Independent Work", "weight": 0.25},
    {"key": "complexity", "label": "Complexity Handled", "weight": 0.15},
    {"key": "teaching", "label": "Can Teach Others", "weight": 0.1},
]

DIMENSION_KEYS = frozenset(d["key"] for d in ASSESSMENT_DIMENSIONS)

DIMENSION_QUESTIONS: dict[str, list[str]] = {
    "knowledge": [
        "I can explain core concepts of this skill to a beginner",
        "I understand the theory behind common techniques",
        "I can identify appropriate tools and methods for different scenarios",
    ],
    "practice": [
        "I have completed real projects using this skill",
        "I can solve practical problems without step-by-step guidance",
        "I have used this skill in a professional or commercial context",
    ],
    "autonomy": [
        "I can work independently without supervision on tasks involving this skill",
        "I can make design decisions and trade-off judgments",
        "I can troubleshoot issues and debug problems on my own",
    ],
    "complexity": [
        "I can handle complex, multi-step problems",
        "I have worked on large-scale or production-quality deliverables",
        "I can integrate this skill with other technologies/domains",
    ],
    "teaching": [
        "I can mentor or train others in this skill",
        "I can create learning materials or documentation",
        "Others come to me for advice on this topic",
    ],
}

QUESTIONS_PER_DIMENSION = 3


class SelfAssessmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def generate_quiz(self, capability_id: str) -> dict:
        """Generate a self-assessment quiz for a capability."""
        return {
            "capability_id": capability_id,
            "dimensions": [
                {
                    **dim,
                    "questions": [
                        {"index": i, "text": q, "min": 1, "max": 5}
                        for i, q in enumerate(DIMENSION_QUESTIONS[dim["key"]])
                    ],
                }
                for dim in ASSESSMENT_DIMENSIONS
            ],
            "total_questions": len(ASSESSMENT_DIMENSIONS) * QUESTIONS_PER_DIMENSION,
        }

    async def submit_assessment(
        self,
        *,
        user_id: str,
        capability_id: str,
        responses: dict[str, list[int]],
    ) -> dict:
        """Process self-assessment responses and create evidence.

        Args:
            responses: {dimension_key: [score1, score2, score3]} where each score is 1-5

        Returns:
            Score breakdown per dimension + composite + evidence_id
        """
        # Validate all dimensions present
        missing = DIMENSION_KEYS - set(responses.keys())
        if missing:
            raise ValueError(f"Missing dimensions: {sorted(missing)}")

        extra_keys = set(responses.keys()) - DIMENSION_KEYS
        if extra_keys:
            raise ValueError(f"Unknown dimensions: {sorted(extra_keys)}")

        # Validate response counts and values
        for dim_key, scores in responses.items():
            expected = len(DIMENSION_QUESTIONS[dim_key])
            if len(scores) != expected:
                raise ValueError(
                    f"Dimension '{dim_key}' expects {expected} responses, got {len(scores)}"
                )
            for i, s in enumerate(scores):
                if not isinstance(s, int) or s < 1 or s > 5:
                    raise ValueError(
                        f"Dimension '{dim_key}' question {i}: score must be int 1-5, got {s}"
                    )

        # Compute per-dimension averages (normalized to 0-1)
        dimension_scores: dict[str, float] = {}
        for dim in ASSESSMENT_DIMENSIONS:
            key = dim["key"]
            scores = responses[key]
            avg = sum(scores) / len(scores)
            dimension_scores[key] = round((avg - 1) / 4, 4)  # 1-5 → 0-1

        # Weighted composite
        composite = sum(
            dim["weight"] * dimension_scores[dim["key"]]
            for dim in ASSESSMENT_DIMENSIONS
        )
        composite = round(composite, 4)

        # Create self_reported evidence
        now = datetime.now(UTC)
        evidence = CapabilityEvidence(
            user_id=user_id,
            capability_id=capability_id,
            source_type="self_assessment",
            source_id=f"self-assessment-{now.isoformat()}",
            score_normalized=composite,
            confidence=0.5,  # self-reported gets low confidence
            verification_level="self_reported",
            occurred_at=now,
            extra={
                "assessment_type": "self_assessment",
                "dimension_scores": dimension_scores,
                "raw_responses": responses,
                "composite_score": composite,
            },
        )
        self.db.add(evidence)
        await self.db.flush()

        return {
            "evidence_id": evidence.id,
            "capability_id": capability_id,
            "composite_score": composite,
            "dimension_scores": {
                dim["key"]: {
                    "label": dim["label"],
                    "weight": dim["weight"],
                    "score": dimension_scores[dim["key"]],
                    "raw_avg": round(sum(responses[dim["key"]]) / len(responses[dim["key"]]), 2),
                }
                for dim in ASSESSMENT_DIMENSIONS
            },
        }
