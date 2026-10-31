from app.services.app_marketplace_footer_builder import build_marketplace_footer

def test_footer():
    f = build_marketplace_footer()
    assert len(f["sections"]) == 3
    assert "Browse" in f["sections"]
    assert f["copyright"].startswith("©")

def test_links():
    f = build_marketplace_footer()
    browse = f["sections"]["Browse"]
    assert any(l["label"] == "All Apps" for l in browse)
