from app.services.app_marketplace_app_app_app_app_app_app_app_snippet_runner import (
    create_snippet, simulate_run, snippet_stats,
)

def test_run():
    s = create_snippet("python", "print('hello')\nprint('world')")
    assert s["lines"] == 2
    r = simulate_run(s)
    assert r["success"]
    assert r["exit_code"] == 0

def test_unsupported():
    s = create_snippet("cobol", "DISPLAY 'HI'")
    r = simulate_run(s)
    assert not r["success"]

def test_stats():
    snippets = [create_snippet("python", "x=1"), create_snippet("python", "y=2"),
                create_snippet("javascript", "let z=3")]
    r = snippet_stats(snippets)
    assert r["total"] == 3
    assert r["by_language"]["python"] == 2
