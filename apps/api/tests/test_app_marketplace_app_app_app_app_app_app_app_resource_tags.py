from app.services.app_marketplace_app_app_app_app_app_app_app_resource_tags import (
    tag_resource, find_by_tag, tag_stats, clear_resources,
)

def test_tag_find():
    clear_resources()
    tag_resource("app-1", {"env": "prod", "team": "platform"})
    tag_resource("app-2", {"env": "staging", "team": "platform"})
    tag_resource("db-1", {"env": "prod", "team": "data"})
    assert len(find_by_tag("env", "prod")) == 2
    assert len(find_by_tag("team", "platform")) == 2
    assert len(find_by_tag("env")) == 3
    clear_resources()

def test_stats():
    clear_resources()
    tag_resource("a", {"env": "prod"})
    tag_resource("b", {"env": "prod", "tier": "critical"})
    s = tag_stats()
    assert s["total_resources"] == 2
    assert s["unique_tags"] == 2
    assert s["tag_distribution"]["env"] == 2
    clear_resources()
