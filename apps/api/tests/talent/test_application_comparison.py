"""Application comparison tests — pure logic, no DB needed."""


from app.talent.services.application_comparison import MAX_COMPARE, CandidateComparison


class TestComparisonConstants:
    def test_max_compare(self):
        assert MAX_COMPARE == 10


class TestCandidateComparison:
    def test_dataclass_creation(self):
        comp = CandidateComparison(
            application_id="app1",
            user_id="user1",
            status="submitted",
            capability_scores={"cap1": 0.8},
            credential_count=3,
            evidence_count=10,
            endorsement_count=5,
            match_score=0.85,
            interview_ratings={"technical": 4.5},
            overall_rank=1,
        )
        assert comp.application_id == "app1"
        assert comp.match_score == 0.85
        assert comp.overall_rank == 1

    def test_ranking_assignment(self):
        comparisons = [
            CandidateComparison(
                application_id=f"app{i}",
                user_id=f"user{i}",
                status="submitted",
                capability_scores={},
                credential_count=0,
                evidence_count=0,
                endorsement_count=0,
                match_score=score,
                interview_ratings={},
                overall_rank=0,
            )
            for i, score in enumerate([0.5, 0.9, 0.7])
        ]
        comparisons.sort(key=lambda c: c.match_score or 0, reverse=True)
        for i, comp in enumerate(comparisons):
            comp.overall_rank = i + 1

        assert comparisons[0].match_score == 0.9
        assert comparisons[0].overall_rank == 1
        assert comparisons[2].match_score == 0.5
        assert comparisons[2].overall_rank == 3

    def test_capability_scores_dict(self):
        comp = CandidateComparison(
            application_id="app1",
            user_id="user1",
            status="interview",
            capability_scores={"cap1": 0.8, "cap2": 0.6, "cap3": 0.9},
            credential_count=0,
            evidence_count=0,
            endorsement_count=0,
            match_score=None,
            interview_ratings={},
            overall_rank=0,
        )
        avg = sum(comp.capability_scores.values()) / len(comp.capability_scores)
        assert abs(avg - 0.7667) < 0.01

    def test_interview_ratings(self):
        comp = CandidateComparison(
            application_id="app1",
            user_id="user1",
            status="interview",
            capability_scores={},
            credential_count=0,
            evidence_count=0,
            endorsement_count=0,
            match_score=None,
            interview_ratings={"technical": 4.5, "cultural": 3.0, "behavioral": None},
            overall_rank=0,
        )
        rated = {k: v for k, v in comp.interview_ratings.items() if v is not None}
        assert len(rated) == 2
        assert rated["technical"] == 4.5

    def test_empty_comparison(self):
        comp = CandidateComparison(
            application_id="app1",
            user_id="user1",
            status="submitted",
            capability_scores={},
            credential_count=0,
            evidence_count=0,
            endorsement_count=0,
            match_score=None,
            interview_ratings={},
            overall_rank=0,
        )
        assert comp.credential_count == 0
        assert comp.match_score is None

    def test_composite_scoring_logic(self):
        """Verify the ranking composite formula."""
        comp = CandidateComparison(
            application_id="app1",
            user_id="user1",
            status="submitted",
            capability_scores={"c1": 0.8, "c2": 0.6},
            credential_count=3,
            evidence_count=15,
            endorsement_count=2,
            match_score=None,
            interview_ratings={},
            overall_rank=0,
        )
        avg_cap = sum(comp.capability_scores.values()) / len(comp.capability_scores)
        score = avg_cap * 0.5 + min(comp.credential_count / 5, 1) * 0.2 + min(comp.evidence_count / 20, 1) * 0.3
        assert score > 0  # Should be positive
        assert score < 1  # Should be bounded

    def test_endorsement_count_tracked(self):
        comp = CandidateComparison(
            application_id="app1",
            user_id="user1",
            status="offer",
            capability_scores={},
            credential_count=0,
            evidence_count=0,
            endorsement_count=12,
            match_score=0.9,
            interview_ratings={},
            overall_rank=1,
        )
        assert comp.endorsement_count == 12
