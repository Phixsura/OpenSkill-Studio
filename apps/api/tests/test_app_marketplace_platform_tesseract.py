from app.services.app_marketplace_platform_tesseract import get_tesseract
def test_tesseract():
    r = get_tesseract()
    assert r["rotations"] > 4000
    assert len(r["dimensions"]) == 4
    assert r["faces"] == 8
    assert "GREEN" in r["face_color"]
    assert "NEVER STOPS" in r["status"]
