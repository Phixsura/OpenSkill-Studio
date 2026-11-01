from app.services.app_marketplace_app_app_app_app_app_app_app_approval_chain import ApprovalChain

def test_chain():
    ac = ApprovalChain()
    ac.create("d1", [{"approver": "lead", "role": "team_lead"},
                      {"approver": "sre", "role": "sre"},
                      {"approver": "vp", "role": "executive"}])
    r1 = ac.approve("d1", "lead")
    assert r1["approved"]
    assert r1["remaining"] == 2
    r2 = ac.approve("d1", "sre")
    assert r2["remaining"] == 1
    r3 = ac.approve("d1", "vp")
    assert r3["status"] == "fully_approved"

def test_wrong_approver():
    ac = ApprovalChain()
    ac.create("d2", [{"approver": "lead"}])
    r = ac.approve("d2", "wrong_person")
    assert not r["approved"]
