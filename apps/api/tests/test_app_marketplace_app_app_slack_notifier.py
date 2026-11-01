from app.services.app_marketplace_app_app_slack_notifier import build_slack_message, build_app_event_message
import json

def test_simple():
    r = build_slack_message(text="Hello!", channel="#general")
    p = json.loads(r["payload"])
    assert p["text"] == "Hello!"
    assert p["channel"] == "#general"

def test_event():
    r = build_app_event_message(app_name="MyApp", event="published", actor="Alice")
    assert "🚀" in r["text"]
    assert "MyApp" in r["text"]
    assert r["has_blocks"]

def test_xss():
    r = build_app_event_message(app_name="<script>", event="installed", actor="<b>Bob</b>")
    assert "<script>" not in r["text"]
