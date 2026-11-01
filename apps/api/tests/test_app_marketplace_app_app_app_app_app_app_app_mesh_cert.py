from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_cert import MeshCertManager

def test_issue_verify():
    mcm = MeshCertManager()
    mcm.issue("api")
    r = mcm.verify("api")
    assert r["valid"]

def test_rotate():
    mcm = MeshCertManager()
    mcm.issue("api")
    old_fp = mcm.verify("api")["fingerprint"]
    mcm.rotate("api")
    new_fp = mcm.verify("api")["fingerprint"]
    assert old_fp != new_fp

def test_revoke():
    mcm = MeshCertManager()
    mcm.issue("api")
    mcm.revoke("api")
    assert not mcm.verify("api")["valid"]
    assert mcm.stats()["revoked"] == 1
