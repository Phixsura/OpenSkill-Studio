from app.services.app_marketplace_app_developer_changelog_aggregator import aggregate_changelogs, group_by_month

def test_aggregate():
    r = aggregate_changelogs(apps_changelogs={
        "App A": [{"version": "2.0", "released_at": "2026-06-01"}],
        "App B": [{"version": "1.0", "released_at": "2026-07-01"}],
    })
    assert r[0]["app_name"] == "App B"  # newest first

def test_group():
    entries = [{"released_at": "2026-06-01"}, {"released_at": "2026-06-15"}, {"released_at": "2026-07-01"}]
    g = group_by_month(entries=entries)
    assert g[0]["month"] == "2026-07"
    assert g[1]["count"] == 2
