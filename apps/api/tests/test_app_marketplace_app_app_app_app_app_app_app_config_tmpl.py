from app.services.app_marketplace_app_app_app_app_app_app_app_config_tmpl import render_template, validate_template

def test_render():
    r = render_template("host=${HOST} port=${PORT}", {"HOST": "localhost", "PORT": "8080"})
    assert r["rendered"] == "host=localhost port=8080"
    assert r["complete"]

def test_missing():
    r = render_template("db=${DB_HOST}:${DB_PORT}", {"DB_HOST": "pg"})
    assert not r["complete"]
    assert "DB_PORT" in r["missing_variables"]

def test_validate():
    r = validate_template("${HOST}:${PORT}", ["HOST", "PORT", "DB"])
    assert not r["valid"]
    assert "DB" in r["missing"]
