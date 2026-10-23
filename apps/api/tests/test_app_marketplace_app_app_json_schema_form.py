from app.services.app_marketplace_app_app_json_schema_form import schema_to_fields

SCHEMA = {
    "properties": {
        "name": {"type": "string", "title": "App Name", "description": "Your app name"},
        "port": {"type": "integer", "minimum": 1, "maximum": 65535, "default": 3000},
        "env": {"type": "string", "enum": ["dev", "staging", "prod"]},
        "debug": {"type": "boolean", "default": False},
    },
    "required": ["name"],
}

def test_fields():
    r = schema_to_fields(schema=SCHEMA)
    assert r["total"] == 4
    assert r["required_count"] == 1
    name_f = next(f for f in r["fields"] if f["name"] == "name")
    assert name_f["required"]
    assert name_f["type"] == "text"

def test_enum():
    r = schema_to_fields(schema=SCHEMA)
    env_f = next(f for f in r["fields"] if f["name"] == "env")
    assert env_f["type"] == "select"
    assert env_f["enum"] == ["dev", "staging", "prod"]

def test_number_constraints():
    r = schema_to_fields(schema=SCHEMA)
    port_f = next(f for f in r["fields"] if f["name"] == "port")
    assert port_f["min"] == 1
    assert port_f["max"] == 65535
    assert port_f["default"] == 3000
