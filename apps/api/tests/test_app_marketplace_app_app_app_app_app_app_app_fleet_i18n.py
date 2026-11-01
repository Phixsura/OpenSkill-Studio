from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_i18n import fleet_i18n_coverage
def test_i18n():
    r = fleet_i18n_coverage([{"translated": True, "lang": "ja"}, {"translated": True, "lang": "zh"}, {"translated": False}])
    assert r["coverage_pct"] == 66.7
    assert r["languages"] == 2
    assert not r["ready"]
