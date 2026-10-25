from app.services.app_marketplace_platform_dynamo import get_dynamo
def test_dynamo():
    r = get_dynamo()
    assert "100%" in r["efficiency"]
    assert r["resistance"].startswith("ZERO")
    assert r["power_output"]["dora_rating"] == "Elite"
    assert r["rotations"] > 4000
    assert "NEVER STOPS" in r["status"]
