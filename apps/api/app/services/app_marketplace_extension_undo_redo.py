"""Undo/Redo Engine — command pattern with history management.

Implements:
- Command objects with execute/undo methods
- Undo stack and redo stack
- Redo invalidation on new action (branching)
- Batch undo/redo (multiple steps)
- Checkpoint/save points for named snapshots
- History limit to bound memory
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from copy import deepcopy


@dataclass
class UndoableCommand:
    name: str
    execute_fn: callable  # (state) -> state
    undo_fn: callable     # (state) -> state
    timestamp: float = 0.0
    def __post_init__(self):
        if not self.timestamp: self.timestamp = time.time()


class UndoRedoEngine:
    def __init__(self, initial_state: dict | None = None, max_history: int = 100):
        self._state = initial_state or {}
        self._undo_stack: list[tuple[UndoableCommand, dict]] = []  # (command, state_before)
        self._redo_stack: list[tuple[UndoableCommand, dict]] = []
        self._checkpoints: dict[str, dict] = {}
        self._max_history = max_history

    @property
    def state(self) -> dict:
        return dict(self._state)

    def execute(self, command: UndoableCommand) -> dict:
        """Execute a command, push to undo stack, clear redo stack."""
        state_before = deepcopy(self._state)
        self._state = command.execute_fn(deepcopy(self._state))

        self._undo_stack.append((command, state_before))
        self._redo_stack.clear()  # new action invalidates redo

        # Trim history
        if len(self._undo_stack) > self._max_history:
            self._undo_stack = self._undo_stack[-self._max_history:]

        return dict(self._state)

    def undo(self) -> dict | None:
        """Undo last command. Returns new state or None if nothing to undo."""
        if not self._undo_stack:
            return None
        command, state_before = self._undo_stack.pop()
        state_after = deepcopy(self._state)
        self._state = state_before
        self._redo_stack.append((command, state_after))
        return dict(self._state)

    def redo(self) -> dict | None:
        """Redo last undone command."""
        if not self._redo_stack:
            return None
        command, state_after = self._redo_stack.pop()
        state_before = deepcopy(self._state)
        self._state = state_after
        self._undo_stack.append((command, state_before))
        return dict(self._state)

    def undo_n(self, n: int) -> dict:
        """Undo N steps."""
        for _ in range(min(n, len(self._undo_stack))):
            self.undo()
        return dict(self._state)

    def redo_n(self, n: int) -> dict:
        """Redo N steps."""
        for _ in range(min(n, len(self._redo_stack))):
            self.redo()
        return dict(self._state)

    def save_checkpoint(self, name: str) -> None:
        self._checkpoints[name] = deepcopy(self._state)

    def restore_checkpoint(self, name: str) -> dict | None:
        cp = self._checkpoints.get(name)
        if cp is None:
            return None
        # Save current state for undo
        state_before = deepcopy(self._state)
        self._state = deepcopy(cp)
        noop = UndoableCommand(f"restore:{name}", lambda s: deepcopy(cp), lambda s: s)
        self._undo_stack.append((noop, state_before))
        self._redo_stack.clear()
        return dict(self._state)

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def history(self) -> list[str]:
        return [cmd.name for cmd, _ in self._undo_stack]
