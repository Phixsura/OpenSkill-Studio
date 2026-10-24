from app.services.app_marketplace_complete_install_page import build_complete_install_page

def test_full():
    p = build_complete_install_page(
        app={"name": "SuperApp"}, developer={"display_name": "DevCo", "verified": True},
        install_guard={"can_install": True, "blockers": [], "warnings": []},
        permissions={"required": ["read"], "optional": ["write"]},
        config_schema={"fields": [{"name": "url"}]},
        reviews_summary={"avg_rating": 4.5, "install_count": 2000},
        related_apps=[{"id": "r1"}])
    assert p["page_type"] == "complete_install"
    assert p["cta"]["enabled"]
    assert len(p["steps"]) == 3  # permissions + config + confirm

def test_no_config():
    p = build_complete_install_page(
        app={"name": "App"}, developer={}, install_guard={"can_install": True},
        permissions={}, config_schema=None, reviews_summary={}, related_apps=[])
    assert len(p["steps"]) == 2  # no config step

def test_blocked():
    p = build_complete_install_page(
        app={"name": "App"}, developer={},
        install_guard={"can_install": False, "blockers": [{"message": "Conflict"}]},
        permissions={}, config_schema=None, reviews_summary={}, related_apps=[])
    assert not p["cta"]["enabled"]
    assert p["cta"]["label"] == "Cannot Install"
