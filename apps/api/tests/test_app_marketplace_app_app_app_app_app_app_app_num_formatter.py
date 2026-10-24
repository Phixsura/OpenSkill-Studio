from app.services.app_marketplace_app_app_app_app_app_app_app_num_formatter import format_compact, format_currency, format_percentage, format_bytes

def test_compact():
    assert format_compact(500) == "500"
    assert format_compact(1500) == "1.5K"
    assert format_compact(2500000) == "2.5M"
    assert format_compact(1200000000) == "1.2B"

def test_currency():
    assert format_currency(29.99) == "$29.99"
    assert format_currency(1500) == "$1,500"
    assert format_currency(2500000) == "$2.5M"
    assert format_currency(99, currency="EUR") == "€99.00"

def test_percentage():
    assert format_percentage(99.95) == "100.0%"
    assert format_percentage(100, decimals=0) == "100%"

def test_bytes():
    assert format_bytes(500) == "500 B"
    assert format_bytes(1536) == "1.5 KB"
    assert format_bytes(1073741824) == "1.0 GB"
