from app.services.app_metrics_timeline import generate_daily_timeline, aggregate_timeline

def test_length():
    tl = generate_daily_timeline(days=7)
    assert len(tl) == 7

def test_ordered():
    tl = generate_daily_timeline(days=5)
    dates = [p["date"] for p in tl]
    assert dates == sorted(dates)

def test_with_data():
    from datetime import UTC, datetime
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    tl = generate_daily_timeline(days=1, data_points={today: 42})
    assert tl[0]["value"] == 42

def test_aggregate():
    t1 = [{"date": "2026-01-01", "value": 10}]
    t2 = [{"date": "2026-01-01", "value": 20}]
    agg = aggregate_timeline([t1, t2])
    assert agg[0]["value"] == 30
