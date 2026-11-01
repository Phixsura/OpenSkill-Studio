from app.services.app_marketplace_app_app_app_app_app_app_app_api_mock import (
    register_mock, match_mock, mock_stats, clear_mocks,
)

def test_register_match():
    clear_mocks()
    register_mock("GET", "/api/users", 200, {"users": []})
    r = match_mock("GET", "/api/users")
    assert r["matched"]
    assert r["status"] == 200
    assert r["body"]["users"] == []
    r2 = match_mock("POST", "/api/missing")
    assert not r2["matched"]
    clear_mocks()

def test_stats():
    clear_mocks()
    register_mock("GET", "/a", 200)
    match_mock("GET", "/a")
    match_mock("GET", "/a")
    s = mock_stats()
    assert s["total_mocks"] == 1
    assert s["total_hits"] == 2
    clear_mocks()
