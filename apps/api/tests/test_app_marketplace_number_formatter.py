from app.services.app_marketplace_number_formatter import format_compact, format_currency, format_percentage, format_bytes, format_duration

def test_compact():
    assert format_compact(value=500) == "500"
    assert format_compact(value=1500) == "1.5K"
    assert format_compact(value=2500000) == "2.5M"

def test_currency():
    assert format_currency(cents=9900) == "$99.00"
    assert format_currency(cents=150000, currency="EUR") == "€1,500.00"

def test_percentage():
    assert format_percentage(value=85.3) == "85.3%"
    assert format_percentage(value=50, decimals=0) == "50%"

def test_bytes():
    assert format_bytes(bytes_val=512) == "512 B"
    assert format_bytes(bytes_val=5120) == "5.0 KB"
    assert format_bytes(bytes_val=5242880) == "5.0 MB"

def test_duration():
    assert format_duration(seconds=45) == "45s"
    assert format_duration(seconds=125) == "2m 5s"
    assert format_duration(seconds=3661) == "1h 1m"
    assert format_duration(seconds=90000) == "1d 1h"
