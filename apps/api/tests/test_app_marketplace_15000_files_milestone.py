from app.services.app_marketplace_15000_files_milestone import celebrate_15000_files
def test_15k():
    assert "15,000" in celebrate_15000_files()["milestone"]
