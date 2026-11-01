from app.services.app_marketplace_app_app_app_app_app_app_app_container_reg import (
    push_image, list_images, get_image, delete_image, registry_stats, clear_registry,
)

def test_push_and_list():
    clear_registry()
    push_image("myapp", "latest", 150.0, layers=5)
    push_image("myapp", "v2.0", 145.0, layers=5)
    push_image("worker", "latest", 80.0, layers=3)
    assert len(list_images("myapp")) == 2
    assert len(list_images()) == 3
    img = get_image("myapp", "latest")
    assert img is not None
    assert img["digest"].startswith("sha256:")
    clear_registry()

def test_stats():
    clear_registry()
    push_image("a", "v1", 100.0)
    push_image("b", "v1", 200.0)
    s = registry_stats()
    assert s["total_images"] == 2
    assert s["total_size_mb"] == 300.0
    assert s["repositories"] == 2
    clear_registry()
