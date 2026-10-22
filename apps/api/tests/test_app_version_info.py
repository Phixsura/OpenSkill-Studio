from app.services.app_version_info import format_version_info

def test_approved():
    v = format_version_info("1.0.0", "approved", "2026-01")
    assert v["is_approved"] is True

def test_pending():
    v = format_version_info("1.0.0", "pending", "2026-01")
    assert v["is_approved"] is False
