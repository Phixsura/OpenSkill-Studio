from app.services.app_marketplace_app_app_app_app_app_app_app_date_formatter import format_relative, format_duration, format_number

def test_relative():
    assert format_relative(30) == "just now"
    assert format_relative(300) == "5m ago"
    assert format_relative(7200) == "2h ago"
    assert format_relative(172800) == "2d ago"
    assert format_relative(1209600) == "2w ago"

def test_duration():
    assert format_duration(0.5) == "500ms"
    assert format_duration(45) == "45.0s"
    assert format_duration(125) == "2m 5s"
    assert format_duration(3700) == "1h 1m"

def test_number():
    assert format_number(500) == "500"
    assert format_number(1500) == "1.5K"
    assert format_number(2500000) == "2.5M"
