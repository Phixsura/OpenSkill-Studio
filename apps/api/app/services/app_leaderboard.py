"""App Leaderboard Engine — ranked score tracking for installed apps.

Manages leaderboards with score tracking:
- Submit scores per user per board
- Ranked listing (highest first by default)
- Top-N queries
- Per-installation scoped boards
- Score history and personal best tracking
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ScoreEntry:
    """A score on a leaderboard."""

    user_id: str
    score: float
    submitted_at: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)


@dataclass
class RankedEntry:
    """A score with its rank."""

    rank: int
    user_id: str
    score: float
    submitted_at: float


class AppLeaderboard:
    """Ranked score tracking for installed apps."""

    def __init__(self) -> None:
        # (installation_id, board_id, user_id) → best ScoreEntry
        self._scores: dict[tuple[str, str, str], ScoreEntry] = {}
        # (installation_id, board_id, user_id) → list of all submissions
        self._history: dict[tuple[str, str, str], list[ScoreEntry]] = {}

    def submit_score(
        self,
        installation_id: str,
        board_id: str,
        user_id: str,
        score: float,
        metadata: dict | None = None,
        now: float | None = None,
    ) -> ScoreEntry:
        """Submit a score. Keeps the highest as personal best."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not board_id:
            raise ValueError("board_id is required")
        if not user_id:
            raise ValueError("user_id is required")

        entry = ScoreEntry(
            user_id=user_id,
            score=score,
            submitted_at=now or time.time(),
            metadata=metadata or {},
        )

        key = (installation_id, board_id, user_id)
        self._history.setdefault(key, []).append(entry)

        current_best = self._scores.get(key)
        if current_best is None or score > current_best.score:
            self._scores[key] = entry

        return entry

    def get_rankings(
        self,
        installation_id: str,
        board_id: str,
        limit: int = 10,
        ascending: bool = False,
    ) -> list[RankedEntry]:
        """Get ranked entries for a board."""
        entries = [
            (uid, entry) for (inst, bid, uid), entry in self._scores.items()
            if inst == installation_id and bid == board_id
        ]
        entries.sort(key=lambda x: x[1].score, reverse=not ascending)
        entries = entries[:limit]

        return [
            RankedEntry(
                rank=i + 1,
                user_id=uid,
                score=entry.score,
                submitted_at=entry.submitted_at,
            )
            for i, (uid, entry) in enumerate(entries)
        ]

    def get_user_rank(
        self,
        installation_id: str,
        board_id: str,
        user_id: str,
    ) -> int | None:
        """Get a user's rank. Returns None if not on the board."""
        rankings = self.get_rankings(installation_id, board_id, limit=999999)
        for r in rankings:
            if r.user_id == user_id:
                return r.rank
        return None

    def get_personal_best(
        self,
        installation_id: str,
        board_id: str,
        user_id: str,
    ) -> ScoreEntry | None:
        """Get a user's personal best score."""
        return self._scores.get((installation_id, board_id, user_id))

    def get_history(
        self,
        installation_id: str,
        board_id: str,
        user_id: str,
        limit: int = 20,
    ) -> list[ScoreEntry]:
        """Get score submission history, newest first."""
        key = (installation_id, board_id, user_id)
        history = self._history.get(key, [])
        return list(reversed(history[-limit:]))

    def board_size(self, installation_id: str, board_id: str) -> int:
        """Count unique users on a board."""
        return sum(
            1 for (inst, bid, _) in self._scores
            if inst == installation_id and bid == board_id
        )

    def list_boards(self, installation_id: str) -> list[str]:
        """List all board IDs for an installation."""
        return sorted({
            bid for (inst, bid, _) in self._scores
            if inst == installation_id
        })
