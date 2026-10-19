

# ── R492 (issue #43 fuzz sweep): AnalyticsBody.get ──


def test_analytics_body_supports_dict_style_get():
    """33 talent routes call body.get(...) on AnalyticsBody — BaseModel has
    no .get, so every one 500'd AttributeError on ANY request. The model now
    implements dict-style get over declared + extra fields."""
    from app.talent.schemas.requests import AnalyticsBody

    b = AnalyticsBody(**{"url": "https://x.example.com/h", "rows": [1, 2], "n": 0})
    assert b.get("url") == "https://x.example.com/h"
    assert b.get("rows") == [1, 2]
    assert b.get("n") == 0  # falsy-zero preserved, not replaced by default
    assert b.get("absent") is None
    assert b.get("absent", "fallback") == "fallback"
    assert b.get("stages", []) == []
