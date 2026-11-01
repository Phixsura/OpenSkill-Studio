from app.services.app_marketplace_extension_rating_system import ExtensionRatingSystemService


def test_rate():
    svc = ExtensionRatingSystemService()
    r = svc.rate("ext-1", "u1", 5, "Amazing!", verified=True)
    assert r.score == 5
    assert r.verified is True


def test_average():
    svc = ExtensionRatingSystemService()
    svc.rate("ext-1", "u1", 5)
    svc.rate("ext-1", "u2", 3)
    svc.rate("ext-1", "u3", 4)
    assert svc.get_average("ext-1") == 4.0


def test_bayesian():
    svc = ExtensionRatingSystemService()
    # Single 5-star should pull toward global avg
    svc.rate("ext-1", "u1", 5)
    bayesian = svc.get_bayesian_average("ext-1")
    assert bayesian < 5.0  # pulled down by prior


def test_update_rating():
    svc = ExtensionRatingSystemService()
    svc.rate("ext-1", "u1", 3)
    svc.rate("ext-1", "u1", 5)  # same user updates
    assert len(svc._ratings["ext-1"]) == 1
    assert svc.get_average("ext-1") == 5.0


def test_distribution():
    svc = ExtensionRatingSystemService()
    svc.rate("ext-1", "u1", 5)
    svc.rate("ext-1", "u2", 5)
    svc.rate("ext-1", "u3", 3)
    dist = svc.get_distribution("ext-1")
    assert dist[5] == 2
    assert dist[3] == 1


def test_invalid_score():
    svc = ExtensionRatingSystemService()
    result = svc.rate("ext-1", "u1", 6)
    assert isinstance(result, dict) and "error" in result


def test_stats():
    svc = ExtensionRatingSystemService()
    svc.rate("ext-1", "u1", 5, "Great!", verified=True)
    svc.rate("ext-1", "u2", 4)
    stats = svc.get_stats("ext-1")
    assert stats["count"] == 2
    assert stats["verified_count"] == 1
    assert stats["with_review"] == 1
