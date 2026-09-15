"""Candidate analytics tests — dataclass structure, no DB needed."""

from app.talent.services.candidate_analytics import (
    _ACTIVE_STATUSES,
    _PENDING_STATUSES,
    _TERMINAL_STATUSES,
    CandidateApplicationStats,
)


class TestCandidateApplicationStats:
    def test_empty_stats(self):
        stats = CandidateApplicationStats(
            total_applications=0,
            active_applications=0,
            offers_received=0,
            placements=0,
            success_rate=0.0,
            response_rate=0.0,
            avg_days_to_response=None,
            most_common_rejection_stage=None,
            applications_by_status={},
            applications_by_type={},
        )
        assert stats.total_applications == 0
        assert stats.success_rate == 0.0
        assert stats.avg_days_to_response is None

    def test_success_rate(self):
        stats = CandidateApplicationStats(
            total_applications=10,
            active_applications=3,
            offers_received=2,
            placements=1,
            success_rate=0.2,
            response_rate=0.7,
            avg_days_to_response=5.5,
            most_common_rejection_stage="screening",
            applications_by_status={"submitted": 3, "rejected": 4, "offer": 2, "hired": 1},
            applications_by_type={"internship": 5, "full_time": 5},
        )
        assert stats.success_rate == 0.2
        assert stats.placements == 1
        assert stats.most_common_rejection_stage == "screening"

    def test_response_rate_calculation(self):
        # 8 out of 10 applications moved past submitted = 0.8
        stats = CandidateApplicationStats(
            total_applications=10,
            active_applications=2,
            offers_received=1,
            placements=0,
            success_rate=0.1,
            response_rate=0.8,
            avg_days_to_response=3.0,
            most_common_rejection_stage=None,
            applications_by_status={"submitted": 2, "screening": 3, "rejected": 5},
            applications_by_type={},
        )
        assert stats.response_rate == 0.8

    def test_frozen(self):
        stats = CandidateApplicationStats(
            total_applications=1,
            active_applications=1,
            offers_received=0,
            placements=0,
            success_rate=0.0,
            response_rate=0.0,
            avg_days_to_response=None,
            most_common_rejection_stage=None,
            applications_by_status={},
            applications_by_type={},
        )
        try:
            stats.total_applications = 99  # type: ignore
            raise AssertionError("Should not allow mutation")
        except AttributeError:
            pass

    def test_status_by_dict(self):
        stats = CandidateApplicationStats(
            total_applications=5,
            active_applications=2,
            offers_received=1,
            placements=0,
            success_rate=0.2,
            response_rate=0.6,
            avg_days_to_response=4.0,
            most_common_rejection_stage="interview",
            applications_by_status={"screening": 2, "interview": 1, "rejected": 2},
            applications_by_type={"contract": 3, "freelance": 2},
        )
        assert stats.applications_by_status["screening"] == 2
        assert stats.applications_by_type["contract"] == 3


class TestConstants:
    def test_pending_statuses(self):
        assert "submitted" in _PENDING_STATUSES

    def test_active_statuses(self):
        assert "screening" in _ACTIVE_STATUSES
        assert "interview" in _ACTIVE_STATUSES
        assert "offer" in _ACTIVE_STATUSES

    def test_terminal_statuses(self):
        assert "rejected" in _TERMINAL_STATUSES
        assert "hired" in _TERMINAL_STATUSES
        assert "completed" in _TERMINAL_STATUSES

    def test_no_overlap_pending_terminal(self):
        assert not _PENDING_STATUSES & _TERMINAL_STATUSES
