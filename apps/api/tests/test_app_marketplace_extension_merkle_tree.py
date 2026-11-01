from app.services.app_marketplace_extension_merkle_tree import MerkleTreeService


def test_build_tree():
    mt = MerkleTreeService()
    root = mt.build([b"block-0", b"block-1", b"block-2", b"block-3"])
    assert len(root) == 64  # sha256 hex digest


def test_root_changes_on_tamper():
    mt = MerkleTreeService()
    r1 = mt.build([b"a", b"b", b"c", b"d"])
    mt2 = MerkleTreeService()
    r2 = mt2.build([b"a", b"b", b"TAMPERED", b"d"])
    assert r1 != r2


def test_same_data_same_root():
    mt1 = MerkleTreeService()
    mt2 = MerkleTreeService()
    r1 = mt1.build([b"x", b"y", b"z"])
    r2 = mt2.build([b"x", b"y", b"z"])
    assert r1 == r2


def test_proof_generation():
    mt = MerkleTreeService()
    mt.build([b"a", b"b", b"c", b"d"])
    proof = mt.get_proof(2)  # proof for block "c"
    assert proof is not None
    assert proof.leaf_index == 2
    assert len(proof.siblings) > 0


def test_proof_verification():
    mt = MerkleTreeService()
    mt.build([b"block-0", b"block-1", b"block-2", b"block-3"])
    for i in range(4):
        proof = mt.get_proof(i)
        assert MerkleTreeService.verify_proof(proof) is True


def test_tampered_proof_fails():
    mt = MerkleTreeService()
    mt.build([b"a", b"b", b"c", b"d"])
    proof = mt.get_proof(0)
    # Tamper with root
    proof.root_hash = "0" * 64
    assert MerkleTreeService.verify_proof(proof) is False


def test_diff():
    mt = MerkleTreeService()
    original = [b"a", b"b", b"c", b"d"]
    mt.build(original)
    modified = [b"a", b"CHANGED", b"c", b"d"]
    changed = mt.diff(modified)
    assert changed == [1]


def test_diff_different_lengths():
    mt = MerkleTreeService()
    mt.build([b"a", b"b"])
    changed = mt.diff([b"a", b"b", b"c"])
    assert 2 in changed


def test_empty_tree():
    mt = MerkleTreeService()
    assert mt.build([]) == ""
    assert mt.root_hash == ""


def test_single_block():
    mt = MerkleTreeService()
    root = mt.build([b"only"])
    assert len(root) == 64
    proof = mt.get_proof(0)
    assert MerkleTreeService.verify_proof(proof) is True
