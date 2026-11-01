from app.services.app_marketplace_app_app_app_app_app_app_app_mock_resp import build_mock_response, mock_collection

def test_build():
    r = build_mock_response("/api/users", "GET", 200, {"users": []})
    assert r["method"] == "GET"
    assert r["status"] == 200
    assert r["headers"]["x-mock"] == "true"

def test_collection():
    mocks = [build_mock_response("/a", "GET"), build_mock_response("/a", "POST"), build_mock_response("/b", "GET")]
    r = mock_collection(mocks)
    assert r["total"] == 3
    assert r["by_method"]["GET"] == 2
    assert len(r["paths"]) == 2
