from app.services.app_marketplace_app_cron_expression_parser import describe_cron

def test_every_minute():
    r = describe_cron(expression="* * * * *")
    assert "Every minute" in r["description"]

def test_every_5():
    r = describe_cron(expression="*/5 * * * *")
    assert "Every 5 minutes" in r["description"]

def test_daily():
    r = describe_cron(expression="30 9 * * *")
    assert "09:30" in r["description"]

def test_weekdays():
    r = describe_cron(expression="0 8 * * 1,2,3,4,5")
    assert "Mon" in r["description"]
    assert "Fri" in r["description"]

def test_invalid():
    r = describe_cron(expression="bad")
    assert "error" in r
