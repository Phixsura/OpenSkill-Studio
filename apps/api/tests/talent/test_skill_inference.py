"""Skill inference tests — pure logic, no DB needed for extraction."""

from app.talent.services.skill_inference import (
    FUZZY_THRESHOLD,
    SOURCE_TYPES,
    InferredSkill,
    _extract_candidates,
    _find_excerpt,
)


class TestExtractCandidates:
    def test_extracts_capitalized_phrases(self):
        text = "I have experience in Machine Learning and Computer Vision."
        candidates = _extract_candidates(text)
        names = [c[0] for c in candidates]
        assert "machine learning" in names or any("machine" in n for n in names)

    def test_extracts_hyphenated_terms(self):
        text = "Proficient in front-end development and back-end systems."
        candidates = _extract_candidates(text)
        names = [c[0] for c in candidates]
        # Hyphenated terms get normalized: "back-end" → "back end"
        assert any("back" in n for n in names) or any("front" in n for n in names)

    def test_extracts_acronyms(self):
        text = "Experience with NLP, AI, and ML frameworks."
        candidates = _extract_candidates(text)
        names = [c[0] for c in candidates]
        assert any("nlp" in n or "ai" in n for n in names)

    def test_filters_stop_phrases(self):
        text = "Experience with strong Communication Skills and team Requirements."
        candidates = _extract_candidates(text)
        names = [c[0] for c in candidates]
        # "experience", "skills", "requirements", "strong" are stop phrases
        assert "experience" not in names
        assert "skills" not in names
        assert "requirements" not in names

    def test_counts_frequency(self):
        text = "Python Python Python is great. Also Java."
        candidates = _extract_candidates(text)
        freq_map = dict(candidates)
        python_freq = freq_map.get("python", 0)
        java_freq = freq_map.get("java", 0)
        assert python_freq >= java_freq

    def test_empty_text(self):
        candidates = _extract_candidates("")
        assert candidates == []

    def test_short_terms_filtered(self):
        text = "I do AI and ML."
        candidates = _extract_candidates(text)
        # Two-char terms like "ai", "ml" may or may not pass (≥3 char filter)
        # but should not crash
        assert isinstance(candidates, list)
        # All extracted terms should be ≥3 chars
        for name, _ in candidates:
            assert len(name) >= 3


class TestFindExcerpt:
    def test_finds_term_in_text(self):
        text = "I have extensive experience in Machine Learning and deep neural networks."
        excerpt = _find_excerpt(text, "Machine Learning")
        assert "Machine Learning" in excerpt

    def test_returns_beginning_when_not_found(self):
        text = "Some long text about various topics."
        excerpt = _find_excerpt(text, "nonexistent")
        assert len(excerpt) > 0

    def test_adds_ellipsis_for_long_text(self):
        text = "A" * 200 + " Python " + "B" * 200
        excerpt = _find_excerpt(text, "Python")
        assert "…" in excerpt


class TestInferredSkill:
    def test_dataclass_fields(self):
        skill = InferredSkill(
            capability_id="cap1",
            capability_name="Python",
            confidence=0.95,
            source_excerpt="Experience with Python",
            match_type="exact",
        )
        assert skill.capability_id == "cap1"
        assert skill.confidence == 0.95
        assert skill.match_type == "exact"

    def test_none_capability_id_for_inferred(self):
        skill = InferredSkill(
            capability_id=None,
            capability_name="New Skill",
            confidence=0.3,
            source_excerpt="...",
            match_type="inferred",
        )
        assert skill.capability_id is None


class TestConstants:
    def test_fuzzy_threshold(self):
        assert FUZZY_THRESHOLD == 0.70

    def test_source_types(self):
        assert "resume" in SOURCE_TYPES
        assert "job_description" in SOURCE_TYPES
        assert "project_description" in SOURCE_TYPES
        assert "free_text" in SOURCE_TYPES

    def test_source_types_count(self):
        assert len(SOURCE_TYPES) == 4
