from app.services.app_diff_summary_formatter import format_diff_summary, format_diff_markdown

DIFF = {"permissions": {"added": ["write:cohorts"], "removed": []}, "sandbox": {"changed": True},
        "events": {"added": ["cohort.member_added"]}, "config_schema_changed": False, "breaking": False}

def test_summary():
    s = format_diff_summary(DIFF)
    assert "+1 permissions" in s
    assert "sandbox changed" in s

def test_summary_no_changes():
    assert format_diff_summary({"permissions": {"added": [], "removed": []}, "sandbox": {"changed": False}}) == "No changes"

def test_summary_breaking():
    d = {**DIFF, "breaking": True, "permissions": {"added": [], "removed": ["read:x"]}}
    assert "BREAKING" in format_diff_summary(d)

def test_markdown():
    md = format_diff_markdown(DIFF)
    assert "write:cohorts" in md

def test_markdown_empty():
    assert format_diff_markdown({"permissions": {"added": [], "removed": []}}) == "No changes"
