from app.services.app_marketplace_extension_feature_request import (
    FeatureRequestService, RequestStatus,
)


def test_submit_and_get():
    frs = FeatureRequestService()
    fr = frs.submit("fr1", "ext-1", "Dark mode", "Add dark mode support", "user-1")
    assert fr.votes == 1  # auto-vote by author
    reqs = frs.get_requests("ext-1")
    assert len(reqs) == 1


def test_vote():
    frs = FeatureRequestService()
    frs.submit("fr2", "ext-2", "Feature A", "Desc", "u1")
    ok, _ = frs.vote("fr2", "u2")
    assert ok is True
    ok2, _ = frs.vote("fr2", "u2")
    assert ok2 is False  # duplicate vote


def test_unvote():
    frs = FeatureRequestService()
    frs.submit("fr3", "ext-3", "Feature B", "Desc", "u1")
    frs.vote("fr3", "u2")
    assert frs.unvote("fr3", "u2") is True
    assert frs._requests["fr3"].votes == 1
    # Author can't unvote
    assert frs.unvote("fr3", "u1") is False


def test_sort_by_votes():
    frs = FeatureRequestService()
    frs.submit("a", "ext-4", "Low", "D", "u1")
    frs.submit("b", "ext-4", "High", "D", "u2")
    frs.vote("b", "u3")
    frs.vote("b", "u4")
    reqs = frs.get_requests("ext-4", sort_by="votes")
    assert reqs[0].request_id == "b"


def test_status_update():
    frs = FeatureRequestService()
    frs.submit("fr5", "ext-5", "Feature", "D", "u1")
    frs.update_status("fr5", RequestStatus.PLANNED, "Coming in v3.0")
    fr = frs._requests["fr5"]
    assert fr.status == RequestStatus.PLANNED
    assert fr.developer_response == "Coming in v3.0"


def test_stats():
    frs = FeatureRequestService()
    frs.submit("s1", "ext-6", "A", "D", "u1")
    frs.submit("s2", "ext-6", "B", "D", "u2")
    frs.update_status("s1", RequestStatus.COMPLETED)
    stats = frs.get_stats("ext-6")
    assert stats["total"] == 2
    assert stats["by_status"]["completed"] == 1
    assert stats["by_status"]["open"] == 1
