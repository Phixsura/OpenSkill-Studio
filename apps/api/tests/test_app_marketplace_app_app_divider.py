from app.services.app_marketplace_app_app_divider import build_divider

def test_simple():
    r = build_divider()
    assert not r["has_label"]
    assert "border-t" in r["variant_class"]
    assert "my-4" in r["spacing_class"]

def test_labeled():
    r = build_divider(label="Or", variant="dashed", spacing="lg")
    assert r["has_label"]
    assert r["label"] == "Or"
    assert "dashed" in r["variant_class"]
    assert "my-8" in r["spacing_class"]
