from app.services.app_marketplace_extension_content_hash_verify import ContentHashVerifyService


def test_hash_sha256():
    svc = ContentHashVerifyService()
    digest = svc.hash_content(b"hello world", "sha256")
    # Known SHA-256 of "hello world" in base64
    assert len(digest) > 0
    # Same input = same output
    assert svc.hash_content(b"hello world", "sha256") == digest


def test_hash_different_algorithms():
    svc = ContentHashVerifyService()
    d256 = svc.hash_content(b"test", "sha256")
    d384 = svc.hash_content(b"test", "sha384")
    d512 = svc.hash_content(b"test", "sha512")
    assert d256 != d384 != d512


def test_unsupported_algorithm():
    svc = ContentHashVerifyService()
    try:
        svc.hash_content(b"test", "md5")
        assert False
    except ValueError:
        pass


def test_sri_format():
    svc = ContentHashVerifyService()
    sri = svc.generate_sri(b"console.log('hi')", "sha384")
    assert sri.startswith("sha384-")
    assert len(sri) > 10


def test_build_and_verify_manifest():
    svc = ContentHashVerifyService()
    files = {
        "main.js": b"console.log('app');",
        "style.css": b"body { margin: 0; }",
        "config.json": b'{"version": "1.0.0"}',
    }
    svc.build_manifest("ext-1", files)
    ok, results = svc.verify_manifest("ext-1", files)
    assert ok is True
    assert all(r.match for r in results)


def test_tamper_detected():
    svc = ContentHashVerifyService()
    original = {"main.js": b"console.log('safe');"}
    svc.build_manifest("ext-1", original)
    tampered = {"main.js": b"console.log('HACKED');"}
    ok, results = svc.verify_manifest("ext-1", tampered)
    assert ok is False
    assert results[0].tampered is True


def test_missing_file_detected():
    svc = ContentHashVerifyService()
    svc.build_manifest("ext-1", {"a.js": b"a", "b.js": b"b"})
    ok, results = svc.verify_manifest("ext-1", {"a.js": b"a"})
    assert ok is False
    missing = [r for r in results if r.actual == "MISSING"]
    assert len(missing) == 1


def test_extra_file_detected():
    svc = ContentHashVerifyService()
    svc.build_manifest("ext-1", {"a.js": b"a"})
    ok, results = svc.verify_manifest("ext-1", {"a.js": b"a", "evil.js": b"malware"})
    assert ok is False
    extra = [r for r in results if r.expected == "NOT IN MANIFEST"]
    assert len(extra) == 1


def test_hash_chain():
    svc = ContentHashVerifyService()
    files = {"a.js": b"aaa", "b.js": b"bbb"}
    chain = svc.generate_hash_chain(files)
    assert svc.verify_chain(chain, files) is True
    # Tampered file breaks chain
    assert svc.verify_chain(chain, {"a.js": b"aaa", "b.js": b"CHANGED"}) is False


def test_hash_chain_order_matters():
    svc = ContentHashVerifyService()
    # Same files, sorted order should be deterministic
    files1 = {"z.js": b"z", "a.js": b"a"}
    files2 = {"a.js": b"a", "z.js": b"z"}
    assert svc.generate_hash_chain(files1) == svc.generate_hash_chain(files2)
