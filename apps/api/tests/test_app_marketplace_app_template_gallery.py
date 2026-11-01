from app.services.app_marketplace_app_template_gallery import list_templates, get_template, scaffold_from_template

def test_list_all():
    t = list_templates()
    assert len(t) == 4
    assert t[0]["stars"] >= t[-1]["stars"]

def test_filter_category():
    t = list_templates(category="connector")
    assert all(x["category"] == "connector" for x in t)

def test_filter_difficulty():
    t = list_templates(difficulty="intermediate")
    assert len(t) == 2

def test_get():
    t = get_template(template_id="slack-bot")
    assert t["name"] == "Slack Bot"

def test_get_missing():
    assert get_template(template_id="nope") is None

def test_scaffold():
    r = scaffold_from_template(template_id="basic-connector", app_name="My Conn", developer_id="d1")
    assert r["status"] == "scaffolded"
    assert len(r["files_created"]) == 3

def test_scaffold_missing():
    r = scaffold_from_template(template_id="nope", app_name="X", developer_id="d1")
    assert r["error"]
