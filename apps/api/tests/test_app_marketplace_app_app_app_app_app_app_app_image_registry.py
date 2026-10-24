from app.services.app_marketplace_app_app_app_app_app_app_app_image_registry import ImageRegistry

def test_push_pull():
    ir = ImageRegistry()
    ir.push("api", "v1.0", 150, "sha256:abc")
    ir.push("api", "v2.0", 160, "sha256:def")
    r = ir.pull("api", "v1.0")
    assert r["found"]
    assert r["digest"] == "sha256:abc"
    assert ir.list_tags("api") == ["v1.0", "v2.0"]

def test_overwrite():
    ir = ImageRegistry()
    ir.push("web", "latest", 100, "sha256:old")
    ir.push("web", "latest", 110, "sha256:new")
    r = ir.pull("web", "latest")
    assert r["digest"] == "sha256:new"
    assert ir.stats()["tags"] == 1

def test_not_found():
    ir = ImageRegistry()
    r = ir.pull("missing", "v1")
    assert not r["found"]
