from app.services.app_marketplace_app_app_app_app_app_app_app_complete_footer import build_complete_footer

def test_footer():
    r = build_complete_footer()
    assert r["brand"]["name"] == "OpenSkill"
    assert len(r["sections"]) == 4
    assert len(r["social"]) == 4
    assert len(r["badges"]) == 3
    assert "©" in r["copyright"]
    assert "Product" in r["sections"]
