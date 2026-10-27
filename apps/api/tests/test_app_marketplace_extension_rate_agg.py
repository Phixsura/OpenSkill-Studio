from app.services.app_marketplace_extension_rate_agg import RateAggregatorService


def test_single_level():
    ra = RateAggregatorService()
    ra.define_level("global", "global", max_per_second=100, burst=10)
    ra.define_chain("api", ["global"])
    result = ra.check("api")
    assert result["allowed"] is True
    assert result["remaining"]["global"] == 9.0


def test_multi_level_pass():
    ra = RateAggregatorService()
    ra.define_level("global", "global", 1000, 100)
    ra.define_level("user", "user:123", 10, 5)
    ra.define_chain("api", ["global", "user:123"])
    result = ra.check("api")
    assert result["allowed"] is True


def test_user_level_blocked():
    ra = RateAggregatorService()
    ra.define_level("global", "global", 1000, 100)
    ra.define_level("user", "user:123", 0.001, 2)
    ra.define_chain("api", ["global", "user:123"])
    ra.check("api")
    ra.check("api")
    result = ra.check("api")  # user bucket empty
    assert result["allowed"] is False
    assert result["blocked_by"] == "user"


def test_global_level_blocked():
    ra = RateAggregatorService()
    ra.define_level("global", "global", 0.001, 2)
    ra.define_level("user", "user:123", 1000, 100)
    ra.define_chain("api", ["global", "user:123"])
    ra.check("api")
    ra.check("api")
    result = ra.check("api")
    assert result["allowed"] is False
    assert result["blocked_by"] == "global"


def test_retry_after():
    ra = RateAggregatorService()
    ra.define_level("limit", "limit", 1.0, 1)
    ra.define_chain("c", ["limit"])
    ra.check("c")  # consume the one token
    result = ra.check("c")
    assert result["allowed"] is False
    assert result["retry_after_ms"] > 0


def test_independent_chains():
    ra = RateAggregatorService()
    ra.define_level("user_a", "user:a", 0.001, 2)
    ra.define_level("user_b", "user:b", 0.001, 2)
    ra.define_chain("chain_a", ["user:a"])
    ra.define_chain("chain_b", ["user:b"])
    ra.check("chain_a"); ra.check("chain_a")
    assert ra.check("chain_a")["allowed"] is False
    assert ra.check("chain_b")["allowed"] is True  # independent


def test_adjust_limit():
    ra = RateAggregatorService()
    ra.define_level("api", "api", 10, 5)
    ra.adjust_limit("api", max_per_second=100, burst=50)
    level = ra._levels["api"]
    assert level.max_per_second == 100
    assert level.burst == 50


def test_stats():
    ra = RateAggregatorService()
    ra.define_level("g", "g", 1000, 100)
    ra.define_chain("c", ["g"])
    ra.check("c")
    ra.check("c")
    stats = ra.get_stats()
    assert stats["total_allowed"] == 2
    assert stats["levels"] == 1
