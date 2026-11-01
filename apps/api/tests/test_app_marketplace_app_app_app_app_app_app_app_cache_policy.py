from app.services.app_marketplace_app_app_app_app_app_app_app_cache_policy import CachePolicyManager

def test_policy():
    cpm = CachePolicyManager()
    cpm.set_policy("/api/users", 300, vary_by=["Authorization"])
    h = cpm.cache_headers("/api/users")
    assert h["cacheable"]
    assert "max-age=300" in h["Cache-Control"]
    assert h["Vary"] == "Authorization"

def test_no_cache():
    cpm = CachePolicyManager()
    cpm.set_policy("/api/auth", 0, cacheable=False)
    h = cpm.cache_headers("/api/auth")
    assert not h["cacheable"]
    assert h["Cache-Control"] == "no-store"

def test_default():
    cpm = CachePolicyManager()
    h = cpm.cache_headers("/unknown")
    assert not h["cacheable"]
