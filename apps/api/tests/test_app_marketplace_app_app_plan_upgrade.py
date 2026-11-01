from app.services.app_marketplace_app_app_plan_upgrade import build_upgrade_flow

def test_upgrade():
    r = build_upgrade_flow(current_plan="free", target_plan="pro")
    assert r["is_upgrade"]
    assert r["price_diff"] == 29
    assert r["requires_payment"]

def test_downgrade():
    r = build_upgrade_flow(current_plan="pro", target_plan="starter")
    assert r["is_downgrade"]
    assert r["warning"] is not None
    assert r["price_diff"] == -20
