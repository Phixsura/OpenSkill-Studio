from app.services.app_marketplace_app_error_page import get_error_page

def test_404():
    r = get_error_page(status_code=404)
    assert r["title"] == "Not Found"
    assert r["icon"] == "🔍"
    assert len(r["suggestions"]) >= 2

def test_500():
    r = get_error_page(status_code=500)
    assert r["title"] == "Server Error"

def test_custom_detail():
    r = get_error_page(status_code=404, detail="App 'xyz' was not found")
    assert "xyz" in r["message"]

def test_xss():
    r = get_error_page(status_code=400, detail="<script>alert(1)</script>")
    assert "<script>" not in r["message"]

def test_unknown():
    r = get_error_page(status_code=999)
    assert r["title"] == "Server Error"  # fallback
