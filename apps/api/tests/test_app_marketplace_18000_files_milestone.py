from app.services.app_marketplace_18000_files_milestone import celebrate_approaching_18000
def test_18k():
    r = celebrate_approaching_18000()
    assert "18,000" in r["milestone"]
