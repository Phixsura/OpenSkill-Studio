from app.services.app_marketplace_app_app_app_app_app_app_app_container_registry import ContainerRegistry

def test_registry():
    reg = ContainerRegistry()
    reg.create_repo("myapp")
    reg.push_tag("myapp", "latest", size_mb=150, layers=5)
    reg.push_tag("myapp", "v1.0", size_mb=148, layers=5)
    p = reg.pull("myapp", "latest")
    assert p["digest"].startswith("sha256:")
    assert p["size_mb"] == 150
    repos = reg.list_repos()
    assert repos[0]["tag_count"] == 2
    assert repos[0]["pulls"] == 1

def test_not_found():
    reg = ContainerRegistry()
    assert "error" in reg.pull("nope")
