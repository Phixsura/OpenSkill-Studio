from app.services.app_marketplace_app_app_changelog_email import generate_changelog_email

def test_generate():
    changes = [
        {"type": "feature", "description": "Dark mode support"},
        {"type": "fix", "description": "Login crash fixed"},
        {"type": "breaking", "description": "Removed v1 API"},
    ]
    r = generate_changelog_email(app_name="MyApp", version="2.0.0", changes=changes, recipient_count=500)
    assert "MyApp v2.0.0" in r["subject"]
    assert r["change_count"] == 3
    assert r["has_breaking"]
    assert r["recipient_count"] == 500
    assert "Dark mode" in r["body_html"]

def test_xss():
    r = generate_changelog_email(app_name="<script>", version="1.0", changes=[], recipient_count=0)
    assert "<script>" not in r["subject"]
    assert "<script>" not in r["body_html"]
