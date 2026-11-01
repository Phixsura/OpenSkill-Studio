from app.services.app_marketplace_app_quickstart_generator import generate_quickstart, render_quickstart_markdown

def test_default():
    q = generate_quickstart(app={"name": "SuperApp"})
    assert q["app_name"] == "SuperApp"
    assert len(q["sections"]) == 4
    assert q["estimated_setup_minutes"] == 5

def test_with_config():
    q = generate_quickstart(app={"name": "App"}, config_fields=[
        {"name": "api_url", "description": "Your API endpoint", "default": "https://api.example.com"}])
    config_section = next(s for s in q["sections"] if s["title"] == "Configuration")
    assert "api_url" in config_section["content"]

def test_custom_steps():
    q = generate_quickstart(app={"name": "App"}, installation_steps=["Step A", "Step B"])
    install = next(s for s in q["sections"] if s["title"] == "Installation")
    assert "Step A" in install["content"]

def test_markdown():
    q = generate_quickstart(app={"name": "MyApp"})
    md = render_quickstart_markdown(quickstart=q)
    assert "# Getting Started with MyApp" in md
    assert "## Installation" in md
    assert "5 minutes" in md
