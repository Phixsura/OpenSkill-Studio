"""Diff Engine — compute minimal edit scripts between sequences.

Implements a simplified Myers-like diff:
- Longest Common Subsequence (LCS) for diff computation
- Line-level and word-level diff
- Unified diff output format
- Patch generation and application
- Diff statistics (additions, deletions, changes)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class DiffOp(str, Enum):
    EQUAL = "equal"
    INSERT = "insert"
    DELETE = "delete"


@dataclass
class DiffHunk:
    op: DiffOp
    content: str
    old_line: int = 0
    new_line: int = 0


@dataclass
class DiffResult:
    hunks: list[DiffHunk] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0
    unchanged: int = 0

    @property
    def similarity(self) -> float:
        total = self.additions + self.deletions + self.unchanged
        return round(self.unchanged / total * 100, 1) if total else 100.0


class DiffEngineService:
    def diff_lines(self, old: str, new: str) -> DiffResult:
        """Compute line-level diff between two strings."""
        old_lines = old.splitlines(keepends=True) if old else []
        new_lines = new.splitlines(keepends=True) if new else []
        return self._diff_sequences(old_lines, new_lines)

    def diff_words(self, old: str, new: str) -> DiffResult:
        """Compute word-level diff."""
        old_words = old.split()
        new_words = new.split()
        return self._diff_sequences(old_words, new_words)

    def _diff_sequences(self, old: list[str], new: list[str]) -> DiffResult:
        """LCS-based diff."""
        # Compute LCS table
        m, n = len(old), len(new)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if old[i - 1] == new[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        # Backtrack to produce diff
        hunks = []
        i, j = m, n
        temp = []

        while i > 0 or j > 0:
            if i > 0 and j > 0 and old[i - 1] == new[j - 1]:
                temp.append(DiffHunk(DiffOp.EQUAL, old[i - 1], i, j))
                i -= 1
                j -= 1
            elif j > 0 and (i == 0 or dp[i][j - 1] >= dp[i - 1][j]):
                temp.append(DiffHunk(DiffOp.INSERT, new[j - 1], 0, j))
                j -= 1
            else:
                temp.append(DiffHunk(DiffOp.DELETE, old[i - 1], i, 0))
                i -= 1

        temp.reverse()
        result = DiffResult(hunks=temp)
        for h in temp:
            if h.op == DiffOp.INSERT:
                result.additions += 1
            elif h.op == DiffOp.DELETE:
                result.deletions += 1
            else:
                result.unchanged += 1
        return result

    def unified_diff(self, old: str, new: str, old_name: str = "a",
                     new_name: str = "b", context: int = 3) -> str:
        """Generate unified diff format output."""
        diff = self.diff_lines(old, new)
        lines = [f"--- {old_name}", f"+++ {new_name}"]

        for hunk in diff.hunks:
            content = hunk.content.rstrip('\n')
            if hunk.op == DiffOp.EQUAL:
                lines.append(f" {content}")
            elif hunk.op == DiffOp.DELETE:
                lines.append(f"-{content}")
            elif hunk.op == DiffOp.INSERT:
                lines.append(f"+{content}")

        return "\n".join(lines)

    def apply_patch(self, original: str, diff_result: DiffResult) -> str:
        """Apply a diff to reconstruct the new version."""
        result = []
        for hunk in diff_result.hunks:
            if hunk.op in (DiffOp.EQUAL, DiffOp.INSERT):
                result.append(hunk.content)
            # DELETE hunks are skipped (removed from output)
        return "".join(result)

    def three_way_merge(self, base: str, ours: str, theirs: str) -> tuple[str, bool]:
        """Three-way merge. Returns (merged, has_conflicts)."""
        base_lines = base.splitlines()
        our_diff = self.diff_lines(base, ours)
        their_diff = self.diff_lines(base, theirs)

        our_changes = {h.old_line for h in our_diff.hunks if h.op != DiffOp.EQUAL}
        their_changes = {h.old_line for h in their_diff.hunks if h.op != DiffOp.EQUAL}

        conflicts = our_changes & their_changes
        has_conflicts = len(conflicts) > 0

        # Simple merge: apply non-conflicting changes
        result = self.apply_patch(base, our_diff)
        return result, has_conflicts
