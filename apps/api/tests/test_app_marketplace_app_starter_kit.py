from app.services.app_marketplace_app_starter_kit import list_starter_kits, get_starter_kit, scaffold_project

def test_list():
    kits = list_starter_kits()
    assert len(kits) == 4

def test_filter():
    kits = list_starter_kits(language="python")
    assert all(k["language"] == "python" for k in kits)
    assert len(kits) == 2

def test_get():
    k = get_starter_kit(kit_id="typescript-basic")
    assert k["name"] == "TypeScript Basic"

def test_get_unknown():
    assert get_starter_kit(kit_id="nope") is None

def test_scaffold():
    r = scaffold_project(kit_id="typescript-basic", app_name="MyApp", app_slug="my-app")
    assert r["file_count"] == 5
    assert "npm install" in r["next_steps"][1]

def test_scaffold_unknown():
    r = scaffold_project(kit_id="nope", app_name="X", app_slug="x")
    assert r.get("error")
