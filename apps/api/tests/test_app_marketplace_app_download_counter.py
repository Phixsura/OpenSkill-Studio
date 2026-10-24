from app.services.app_marketplace_app_download_counter import record_download, get_download_stats

def test_record_get():
    record_download("dl1", version="1.0.0", platform="npm")
    record_download("dl1", version="1.0.0", platform="npm")
    record_download("dl1", version="1.0.0", platform="pip")
    s = get_download_stats("dl1")
    assert s["total"] >= 3
    assert s["by_platform"]["npm"] >= 2
    assert s["by_platform"]["pip"] >= 1

def test_empty():
    s = get_download_stats("nonexist")
    assert s["total"] == 0
