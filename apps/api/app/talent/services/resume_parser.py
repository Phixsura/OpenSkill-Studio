"""Resume text extraction and skill inference pipeline (N18).

Accepts plain text from a resume/CV and uses the SkillInferenceService
to extract capabilities, then optionally auto-creates self_reported
evidence for high-confidence matches.

Actual file upload + PDF parsing is out of scope — this handles the
text extraction step after upload.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.services.skill_inference import infer_skills_from_text

# Minimum confidence to auto-create evidence
AUTO_EVIDENCE_THRESHOLD = 0.80

# Common resume section headers
_SECTION_PATTERNS: dict[str, str] = {
    "education": r"(?i)(?:education|academic|degree|university|school)",
    "experience": r"(?i)(?:experience|employment|work\s*history|professional\s*background)",
    "skills": r"(?i)(?:skills?|competenc|technical|proficienc|expertise)",
    "projects": r"(?i)(?:projects?|portfolio|personal\s*projects)",
    "certifications": r"(?i)(?:certif|credential|license|qualification|accreditation)",
    "summary": r"(?i)(?:summary|objective|profile|about\s*me|overview)",
}


class ResumeParserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def parse_resume_text(
        self,
        user_id: str,
        text: str,
        *,
        auto_create_evidence: bool = False,
    ) -> dict:
        """Parse resume text and extract capabilities.

        1. Extract structured sections from text
        2. Use SkillInferenceService to extract skills
        3. Optionally create self_reported evidence for high-confidence matches
        4. Return structured result
        """
        sections = self.extract_experience_sections(text)
        section_names = [k for k in sections if k != "other"]

        # Run skill inference on full text
        inferred, _processing_ms = await infer_skills_from_text(
            self.db,
            text,
            "resume",
            max_results=50,
        )

        matched = [s for s in inferred if s.capability_id is not None]
        unmatched_terms = [s.capability_name for s in inferred if s.capability_id is None]

        evidence_created: list[dict] = []

        if auto_create_evidence:
            from app.talent.models.evidence import CapabilityEvidence

            for skill in matched:
                if skill.confidence < AUTO_EVIDENCE_THRESHOLD:
                    continue
                if skill.capability_id is None:
                    continue

                # Check for existing evidence to avoid duplicates
                from sqlalchemy import select

                existing_q = select(CapabilityEvidence).where(
                    CapabilityEvidence.user_id == user_id,
                    CapabilityEvidence.capability_id == skill.capability_id,
                    CapabilityEvidence.source_type == "resume_extraction",
                    CapabilityEvidence.status == "active",
                )
                existing = await self.db.execute(existing_q)
                if existing.scalar_one_or_none():
                    continue

                ev = CapabilityEvidence(
                    user_id=user_id,
                    capability_id=skill.capability_id,
                    source_type="resume_extraction",
                    source_id=f"resume_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
                    score_normalized=round(skill.confidence * 0.6, 2),
                    confidence=round(skill.confidence, 2),
                    verification_level="self_reported",
                    occurred_at=datetime.now(UTC),
                    status="active",
                )
                self.db.add(ev)
                evidence_created.append({
                    "capability_id": skill.capability_id,
                    "capability_name": skill.capability_name,
                    "confidence": skill.confidence,
                })

            if evidence_created:
                await self.db.flush()

        return {
            "extracted_skills": [
                {
                    "capability_id": s.capability_id,
                    "capability_name": s.capability_name,
                    "confidence": s.confidence,
                    "match_type": s.match_type,
                    "source_excerpt": s.source_excerpt,
                }
                for s in inferred
            ],
            "matched_capabilities": [
                {
                    "capability_id": s.capability_id,
                    "capability_name": s.capability_name,
                    "confidence": s.confidence,
                }
                for s in matched
            ],
            "evidence_created": evidence_created,
            "unmatched_terms": unmatched_terms,
            "sections_found": section_names,
        }

    def extract_experience_sections(self, text: str) -> dict[str, str]:
        """Extract structured sections from resume text.

        Uses regex patterns to identify common resume sections.
        Returns {section_name: text_content}.
        """
        lines = text.split("\n")
        sections: dict[str, list[str]] = {}
        current_section = "other"

        for line in lines:
            stripped = line.strip()
            # Only match short lines as potential headers
            if stripped and len(stripped) < 60:
                for section, pattern in _SECTION_PATTERNS.items():
                    if re.search(pattern, stripped):
                        current_section = section
                        break
            sections.setdefault(current_section, []).append(line)

        return {k: "\n".join(v).strip() for k, v in sections.items() if v}
