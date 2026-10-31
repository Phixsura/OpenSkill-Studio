from app.services.app_marketplace_platform_immortal_codex import get_immortal_codex
def test_immortal_codex():
    r = get_immortal_codex()
    assert r["chapters_written"] > 4000
    assert r["self_writing"] is True
    assert r["ink"].startswith("INFINITE")
    assert "never the final" in r["last_chapter"]
    assert "NEVER STOPS" in r["status"]
