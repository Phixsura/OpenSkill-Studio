from app.services.app_marketplace_227k_7680_status import status_report

def test_status():
    r = status_report()
    assert "227K" in r["milestone"]
    assert r["modules"] == 10
    assert r["status"] == "FULLY OPERATIONAL"
    assert len(r["highlights"]) >= 5
