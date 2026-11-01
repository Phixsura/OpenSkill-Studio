from app.services.app_marketplace_review_system import ReviewSystem


def test_submit_and_get():
    rs = ReviewSystem()
    review, msg = rs.submit_review("r1", "ext-1", "user-1", 5, "Great!", "Works perfectly")
    assert review is not None
    assert review.rating == 5
    reviews = rs.get_reviews("ext-1")
    assert len(reviews) == 1


def test_invalid_rating():
    rs = ReviewSystem()
    r, msg = rs.submit_review("r2", "ext-2", "user-1", 6, "Too high", "")
    assert r is None
    assert "between 1 and 5" in msg


def test_duplicate_review():
    rs = ReviewSystem()
    rs.submit_review("r3", "ext-3", "user-1", 4, "Good", "Nice")
    r, msg = rs.submit_review("r4", "ext-3", "user-1", 3, "Changed mind", "")
    assert r is None
    assert "already reviewed" in msg


def test_rating_summary():
    rs = ReviewSystem()
    rs.submit_review("r10", "ext-10", "u1", 5, "A", "")
    rs.submit_review("r11", "ext-10", "u2", 4, "B", "")
    rs.submit_review("r12", "ext-10", "u3", 3, "C", "")
    summary = rs.get_rating_summary("ext-10")
    assert summary["count"] == 3
    assert summary["average"] == 4.0
    assert summary["distribution"][5] == 1


def test_flag_hides_review():
    rs = ReviewSystem()
    rs.submit_review("r20", "ext-20", "u1", 1, "Spam", "Buy my stuff")
    assert rs.flag_review("r20") is True
    reviews = rs.get_reviews("ext-20")
    assert len(reviews) == 0  # flagged reviews hidden
    rs.unflag_review("r20")
    assert len(rs.get_reviews("ext-20")) == 1


def test_mark_helpful_and_sort():
    rs = ReviewSystem()
    rs.submit_review("r30", "ext-30", "u1", 5, "Helpful", "Detailed review")
    rs.submit_review("r31", "ext-30", "u2", 4, "OK", "Short")
    rs.mark_helpful("r30")
    rs.mark_helpful("r30")
    sorted_reviews = rs.get_reviews("ext-30", sort_by="helpful")
    assert sorted_reviews[0].review_id == "r30"
    assert sorted_reviews[0].helpful_count == 2
