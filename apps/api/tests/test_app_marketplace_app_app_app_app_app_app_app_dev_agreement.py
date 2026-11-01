from app.services.app_marketplace_app_app_app_app_app_app_app_dev_agreement import check_agreements, accept_agreement

def test_check():
    r = check_agreements({"developer_tos": "2.0", "marketplace_guidelines": "1.5",
                            "data_processing": "1.0"})
    assert r["all_accepted"]
    assert len(r["missing_required"]) == 0

def test_missing():
    r = check_agreements({"developer_tos": "1.0"})  # outdated
    assert not r["all_accepted"]
    assert len(r["missing_required"]) > 0

def test_accept():
    r = accept_agreement("developer_tos")
    assert r["version"] == "2.0"
    assert r["accepted"] == "developer_tos"
