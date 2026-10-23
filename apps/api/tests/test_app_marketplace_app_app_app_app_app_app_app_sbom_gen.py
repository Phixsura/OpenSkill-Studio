from app.services.app_marketplace_app_app_app_app_app_app_app_sbom_gen import generate_sbom, check_license_compliance

def test_sbom():
    r = generate_sbom("my-app", [
        {"name": "react", "version": "18.2.0", "license": "MIT"},
        {"name": "lodash", "version": "4.17.21", "license": "MIT"},
        {"name": "custom-lib", "version": "1.0", "license": "GPL-3.0"},
    ])
    assert r["total_components"] == 3
    assert r["license_count"] == 2
    assert "MIT" in r["unique_licenses"]

def test_compliance():
    sbom = generate_sbom("app", [
        {"name": "lib-a", "license": "MIT"}, {"name": "lib-b", "license": "GPL-3.0"},
    ])
    r = check_license_compliance(sbom, ["GPL-3.0"])
    assert not r["compliant"]
    assert r["violation_count"] == 1
    assert r["violations"][0]["component"] == "lib-b"
