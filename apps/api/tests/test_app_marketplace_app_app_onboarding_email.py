from app.services.app_marketplace_app_app_onboarding_email import generate_welcome_email, generate_day_3_email

def test_welcome():
    r = generate_welcome_email(developer_name="Alice", plan="pro")
    assert "Alice" in r["subject"]
    assert len(r["steps"]) == 4
    assert r["plan"] == "pro"

def test_xss():
    r = generate_welcome_email(developer_name="<script>xss</script>", plan="free")
    assert "<script>" not in r["subject"]

def test_day3_no_apps():
    r = generate_day_3_email(developer_name="Bob", apps_created=0)
    assert "haven't created" in r["message"]
    assert r["cta"] == "Create Your First App"

def test_day3_one_app():
    r = generate_day_3_email(developer_name="Carol", apps_created=1)
    assert "first app" in r["message"]
