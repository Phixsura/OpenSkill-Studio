from app.services.app_marketplace_extension_screenshot_mgr import ExtScreenshotMgrService

def test_upload():
    svc = ExtScreenshotMgrService()
    ss = svc.upload("ext-1", "https://cdn.example.com/shot1.png", "Home page")
    assert ss.caption == "Home page"
    assert len(svc.get_all("ext-1")) == 1

def test_invalid_type():
    svc = ExtScreenshotMgrService()
    try:
        svc.upload("ext-1", "https://cdn.example.com/file.exe")
        assert False
    except ValueError:
        pass

def test_max_limit():
    svc = ExtScreenshotMgrService()
    for i in range(10):
        svc.upload("ext-1", f"https://cdn.example.com/s{i}.png")
    try:
        svc.upload("ext-1", "https://cdn.example.com/s11.png")
        assert False
    except ValueError:
        pass

def test_delete():
    svc = ExtScreenshotMgrService()
    ss = svc.upload("ext-1", "https://cdn.example.com/shot.jpg")
    assert svc.delete("ext-1", ss.screenshot_id) is True
    assert len(svc.get_all("ext-1")) == 0
