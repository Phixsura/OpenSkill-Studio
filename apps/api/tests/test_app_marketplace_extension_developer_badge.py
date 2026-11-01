from app.services.app_marketplace_extension_developer_badge import DeveloperBadgeService


def test_earn_first_badge():
    svc = DeveloperBadgeService()
    newly = svc.increment_metric("dev-1", "extensions_published")
    assert any(b.badge_id == "first_ext" for b in newly)
    badges = svc.get_badges("dev-1")
    assert len(badges) == 1


def test_install_milestone():
    svc = DeveloperBadgeService()
    svc.update_metric("dev-1", "max_installs", 150)
    badges = svc.get_badges("dev-1")
    badge_ids = {b.badge_id for b in badges}
    assert "popular_10" in badge_ids
    assert "popular_100" in badge_ids
    assert "popular_1000" not in badge_ids


def test_no_duplicate():
    svc = DeveloperBadgeService()
    svc.increment_metric("dev-1", "extensions_published")
    svc.increment_metric("dev-1", "extensions_published")
    badges = svc.get_badges("dev-1")
    assert len([b for b in badges if b.badge_id == "first_ext"]) == 1


def test_progress():
    svc = DeveloperBadgeService()
    svc.update_metric("dev-1", "max_installs", 50)
    progress = svc.get_progress("dev-1")
    popular_100 = next(p for p in progress if p["badge"] == "Rising Star")
    assert popular_100["percent"] == 50
    assert popular_100["earned"] is False


def test_multiple_badges():
    svc = DeveloperBadgeService()
    for _ in range(5):
        svc.increment_metric("dev-1", "extensions_published")
    svc.update_metric("dev-1", "max_installs", 100)
    badges = svc.get_badges("dev-1")
    assert len(badges) >= 4  # first_ext, prolific_5, popular_10, popular_100
