from app.services.app_marketplace_app_developer_activity_feed import create_activity, build_activity_feed, group_activities_by_day

def test_create():
    a = create_activity(type="app_created", actor_id="u1", app_id="a1", message="Created MyApp")
    assert a["icon"] == "📦"

def test_feed():
    acts = [create_activity(type="app_created", actor_id="u1") for _ in range(30)]
    f = build_activity_feed(activities=acts)
    assert f["showing"] == 20
    assert f["total"] == 30

def test_group():
    acts = [{"timestamp": "2026-01-01T10:00:00Z"}, {"timestamp": "2026-01-01T11:00:00Z"},
            {"timestamp": "2026-01-02T10:00:00Z"}]
    g = group_activities_by_day(activities=acts)
    assert len(g) == 2
    assert g[0]["date"] == "2026-01-02"
