from app.services.app_marketplace_app_app_app_app_app_app_app_data_masking import mask_field, mask_record, mask_batch

def test_mask_types():
    assert mask_field("alice@example.com", "email") != "alice@example.com"
    assert "@" in mask_field("alice@example.com", "email")
    assert mask_field("1234567890", "phone").endswith("90")
    assert mask_field("123-45-6789", "ssn").endswith("6789")
    assert mask_field("4111111111111234", "card").endswith("1234")

def test_record():
    r = mask_record(
        {"name": "Alice", "email": "alice@test.com", "age": 30},
        {"email": "email"}
    )
    assert r["name"] == "Alice"
    assert r["age"] == 30
    assert r["email"] != "alice@test.com"

def test_batch():
    r = mask_batch(
        [{"name": "A", "ssn": "123-45-6789"}],
        {"ssn": "ssn"}
    )
    assert r["total"] == 1
    assert r["records"][0]["ssn"].endswith("6789")
