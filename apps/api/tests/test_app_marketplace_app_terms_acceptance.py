from app.services.app_marketplace_app_terms_acceptance import get_current_terms, record_acceptance, check_acceptance

def test_get_tos():
    r = get_current_terms(document_type="tos")
    assert r["version"] == "2.1"
    assert r["title"] == "Terms of Service"

def test_unknown():
    r = get_current_terms(document_type="eula")
    assert "error" in r

def test_record():
    r = record_acceptance(user_id="u1", document_type="tos", version="2.1", ip_address="1.2.3.4")
    assert r["acceptance_id"].startswith("acc_")

def test_check_all():
    accepted = [{"document_type": "tos", "version": "2.1"}, {"document_type": "privacy", "version": "1.5"}]
    required = [{"document_type": "tos", "version": "2.1"}, {"document_type": "privacy", "version": "1.5"}]
    r = check_acceptance(user_acceptances=accepted, required=required)
    assert r["all_accepted"]

def test_check_pending():
    accepted = [{"document_type": "tos", "version": "2.0"}]
    required = [{"document_type": "tos", "version": "2.1"}]
    r = check_acceptance(user_acceptances=accepted, required=required)
    assert not r["all_accepted"]
    assert r["pending_count"] == 1
