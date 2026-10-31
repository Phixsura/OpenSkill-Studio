from app.services.app_marketplace_extension_compat_matrix import ExtCompatMatrixService

def test_set_and_check():
    svc = ExtCompatMatrixService()
    svc.set("ext-1", "1.0", "4.0", "compatible")
    assert svc.check("ext-1", "1.0", "4.0") == "compatible"

def test_untested():
    svc = ExtCompatMatrixService()
    assert svc.check("ext-1", "1.0", "5.0") == "untested"

def test_compatible_versions():
    svc = ExtCompatMatrixService()
    svc.set("ext-1", "1.0", "4.0", "compatible")
    svc.set("ext-1", "2.0", "4.0", "compatible")
    svc.set("ext-1", "3.0", "4.0", "incompatible")
    versions = svc.get_compatible_versions("ext-1", "4.0")
    assert set(versions) == {"1.0", "2.0"}
