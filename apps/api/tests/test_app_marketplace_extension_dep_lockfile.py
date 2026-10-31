from app.services.app_marketplace_extension_dep_lockfile import ExtDepLockfileService

def test_generate_and_verify():
    svc = ExtDepLockfileService()
    deps = [("react", "18.2.0"), ("axios", "1.4.0")]
    svc.generate("ext-1", deps)
    ok, issues = svc.verify("ext-1", deps)
    assert ok is True

def test_mismatch():
    svc = ExtDepLockfileService()
    svc.generate("ext-1", [("react", "18.2.0")])
    ok, issues = svc.verify("ext-1", [("react", "19.0.0")])
    assert ok is False
    assert "Version mismatch" in issues[0]

def test_diff():
    svc = ExtDepLockfileService()
    svc.generate("ext-1", [("react", "18.2.0"), ("lodash", "4.17.0")])
    d = svc.diff("ext-1", [("react", "19.0.0"), ("axios", "1.0.0")])
    assert "axios" in d["added"]
    assert "lodash" in d["removed"]
    assert "react" in d["changed"]
