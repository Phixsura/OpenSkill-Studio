from app.services.app_marketplace_extension_resource_limiter import ResourceLimiterService


def test_basic_request():
    rl = ResourceLimiterService()
    rl.create_group("org", limit=100)
    result = rl.request("org", 30)
    assert result["granted"] is True
    assert rl._groups["org"].used == 30


def test_limit_exceeded():
    rl = ResourceLimiterService()
    rl.create_group("org", limit=50)
    rl.request("org", 40)
    result = rl.request("org", 20)
    assert result["granted"] is False
    assert result["blocked_by"] == "org"


def test_hierarchical_limit():
    rl = ResourceLimiterService()
    rl.create_group("org", limit=100)
    rl.create_group("team-a", limit=60, parent="org")
    rl.create_group("team-b", limit=60, parent="org")
    rl.request("team-a", 50)
    rl.request("team-b", 40)
    # team-b has room (40 < 60) but org is at 90
    result = rl.request("team-b", 20)
    assert result["granted"] is False
    assert result["blocked_by"] == "org"


def test_release():
    rl = ResourceLimiterService()
    rl.create_group("org", limit=50)
    rl.request("org", 40)
    rl.release("org", 20)
    result = rl.request("org", 20)
    assert result["granted"] is True


def test_burst():
    rl = ResourceLimiterService()
    rl.create_group("api", limit=100, burst_limit=20)
    rl.request("api", 100)
    result = rl.request("api", 15)  # within burst
    assert result["granted"] is True
    result2 = rl.request("api", 10)  # over burst
    assert result2["granted"] is False


def test_fair_share():
    rl = ResourceLimiterService()
    rl.create_group("org", limit=100)
    rl.create_group("high", limit=0, parent="org", priority=3)
    rl.create_group("low", limit=0, parent="org", priority=1)
    assert rl.get_fair_share("high") == 75.0  # 3/4 of 100
    assert rl.get_fair_share("low") == 25.0  # 1/4 of 100


def test_utilization():
    rl = ResourceLimiterService()
    rl.create_group("api", limit=100)
    rl.request("api", 75)
    util = rl.get_utilization("api")
    assert util["utilization_pct"] == 75.0
    assert util["in_burst"] is False


def test_three_level_hierarchy():
    rl = ResourceLimiterService()
    rl.create_group("company", limit=1000)
    rl.create_group("engineering", limit=500, parent="company")
    rl.create_group("alice", limit=100, parent="engineering")
    result = rl.request("alice", 80)
    assert result["granted"] is True
    # Check all levels updated
    assert rl._groups["alice"].used == 80
    assert rl._groups["engineering"].used == 80
    assert rl._groups["company"].used == 80


def test_tree():
    rl = ResourceLimiterService()
    rl.create_group("root", limit=100)
    rl.create_group("a", limit=50, parent="root")
    rl.create_group("b", limit=50, parent="root")
    tree = rl.get_tree("root")
    assert "children" in tree
    assert "a" in tree["children"]
