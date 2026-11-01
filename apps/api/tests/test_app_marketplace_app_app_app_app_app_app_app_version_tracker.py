from app.services.app_marketplace_app_app_app_app_app_app_app_version_tracker import check_versions

def test_versions():
    r = check_versions([
        {"name": "Next.js", "current": "15.0.0", "latest": "15.1.0"},
        {"name": "React", "current": "18.3.1", "latest": "18.3.1"},
        {"name": "FastAPI", "current": "0.115.0", "latest": "1.0.0"},
    ])
    assert r["total"] == 3
    assert r["updates_available"] == 2
    assert not r["all_current"]
    nextjs = next(c for c in r["components"] if c["name"] == "Next.js")
    assert nextjs["update_type"] == "minor"
    fastapi = next(c for c in r["components"] if c["name"] == "FastAPI")
    assert fastapi["update_type"] == "major"
