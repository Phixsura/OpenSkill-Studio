from app.services.app_marketplace_extension_cas_store import CasStoreService


def test_store_and_retrieve():
    cas = CasStoreService()
    addr = cas.store(b"hello world")
    assert len(addr) == 64  # SHA-256 hex
    content = cas.retrieve(addr)
    assert content == b"hello world"


def test_deduplication():
    cas = CasStoreService()
    a1 = cas.store(b"same content")
    a2 = cas.store(b"same content")
    assert a1 == a2  # same content = same address
    assert cas.stats()["objects"] == 1  # only one copy
    assert cas.stats()["total_deduped"] == 1


def test_different_content_different_address():
    cas = CasStoreService()
    a1 = cas.store(b"content A")
    a2 = cas.store(b"content B")
    assert a1 != a2
    assert cas.stats()["objects"] == 2


def test_integrity_verification():
    cas = CasStoreService()
    addr = cas.store(b"important data")
    # Tamper with stored content
    cas._objects[addr].content = b"TAMPERED"
    try:
        cas.retrieve(addr, verify=True)
        assert False
    except ValueError:
        pass


def test_retrieve_without_verify():
    cas = CasStoreService()
    addr = cas.store(b"data")
    cas._objects[addr].content = b"changed"
    # Without verify, returns whatever is stored
    assert cas.retrieve(addr, verify=False) == b"changed"


def test_ref_counting():
    cas = CasStoreService()
    addr = cas.store(b"shared")
    cas.store(b"shared")  # ref_count = 2
    meta = cas.get_metadata(addr)
    assert meta["ref_count"] == 2
    cas.release(addr)  # ref_count = 1
    assert cas.exists(addr) is True
    cas.release(addr)  # ref_count = 0 → removed
    assert cas.exists(addr) is False


def test_manifest():
    cas = CasStoreService()
    files = {"main.js": b"console.log('hi')", "style.css": b"body{}"}
    manifest = cas.store_manifest(files)
    assert len(manifest) == 2
    assert cas.retrieve(manifest["main.js"]) == b"console.log('hi')"


def test_nonexistent():
    cas = CasStoreService()
    assert cas.retrieve("0" * 64) is None
    assert cas.exists("0" * 64) is False


def test_dedup_ratio():
    cas = CasStoreService()
    for _ in range(5):
        cas.store(b"repeated")
    cas.store(b"unique")
    stats = cas.stats()
    # 5 repeated (1 stored + 4 deduped) + 1 unique = 2 stored, 4 deduped
    assert stats["dedup_ratio"] > 50
