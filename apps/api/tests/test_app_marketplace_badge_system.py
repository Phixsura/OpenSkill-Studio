from app.services.app_marketplace_badge_system import BadgeSystem


def test_first_extension_badge():
    bs = BadgeSystem()
    awards = bs.check_and_award("dev-1", {"extension_count": 1})
    badge_ids = [a.badge.badge_id for a in awards]
    assert "first_extension" in badge_ids
    assert "security_clean" in badge_ids  # also earned (0 incidents + 1 ext)


def test_popular_badges():
    bs = BadgeSystem()
    awards = bs.check_and_award("dev-2", {"extension_count": 1, "total_downloads": 150000})
    badge_ids = [a.badge.badge_id for a in awards]
    assert "popular_10k" in badge_ids
    assert "popular_100k" in badge_ids


def test_no_duplicate_awards():
    bs = BadgeSystem()
    bs.check_and_award("dev-3", {"extension_count": 1})
    second = bs.check_and_award("dev-3", {"extension_count": 2})
    # first_extension already awarded, shouldn't be re-awarded
    assert not any(a.badge.badge_id == "first_extension" for a in second)


def test_get_badges():
    bs = BadgeSystem()
    bs.check_and_award("dev-4", {"extension_count": 1, "avg_rating": 4.8, "review_count": 10})
    badges = bs.get_badges("dev-4")
    assert len(badges) >= 2
    assert bs.has_badge("dev-4", "top_rated") is True


def test_veteran_badge():
    bs = BadgeSystem()
    bs.check_and_award("dev-5", {"extension_count": 1, "account_age_days": 400})
    assert bs.has_badge("dev-5", "veteran") is True


def test_badge_holders():
    bs = BadgeSystem()
    bs.check_and_award("dev-a", {"extension_count": 10})
    bs.check_and_award("dev-b", {"extension_count": 10})
    holders = bs.get_badge_holders("prolific")
    assert "dev-a" in holders and "dev-b" in holders


def test_available_badges():
    bs = BadgeSystem()
    available = bs.get_available_badges()
    assert len(available) == 10
