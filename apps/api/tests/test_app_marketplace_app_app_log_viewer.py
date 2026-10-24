from app.services.app_marketplace_app_app_log_viewer import parse_log_lines

LINES = [
    "2026-01-01T10:00:00 INFO App started",
    "2026-01-01T10:00:01 DEBUG Loading config",
    "2026-01-01T10:00:05 ERROR Connection refused",
    "2026-01-01T10:00:06 WARN High memory usage",
]

def test_parse_all():
    r = parse_log_lines(lines=LINES)
    assert r["total"] == 4
    assert r["error_count"] == 1
    assert r["has_errors"]

def test_filter_level():
    r = parse_log_lines(lines=LINES, min_level="WARN")
    assert r["total"] == 2

def test_xss():
    r = parse_log_lines(lines=["<script>alert(1)</script> ERROR bad"])
    assert "<script>" not in r["entries"][0]["raw"]
