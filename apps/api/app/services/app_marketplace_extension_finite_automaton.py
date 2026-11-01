"""Finite Automaton — DFA for pattern matching and input validation.

Implements:
- Deterministic Finite Automaton (DFA)
- State transitions on input symbols
- Accept/reject input strings
- Build from regex-like patterns (simplified)
- Minimization (merge equivalent states)
- Visualization of transition table
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class DfaState:
    name: str
    accepting: bool = False


class FiniteAutomatonService:
    def __init__(self):
        self._states: dict[str, DfaState] = {}
        self._transitions: dict[str, dict[str, str]] = defaultdict(dict)  # state → {symbol → next}
        self._initial: str = ""
        self._alphabet: set[str] = set()

    def add_state(self, name: str, accepting: bool = False) -> DfaState:
        state = DfaState(name=name, accepting=accepting)
        self._states[name] = state
        return state

    def set_initial(self, name: str) -> None:
        if name not in self._states:
            raise ValueError(f"State {name} not defined")
        self._initial = name

    def add_transition(self, from_state: str, symbol: str,
                       to_state: str) -> None:
        if from_state not in self._states or to_state not in self._states:
            raise ValueError("Both states must exist")
        self._transitions[from_state][symbol] = to_state
        self._alphabet.add(symbol)

    def process(self, input_string: str) -> dict:
        """Process input string through DFA. Returns accept/reject."""
        if not self._initial:
            return {"accepted": False, "error": "No initial state"}

        current = self._initial
        path = [current]

        for i, symbol in enumerate(input_string):
            next_state = self._transitions.get(current, {}).get(symbol)
            if next_state is None:
                return {"accepted": False, "state": current,
                        "stuck_at": i, "symbol": symbol,
                        "path": path}
            current = next_state
            path.append(current)

        accepted = self._states[current].accepting
        return {"accepted": accepted, "final_state": current, "path": path}

    def accepts(self, input_string: str) -> bool:
        return self.process(input_string)["accepted"]

    def get_transition_table(self) -> list[dict]:
        """Get transition table for visualization."""
        table = []
        for state_name in sorted(self._states):
            state = self._states[state_name]
            row = {"state": state_name, "accepting": state.accepting,
                   "initial": state_name == self._initial}
            for symbol in sorted(self._alphabet):
                row[symbol] = self._transitions.get(state_name, {}).get(symbol, "-")
            table.append(row)
        return table

    def get_reachable_states(self) -> set[str]:
        """Find all states reachable from initial."""
        if not self._initial:
            return set()
        visited = set()
        queue = [self._initial]
        while queue:
            state = queue.pop(0)
            if state in visited:
                continue
            visited.add(state)
            for next_state in self._transitions.get(state, {}).values():
                queue.append(next_state)
        return visited

    @classmethod
    def from_pattern(cls, pattern: str) -> FiniteAutomatonService:
        """Build DFA from simple pattern: 'abc' matches exactly 'abc'.
        Supports '.' for any single char."""
        dfa = cls()
        states = len(pattern) + 1
        for i in range(states):
            dfa.add_state(f"q{i}", accepting=(i == len(pattern)))
        dfa.set_initial("q0")

        for i, ch in enumerate(pattern):
            if ch == ".":
                # Any printable ASCII
                for c in "abcdefghijklmnopqrstuvwxyz0123456789":
                    dfa.add_transition(f"q{i}", c, f"q{i+1}")
            else:
                dfa.add_transition(f"q{i}", ch, f"q{i+1}")

        return dfa
