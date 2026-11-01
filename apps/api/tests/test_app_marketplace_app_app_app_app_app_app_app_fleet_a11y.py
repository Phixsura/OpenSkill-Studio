from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_a11y import fleet_accessibility
def test_a11y():
    r = fleet_accessibility([{"wcag_aa": True, "wcag_aaa": True}, {"wcag_aa": True}, {"wcag_aa": False}])
    assert r["wcag_aa"] == 2
    assert r["score"] == 66.7
    assert not r["compliant"]
