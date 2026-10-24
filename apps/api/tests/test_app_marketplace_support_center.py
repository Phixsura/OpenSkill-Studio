from app.services.app_marketplace_support_center import search_faq, get_faq_by_category, create_support_ticket, build_troubleshooting_guide

def test_search():
    r = search_faq(query="webhook")
    assert any("webhook" in f["question"].lower() for f in r)

def test_category():
    r = get_faq_by_category(category="security")
    assert len(r) >= 1

def test_ticket():
    t = create_support_ticket(user_id="u1", subject="Help", description="Need help", category="technical")
    assert t["status"] == "open"

def test_invalid_priority():
    t = create_support_ticket(user_id="u1", subject="X", description="Y", category="Z", priority="asap")
    assert t["error"]

def test_troubleshoot():
    g = build_troubleshooting_guide(symptom="webhook_not_delivered")
    assert len(g) == 4
    assert g[0]["step"] == 1
