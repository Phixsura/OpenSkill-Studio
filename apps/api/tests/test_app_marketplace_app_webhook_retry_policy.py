from app.services.app_marketplace_app_webhook_retry_policy import create_retry_policy

def test_exponential():
    r = create_retry_policy(strategy="exponential", max_retries=4, initial_delay_sec=10)
    assert r["schedule"][0]["delay_sec"] == 10
    assert r["schedule"][1]["delay_sec"] == 20
    assert r["schedule"][2]["delay_sec"] == 40
    assert r["schedule"][3]["delay_sec"] == 80

def test_linear():
    r = create_retry_policy(strategy="linear", max_retries=3, initial_delay_sec=60)
    assert r["schedule"][0]["delay_sec"] == 60
    assert r["schedule"][1]["delay_sec"] == 120
    assert r["schedule"][2]["delay_sec"] == 180

def test_fixed():
    r = create_retry_policy(strategy="fixed", max_retries=3, initial_delay_sec=30)
    assert all(s["delay_sec"] == 30 for s in r["schedule"])

def test_invalid():
    r = create_retry_policy(strategy="random")
    assert "error" in r

def test_max_exceeded():
    r = create_retry_policy(max_retries=25)
    assert "error" in r
