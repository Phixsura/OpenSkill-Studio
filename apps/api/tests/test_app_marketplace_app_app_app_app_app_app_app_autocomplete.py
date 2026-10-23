from app.services.app_marketplace_app_app_app_app_app_app_app_autocomplete import build_suggestions

def test_autocomplete():
    r = build_suggestions("sl", apps=["Slack Bot", "Slack Notifier", "GitHub Sync"],
                            categories=["tools"], developers=["Slack Inc"])
    assert r["total"] == 3  # 2 apps + 1 developer
    assert all(s["text"].lower().startswith("sl") or "sl" in s["text"].lower() for s in r["suggestions"])

def test_empty():
    r = build_suggestions("", apps=["A"], categories=["B"], developers=["C"])
    assert len(r["suggestions"]) == 0
