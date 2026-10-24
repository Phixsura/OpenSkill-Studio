from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_out_parser import fleet_ai_output_parser
def test_op():
    r = fleet_ai_output_parser([{"active": True, "parsed_24h": 10000000, "formats": ["json", "xml", "yaml", "csv"], "success_pct": 99}])
    assert r["formats"] == 4
    assert r["reliable"]
