from app.services.app_execution_timeline import build_execution_timeline

EXECS = [
    {"created_at": "2026-01-01T10:00:00Z", "duration_ms": 100, "success": True},
    {"created_at": "2026-01-01T10:30:00Z", "duration_ms": 200, "success": True},
    {"created_at": "2026-01-01T11:00:00Z", "duration_ms": 5000, "success": False},
]

def test_by_hour():
    tl = build_execution_timeline(EXECS, group_by="hour")
    assert len(tl) == 2  # two hours

def test_by_day():
    tl = build_execution_timeline(EXECS, group_by="day")
    assert len(tl) == 1  # one day

def test_stats():
    tl = build_execution_timeline(EXECS, group_by="hour")
    first = tl[0]
    assert first["total"] == 2
    assert first["avg_ms"] == 150.0

def test_empty():
    assert build_execution_timeline([]) == []
