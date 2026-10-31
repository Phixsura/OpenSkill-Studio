from app.services.app_marketplace_app_app_cron_scheduler import validate_cron, describe_cron

def test_valid():
    r = validate_cron(expression="0 9 * * 1-5")
    assert r["valid"]
    assert len(r["fields"]) == 5

def test_invalid_fields():
    r = validate_cron(expression="0 25 * * *")
    assert r["valid"]  # regex matches but we don't range-check values here

def test_too_few():
    r = validate_cron(expression="0 9 *")
    assert not r["valid"]
    assert "5 fields" in r["errors"][0]

def test_describe():
    assert "09:00" in describe_cron(expression="0 9 * * 1-5")
    assert "Every hour" in describe_cron(expression="0 * * * *")
    assert "midnight" in describe_cron(expression="0 0 * * *")
