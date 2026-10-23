from app.services.app_marketplace_terms_page import build_legal_page, get_legal_pages_index

def test_terms():
    p = build_legal_page(page_id="terms")
    assert p["title"] == "Terms of Service"
    assert p["section_count"] == 10

def test_privacy():
    p = build_legal_page(page_id="privacy")
    assert p["title"] == "Privacy Policy"

def test_unknown():
    assert build_legal_page(page_id="nope") is None

def test_index():
    idx = get_legal_pages_index()
    assert len(idx) == 4
    assert any(p["id"] == "developer_agreement" for p in idx)
