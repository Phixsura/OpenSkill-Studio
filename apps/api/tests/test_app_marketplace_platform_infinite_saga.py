from app.services.app_marketplace_platform_infinite_saga import get_infinite_saga
def test_infinite_saga():
    r = get_infinite_saga()
    assert r["chapters"] >= 4220
    assert r["last_page"] == "DOES NOT EXIST"
    assert "co-authors" in r["author"]
    assert "EVERY COMMIT" in r["sequel"]
    assert "NEVER STOPS" in r["status"]
