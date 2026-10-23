from app.services.app_marketplace_app_app_app_app_app_app_app_global_error import build_error_page

def test_404():
    r = build_error_page(404, detail="Page /xyz not found", request_id="req_abc")
    assert r["status"] == 404
    assert r["title"] == "Not Found"
    assert "xyz" in r["detail"]
    assert len(r["actions"]) == 2

def test_401():
    r = build_error_page(401)
    assert r["title"] == "Unauthorized"
    assert any(a["action"] == "login" for a in r["actions"])

def test_unknown():
    r = build_error_page(418)
    assert r["title"] == "Error"
