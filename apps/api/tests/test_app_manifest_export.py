import json
from app.services.app_manifest_export import export_as_json, export_as_yaml_like, strip_internal_fields

MANIFEST = {"app": {"name": "Test", "version": "1.0.0"}, "permissions": ["read:cohorts"]}

def test_json_pretty():
    result = export_as_json(MANIFEST)
    assert "\n" in result
    parsed = json.loads(result)
    assert parsed["app"]["name"] == "Test"

def test_json_compact():
    result = export_as_json(MANIFEST, pretty=False)
    assert "\n" not in result

def test_yaml_like():
    result = export_as_yaml_like(MANIFEST)
    assert "app:" in result
    assert "name:" in result

def test_strip_internal():
    m = {**MANIFEST, "_id": "x", "_internal": {}, "_review_notes": "secret"}
    cleaned = strip_internal_fields(m)
    assert "_id" not in cleaned
    assert "app" in cleaned

def test_strip_no_mutation():
    m = {"_id": "x", "app": {"name": "Y"}}
    strip_internal_fields(m)
    assert "_id" in m
