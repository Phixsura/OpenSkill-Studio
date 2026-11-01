from app.services.app_marketplace_extension_rate_plan import RatePlanService


def test_default_free_plan():
    rps = RatePlanService()
    limits = rps.get_effective_limits("new-org")
    assert limits["plan"] == "Free"
    assert limits["limits"]["requests_per_minute"] == 60


def test_assign_plan():
    rps = RatePlanService()
    assert rps.assign_plan("org-1", "pro") is True
    limits = rps.get_effective_limits("org-1")
    assert limits["plan"] == "Professional"
    assert limits["limits"]["requests_per_minute"] == 1000


def test_override():
    rps = RatePlanService()
    rps.assign_plan("org-2", "starter")
    rps.set_override("org-2", {"requests_per_minute": 500})
    limits = rps.get_effective_limits("org-2")
    assert limits["limits"]["requests_per_minute"] == 500
    assert limits["has_overrides"] is True


def test_compare_plans():
    rps = RatePlanService()
    comp = rps.compare_plans("free", "enterprise")
    assert comp["differences"]["requests_per_minute"]["a"] == 60
    assert comp["differences"]["requests_per_minute"]["b"] == 5000


def test_list_plans():
    rps = RatePlanService()
    plans = rps.list_plans()
    assert len(plans) == 4
    names = {p["name"] for p in plans}
    assert "Free" in names and "Enterprise" in names


def test_invalid_plan():
    rps = RatePlanService()
    assert rps.assign_plan("org-3", "nonexistent") is False
