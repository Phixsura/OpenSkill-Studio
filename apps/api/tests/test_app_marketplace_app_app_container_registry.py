from app.services.app_marketplace_app_app_container_registry import validate_image_ref, build_image_list

def test_valid_ref():
    r = validate_image_ref(image="myapp/api", tag="v2.1.0")
    assert r["valid"]
    assert r["ref"] == "myapp/api:v2.1.0"

def test_invalid_image():
    r = validate_image_ref(image="INVALID NAME!", tag="latest")
    assert not r["valid"]

def test_image_list():
    images = [
        {"name": "api", "tag": "v1", "size_mb": 150, "pushed_at": "2026-01-01", "pull_count": 500},
        {"name": "web", "tag": "latest", "size_mb": 80, "pushed_at": "2026-01-02", "pull_count": 300},
    ]
    r = build_image_list(images=images)
    assert r["total"] == 2
    assert r["total_size_mb"] == 230
    assert r["images"][0]["name"] == "web"  # newest first
