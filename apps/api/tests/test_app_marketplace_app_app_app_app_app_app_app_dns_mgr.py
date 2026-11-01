from app.services.app_marketplace_app_app_app_app_app_app_app_dns_mgr import (
    add_record, list_records, delete_record, clear_records,
)

def test_crud():
    clear_records()
    r = add_record("app.example.com", "A", "1.2.3.4")
    assert r["added"]
    add_record("app.example.com", "CNAME", "proxy.example.com")
    assert len(list_records("app.example.com")) == 2
    delete_record("app.example.com", "A", "1.2.3.4")
    assert len(list_records("app.example.com")) == 1
    clear_records()

def test_invalid():
    clear_records()
    assert not add_record("bad!", "A", "1.2.3.4")["added"]
    assert not add_record("ok.com", "INVALID", "x")["added"]
    clear_records()
