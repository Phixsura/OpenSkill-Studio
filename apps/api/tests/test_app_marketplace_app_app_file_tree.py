from app.services.app_marketplace_app_app_file_tree import build_file_tree

def test_tree():
    files = ["src/index.ts", "src/components/Button.tsx", "package.json", "README.md"]
    r = build_file_tree(files=files)
    assert r["total_files"] == 4
    assert "src" in r["tree"]
    assert "package.json" in r["tree"]
    assert r["tree"]["README.md"]["icon"] == "📝"

def test_empty():
    r = build_file_tree(files=[])
    assert r["total_files"] == 0
