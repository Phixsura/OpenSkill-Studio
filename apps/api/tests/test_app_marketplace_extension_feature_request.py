from app.services.app_marketplace_extension_feature_request import (
    FeatureRequestService, RequestStatus,
)
import pytest


def test_submit_and_get():
    frs = FeatureRequestService()
    fr = frs.submit("ext-1", "Dark mode", "Add dark mode support", "user-1")
    assert fr.votes == 1  # auto-vote by author
    assert fr.request_id.startswith("fr_")  # server-generated ID
    reqs = frs.get_requests("ext-1")
    assert len(reqs) == 1


def test_submit_duplicate_id_rejected():
    frs = FeatureRequestService()
    frs.submit("ext-1", "A", "Desc", "u1", request_id="fixed-id")
    with pytest.raises(ValueError, match="already exists"):
        frs.submit("ext-1", "B", "Desc", "u2", request_id="fixed-id")


def test_vote():
    frs = FeatureRequestService()
    fr = frs.submit("ext-2", "Feature A", "Desc", "u1")
    ok, _ = frs.vote(fr.request_id, "u2")
    assert ok is True
    ok2, _ = frs.vote(fr.request_id, "u2")
    assert ok2 is False  # duplicate vote


def test_unvote():
    frs = FeatureRequestService()
    fr = frs.submit("ext-3", "Feature B", "Desc", "u1")
    frs.vote(fr.request_id, "u2")
    assert frs.unvote(fr.request_id, "u2") is True
    assert frs._requests[fr.request_id].votes == 1
    # Author can't unvote
    assert frs.unvote(fr.request_id, "u1") is False


def test_sort_by_votes():
    frs = FeatureRequestService()
    fr_a = frs.submit("ext-4", "Low", "D", "u1")
    fr_b = frs.submit("ext-4", "High", "D", "u2")
    frs.vote(fr_b.request_id, "u3")
    frs.vote(fr_b.request_id, "u4")
    reqs = frs.get_requests("ext-4", sort_by="votes")
    assert reqs[0].request_id == fr_b.request_id


def test_status_update():
    frs = FeatureRequestService()
    fr = frs.submit("ext-5", "Feature", "D", "u1")
    frs.update_status(fr.request_id, RequestStatus.PLANNED, "Coming in v3.0")
    req = frs._requests[fr.request_id]
    assert req.status == RequestStatus.PLANNED
    assert req.developer_response == "Coming in v3.0"


def test_stats():
    frs = FeatureRequestService()
    fr1 = frs.submit("ext-6", "A", "D", "u1")
    fr2 = frs.submit("ext-6", "B", "D", "u2")
    frs.update_status(fr1.request_id, RequestStatus.COMPLETED)
    stats = frs.get_stats("ext-6")
    assert stats["total"] == 2
    assert stats["by_status"]["completed"] == 1
    assert stats["by_status"]["open"] == 1
