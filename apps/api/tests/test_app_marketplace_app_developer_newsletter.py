from app.services.app_marketplace_app_developer_newsletter import generate_newsletter, build_email_subject

def test_newsletter():
    n = generate_newsletter(period="Oct 2026",
                             new_apps=[{"name": "App1", "description": "Great"}],
                             trending=[{"name": "PopularApp"}],
                             announcements=["API v3 launched"], tips=["Use webhooks"])
    assert n["section_count"] == 4
    assert n["period"] == "Oct 2026"

def test_empty():
    n = generate_newsletter(period="Oct 2026", new_apps=[], trending=[], announcements=[], tips=[])
    assert n["section_count"] == 0

def test_subject():
    s = build_email_subject(period="Oct 2026", highlight="API v3 is here!")
    assert "Oct 2026" in s
    assert "API v3" in s

def test_subject_no_highlight():
    s = build_email_subject(period="Oct 2026")
    assert "Oct 2026" in s
