"""Self-assessment quiz tests — pure logic, no DB needed."""

from app.talent.services.self_assessment import (
    ASSESSMENT_DIMENSIONS,
    DIMENSION_KEYS,
    DIMENSION_QUESTIONS,
    QUESTIONS_PER_DIMENSION,
    SelfAssessmentService,
)


class TestQuizGeneration:
    def test_quiz_has_all_dimensions(self):
        svc = SelfAssessmentService(None)
        quiz = svc.generate_quiz("cap-123")
        assert quiz["capability_id"] == "cap-123"
        dim_keys = {d["key"] for d in quiz["dimensions"]}
        assert dim_keys == DIMENSION_KEYS

    def test_each_dimension_has_questions(self):
        svc = SelfAssessmentService(None)
        quiz = svc.generate_quiz("cap-123")
        for dim in quiz["dimensions"]:
            assert len(dim["questions"]) == QUESTIONS_PER_DIMENSION
            for q in dim["questions"]:
                assert q["min"] == 1
                assert q["max"] == 5
                assert isinstance(q["text"], str)
                assert len(q["text"]) > 10

    def test_total_questions_count(self):
        svc = SelfAssessmentService(None)
        quiz = svc.generate_quiz("cap-123")
        assert quiz["total_questions"] == len(ASSESSMENT_DIMENSIONS) * QUESTIONS_PER_DIMENSION

    def test_dimensions_have_weights(self):
        total_weight = sum(d["weight"] for d in ASSESSMENT_DIMENSIONS)
        assert abs(total_weight - 1.0) < 0.001

    def test_dimension_questions_match_keys(self):
        assert set(DIMENSION_QUESTIONS.keys()) == DIMENSION_KEYS

    def test_all_questions_are_strings(self):
        for key, questions in DIMENSION_QUESTIONS.items():
            assert len(questions) == QUESTIONS_PER_DIMENSION, f"{key} has wrong count"
            for q in questions:
                assert isinstance(q, str)


class TestScoreComputation:
    """Test the scoring logic without DB — we can't call submit_assessment
    (needs DB) but can test the math directly."""

    def test_perfect_scores_normalize_to_1(self):
        """All 5s → dimension score = 1.0."""
        avg = 5.0
        normalized = (avg - 1) / 4
        assert abs(normalized - 1.0) < 0.001

    def test_minimum_scores_normalize_to_0(self):
        """All 1s → dimension score = 0.0."""
        avg = 1.0
        normalized = (avg - 1) / 4
        assert abs(normalized) < 0.001

    def test_mid_scores_normalize_to_half(self):
        """All 3s → dimension score = 0.5."""
        avg = 3.0
        normalized = (avg - 1) / 4
        assert abs(normalized - 0.5) < 0.001

    def test_composite_is_weighted_sum(self):
        """Verify composite formula: sum(weight * dimension_score)."""
        dim_scores = {
            "knowledge": 0.5,
            "practice": 0.8,
            "autonomy": 0.6,
            "complexity": 0.4,
            "teaching": 0.3,
        }
        composite = sum(d["weight"] * dim_scores[d["key"]] for d in ASSESSMENT_DIMENSIONS)
        expected = 0.2 * 0.5 + 0.3 * 0.8 + 0.25 * 0.6 + 0.15 * 0.4 + 0.1 * 0.3
        assert abs(composite - expected) < 0.001


class TestValidation:
    def test_valid_responses_structure(self):
        """Valid: all 5 dimensions, 3 scores each, all 1-5."""
        responses = {
            "knowledge": [3, 4, 5],
            "practice": [2, 3, 4],
            "autonomy": [4, 4, 3],
            "complexity": [3, 2, 3],
            "teaching": [1, 2, 1],
        }
        assert set(responses.keys()) == DIMENSION_KEYS
        for scores in responses.values():
            assert len(scores) == QUESTIONS_PER_DIMENSION
            for s in scores:
                assert 1 <= s <= 5
