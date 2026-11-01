from app.services.app_marketplace_app_dns_record_manager import create_dns_record, list_dns_records

def test_create_a():
    r = create_dns_record(domain="example.com", record_type="A", name="@", value="1.2.3.4")
    assert r["status"] == "active"
    assert r["fqdn"] == "example.com"

def test_create_cname():
    r = create_dns_record(domain="example.com", record_type="CNAME", name="www", value="apps.openskill.dev")
    assert r["fqdn"] == "www.example.com"

def test_invalid_type():
    r = create_dns_record(domain="x.com", record_type="PTR", name="@", value="x")
    assert "error" in r

def test_invalid_ipv4():
    r = create_dns_record(domain="x.com", record_type="A", name="@", value="not-an-ip")
    assert "error" in r

def test_list():
    r = list_dns_records(domain="example.com")
    assert r["total"] == 3
