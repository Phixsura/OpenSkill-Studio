"""Merkle Tree — hash tree for efficient data integrity verification.

Implements:
- Build tree from leaf data blocks
- Root hash for tamper detection
- Generate inclusion proof (path from leaf to root)
- Verify proof without full tree
- Diff two trees to find changed blocks
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib


@dataclass
class MerkleNode:
    hash: str
    left: MerkleNode | None = None
    right: MerkleNode | None = None
    data: bytes | None = None  # only for leaves
    index: int = -1


@dataclass
class MerkleProof:
    leaf_hash: str
    leaf_index: int
    siblings: list[tuple[str, str]]  # [(hash, "left"|"right"), ...]
    root_hash: str


class MerkleTreeService:
    def __init__(self, algorithm: str = "sha256"):
        self._algorithm = algorithm
        self._root: MerkleNode | None = None
        self._leaves: list[MerkleNode] = []

    def _hash(self, data: bytes) -> str:
        return hashlib.new(self._algorithm, data).hexdigest()

    def _hash_pair(self, left: str, right: str) -> str:
        return self._hash((left + right).encode())

    def build(self, blocks: list[bytes]) -> str:
        """Build tree from data blocks. Returns root hash."""
        if not blocks:
            self._root = None
            self._leaves = []
            return ""

        # Create leaves
        self._leaves = []
        for i, block in enumerate(blocks):
            node = MerkleNode(hash=self._hash(block), data=block, index=i)
            self._leaves.append(node)

        # Build tree bottom-up
        level = list(self._leaves)
        while len(level) > 1:
            next_level = []
            for i in range(0, len(level), 2):
                left = level[i]
                right = level[i + 1] if i + 1 < len(level) else level[i]
                parent = MerkleNode(
                    hash=self._hash_pair(left.hash, right.hash),
                    left=left, right=right)
                next_level.append(parent)
            level = next_level

        self._root = level[0]
        return self._root.hash

    @property
    def root_hash(self) -> str:
        return self._root.hash if self._root else ""

    def get_proof(self, index: int) -> MerkleProof | None:
        """Generate inclusion proof for leaf at index."""
        if not self._leaves or index >= len(self._leaves):
            return None

        siblings = []
        level = list(self._leaves)

        idx = index
        while len(level) > 1:
            next_level = []
            for i in range(0, len(level), 2):
                left = level[i]
                right = level[i + 1] if i + 1 < len(level) else level[i]
                parent = MerkleNode(hash=self._hash_pair(left.hash, right.hash))
                next_level.append(parent)

                # Record sibling for our path
                if i == idx or i + 1 == idx:
                    if idx == i:
                        siblings.append((right.hash, "right"))
                    else:
                        siblings.append((left.hash, "left"))

            idx = idx // 2
            level = next_level

        return MerkleProof(
            leaf_hash=self._leaves[index].hash,
            leaf_index=index,
            siblings=siblings,
            root_hash=self._root.hash if self._root else "")

    @staticmethod
    def verify_proof(proof: MerkleProof, algorithm: str = "sha256") -> bool:
        """Verify an inclusion proof without the full tree."""
        def h(data: bytes) -> str:
            return hashlib.new(algorithm, data).hexdigest()

        current = proof.leaf_hash
        for sibling_hash, side in proof.siblings:
            if side == "right":
                current = h((current + sibling_hash).encode())
            else:
                current = h((sibling_hash + current).encode())

        return current == proof.root_hash

    def diff(self, other_leaves: list[bytes]) -> list[int]:
        """Find indices of blocks that differ from another dataset."""
        changed = []
        other_hashes = [self._hash(b) for b in other_leaves]
        max_len = max(len(self._leaves), len(other_hashes))

        for i in range(max_len):
            if i >= len(self._leaves) or i >= len(other_hashes):
                changed.append(i)
            elif self._leaves[i].hash != other_hashes[i]:
                changed.append(i)
        return changed
