from app.services.app_marketplace_app_app_number_formatter import format_number, format_bytes

def test_compact_k():
    assert format_number(value=5400, style="compact")["formatted"] == "5.4K"

def test_compact_m():
    assert format_number(value=2_500_000, style="compact")["formatted"] == "2.5M"

def test_currency():
    assert format_number(value=1234.5, style="currency")["formatted"] == "$1,234.50"

def test_percentage():
    assert format_number(value=99.5, style="percentage")["formatted"] == "99.5%"

def test_bytes_mb():
    r = format_bytes(bytes_val=52_428_800)
    assert r["formatted"] == "50.0 MB"

def test_bytes_gb():
    r = format_bytes(bytes_val=1_073_741_824)
    assert "1.0 GB" in r["formatted"]
