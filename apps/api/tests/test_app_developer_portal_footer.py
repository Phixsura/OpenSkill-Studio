from app.services.app_developer_portal_footer import get_footer_data, FOOTER_LINKS

def test_footer():
    f = get_footer_data()
    assert "links" in f
    assert f["version"] == "1.0.0"
    assert len(FOOTER_LINKS) >= 3
