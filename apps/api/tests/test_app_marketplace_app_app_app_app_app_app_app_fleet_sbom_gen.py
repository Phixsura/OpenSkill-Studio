from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sbom_gen import fleet_sbom_generation
def test_sbom():
    r = fleet_sbom_generation([{"has_sbom": True, "sbom_format": "SPDX"}, {"has_sbom": True, "sbom_format": "CycloneDX"}, {"has_sbom": False}])
    assert r["with_sbom"] == 2
    assert r["coverage_pct"] == 66.7
    assert not r["compliant"]
    assert "SPDX" in r["formats"]
