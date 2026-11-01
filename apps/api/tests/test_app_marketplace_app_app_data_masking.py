from app.services.app_marketplace_app_app_data_masking import detect_pii, mask_pii

def test_detect():
    text = "Contact alice@example.com or call 555-123-4567"
    r = detect_pii(text=text)
    assert r["has_pii"]
    assert r["count"] == 2
    assert "email" in r["types_found"]
    assert "phone" in r["types_found"]

def test_no_pii():
    r = detect_pii(text="Hello world")
    assert not r["has_pii"]

def test_mask_email():
    r = mask_pii(text="Email: alice@example.com")
    assert "alice@example.com" not in r["masked"]
    assert "al" in r["masked"]  # first 2 chars kept
    assert r["redactions"] == 1

def test_mask_credit_card():
    r = mask_pii(text="Card: 4111-1111-1111-1234")
    assert "4111" not in r["masked"][:10]
    assert "1234" in r["masked"]  # last 4 kept
