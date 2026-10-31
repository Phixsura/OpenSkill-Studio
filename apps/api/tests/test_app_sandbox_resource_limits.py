from app.services.app_sandbox_resource_limits import get_limits, validate_limits, clamp_limits, ResourceLimits, TIER_LIMITS

def test_default():
    l = get_limits()
    assert l.memory_mb == 128

def test_premium():
    l = get_limits("premium")
    assert l.memory_mb == 512

def test_validate_ok():
    assert validate_limits(ResourceLimits()) == []

def test_validate_too_much_memory():
    assert len(validate_limits(ResourceLimits(memory_mb=99999))) > 0

def test_validate_negative():
    assert len(validate_limits(ResourceLimits(memory_mb=-1))) > 0

def test_clamp():
    r = clamp_limits(ResourceLimits(memory_mb=9999, timeout_seconds=9999), tier="standard")
    assert r.memory_mb == 128
    assert r.timeout_seconds == 30

def test_clamp_under():
    r = clamp_limits(ResourceLimits(memory_mb=64), tier="premium")
    assert r.memory_mb == 64  # Under limit, keep as-is

def test_tier_ordering():
    free = get_limits("free")
    std = get_limits("standard")
    prem = get_limits("premium")
    assert free.memory_mb <= std.memory_mb <= prem.memory_mb
