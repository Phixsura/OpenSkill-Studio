from app.services.app_marketplace_17000_files_milestone import celebrate_17000_files
def test_17k():
    r = celebrate_17000_files()
    assert "17,000" in r["milestone"]
    assert r["files"] >= 17000
