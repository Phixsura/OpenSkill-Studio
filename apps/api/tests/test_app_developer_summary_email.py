from app.services.app_developer_summary_email import build_summary_email

def test_email():
    e = build_summary_email(developer_name="Alice", app_count=3, total_installs_week=50, total_errors_week=2)
    assert "Alice" in e["greeting"]
    assert e["stats"]["new_installs"] == 50
    assert "Weekly" in e["subject"]
