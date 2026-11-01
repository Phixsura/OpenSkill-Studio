from app.services.app_developer_api_key_summary import build_key_summary

def test_summary():
    keys = [{"revoked": False, "expired": False, "total_calls": 100},
            {"revoked": True, "expired": False, "total_calls": 50}]
    s = build_key_summary(keys)
    assert s["active"] == 1
    assert s["total_api_calls"] == 150

def test_empty():
    s = build_key_summary([])
    assert s["total"] == 0
