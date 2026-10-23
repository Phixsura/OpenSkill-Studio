from app.services.app_marketplace_app_app_app_app_app_app_app_build_artifact import (
    store_artifact, download_artifact, artifact_stats, clear_artifacts,
)

def test_store_download():
    clear_artifacts()
    store_artifact("api", "1.0.0", 45.5, "build-123")
    r = download_artifact("api", "1.0.0")
    assert r["found"]
    assert r["digest"].startswith("sha256:")
    download_artifact("api", "1.0.0")
    s = artifact_stats()
    assert s["total"] == 1
    assert s["total_downloads"] == 2
    clear_artifacts()

def test_not_found():
    clear_artifacts()
    r = download_artifact("missing", "1.0")
    assert not r["found"]
    clear_artifacts()
