from app.services.app_marketplace_app_app_dns_record import validate_record, build_dns_table

def test_valid():
    r = validate_record(record_type="A", name="@", value="1.2.3.4")
    assert r["valid"]

def test_invalid_type():
    r = validate_record(record_type="INVALID", name="@", value="x")
    assert not r["valid"]

def test_table():
    records = [
        {"type": "A", "name": "@", "value": "1.2.3.4"},
        {"type": "CNAME", "name": "www", "value": "example.com"},
        {"type": "A", "name": "api", "value": "5.6.7.8"},
    ]
    r = build_dns_table(records=records)
    assert r["total"] == 3
    assert r["by_type"]["A"] == 2
