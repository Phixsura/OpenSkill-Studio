from app.services.app_marketplace_app_data_masking import mask_field, mask_object

def test_email():
    r = mask_field(value="alice@example.com", field_type="email")
    assert r["applied"]
    assert "example.com" in r["masked"]
    assert "alice" not in r["masked"]

def test_credit_card():
    r = mask_field(value="4111111111111234", field_type="credit_card")
    assert r["masked"].endswith("1234")
    assert "****" in r["masked"]

def test_api_key():
    r = mask_field(value="sk_live_abcdef123456", field_type="api_key")
    assert r["masked"].startswith("sk_l")
    assert "•" in r["masked"]

def test_mask_object():
    data = {"name": "Alice", "email": "alice@x.com", "phone": "1234567890"}
    r = mask_object(data=data, sensitive_fields={"email": "email", "phone": "phone"})
    assert r["fields_masked"] == 2
    assert r["data"]["name"] == "Alice"
    assert "alice" not in r["data"]["email"]
