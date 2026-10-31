from app.services.app_marketplace_app_event_bus import publish_event, subscribe, get_topic_stats

def test_publish():
    r = publish_event(topic="app.installed", payload={"app_id": "a1"}, source="marketplace")
    assert r["event_id"].startswith("ev_")
    assert r["status"] == "published"

def test_subscribe():
    r = subscribe(topic="app.installed", subscriber_id="wh1", endpoint="https://x.com/hook")
    assert r["subscription_id"].startswith("sub_")
    assert r["status"] == "active"

def test_stats():
    topics = [{"name": "app.installed", "subscriber_count": 5, "events_24h": 120},
              {"name": "review.created", "subscriber_count": 3, "events_24h": 45}]
    r = get_topic_stats(topics=topics)
    assert r["total_topics"] == 2
    assert r["total_events_24h"] == 165
