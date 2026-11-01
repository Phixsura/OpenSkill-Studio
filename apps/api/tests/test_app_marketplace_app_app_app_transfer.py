from app.services.app_marketplace_app_app_app_transfer import initiate_transfer, build_transfer_status

def test_initiate():
    r = initiate_transfer(app_id="a1", from_org="Acme", to_org="NewCo", initiated_by="Alice")
    assert r["transfer_id"].startswith("xfr_")
    assert r["status"] == "pending_acceptance"
    assert len(r["token"]) > 20

def test_status():
    transfers = [{"status": "pending_acceptance"}, {"status": "completed"}, {"status": "completed"}]
    r = build_transfer_status(transfers=transfers)
    assert r["pending"] == 1
    assert r["completed"] == 2
    assert r["has_pending"]
