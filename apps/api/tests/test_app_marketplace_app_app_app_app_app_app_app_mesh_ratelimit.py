from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_ratelimit import MeshRateLimiter

def test_limit():
    mrl = MeshRateLimiter()
    mrl.set_limit("web", "api", rpm=3)
    assert mrl.allow("web", "api", now=100)["allowed"]
    assert mrl.allow("web", "api", now=100)["allowed"]
    assert mrl.allow("web", "api", now=100)["allowed"]
    assert not mrl.allow("web", "api", now=100)["allowed"]
    # New window
    assert mrl.allow("web", "api", now=161)["allowed"]

def test_no_limit():
    mrl = MeshRateLimiter()
    assert mrl.allow("x", "y")["allowed"]
    assert mrl.allow("x", "y")["reason"] == "no_limit"
