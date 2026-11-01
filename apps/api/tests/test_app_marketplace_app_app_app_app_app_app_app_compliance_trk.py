from app.services.app_marketplace_app_app_app_app_app_app_app_compliance_trk import track_compliance

def test_compliance():
    r = track_compliance({
        "SOC2": {"passed": 10, "total": 10},
        "GDPR": {"passed": 8, "total": 10},
        "HIPAA": {"passed": 15, "total": 15},
    })
    assert r["overall_pct"] == 94
    assert not r["all_compliant"]  # GDPR not 100%
    assert r["frameworks"]["SOC2"]["compliant"]
    assert not r["frameworks"]["GDPR"]["compliant"]
