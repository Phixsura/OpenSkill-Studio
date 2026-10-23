from app.services.app_marketplace_app_app_app_app_sidebar import build_app_sidebar

def test_sidebar():
    r = build_app_sidebar(app_id="a1", app_name="SuperApp", active_section="analytics",
                           badges={"reviews": 5, "webhooks": 2})
    assert r["app_name"] == "SuperApp"
    assert len(r["items"]) == 6
    analytics = next(i for i in r["items"] if i["id"] == "analytics")
    assert analytics["active"]
    reviews = next(i for i in r["items"] if i["id"] == "reviews")
    assert reviews["badge"] == 5
    assert reviews["href"] == "/apps/a1/reviews"
