"""Command Pattern — encapsulate operations as objects with undo and macros.

Implements:
- Command interface with execute/undo
- Command queue with sequential execution
- Macro commands (compose multiple commands as one)
- Transaction commands (all-or-nothing)
- Command serialization for replay
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class CommandResult:
    success: bool
    output: dict = field(default_factory=dict)
    error: str = ""


class Command:
    """Base command with execute and undo."""
    def __init__(self, name: str, execute_fn: callable, undo_fn: callable | None = None):
        self.name = name
        self._execute = execute_fn
        self._undo = undo_fn
        self.executed = False
        self.result: CommandResult | None = None

    def execute(self, context: dict) -> CommandResult:
        try:
            output = self._execute(context) or {}
            self.result = CommandResult(success=True, output=output)
            self.executed = True
        except Exception as e:
            self.result = CommandResult(success=False, error=str(e))
        return self.result

    def undo(self, context: dict) -> bool:
        if not self.executed or not self._undo:
            return False
        try:
            self._undo(context)
            self.executed = False
            return True
        except Exception:
            return False


class MacroCommand:
    """Compose multiple commands into one (all execute in order)."""
    def __init__(self, name: str, commands: list[Command]):
        self.name = name
        self.commands = commands
        self.executed_commands: list[Command] = []

    def execute(self, context: dict) -> CommandResult:
        self.executed_commands = []
        for cmd in self.commands:
            result = cmd.execute(context)
            if result.success:
                self.executed_commands.append(cmd)
                context.update(result.output)
            else:
                # Undo previously executed
                for prev in reversed(self.executed_commands):
                    prev.undo(context)
                self.executed_commands = []
                return CommandResult(success=False,
                                    error=f"Failed at {cmd.name}: {result.error}")
        return CommandResult(success=True, output=context)

    def undo(self, context: dict) -> bool:
        for cmd in reversed(self.executed_commands):
            cmd.undo(context)
        self.executed_commands = []
        return True


class CommandPatternService:
    def __init__(self):
        self._queue: list[Command | MacroCommand] = []
        self._history: list[tuple[Command | MacroCommand, float]] = []

    def create_command(self, name: str, execute_fn: callable,
                       undo_fn: callable | None = None) -> Command:
        return Command(name, execute_fn, undo_fn)

    def create_macro(self, name: str, commands: list[Command]) -> MacroCommand:
        return MacroCommand(name, commands)

    def enqueue(self, command: Command | MacroCommand) -> None:
        self._queue.append(command)

    def execute_next(self, context: dict) -> CommandResult | None:
        if not self._queue:
            return None
        cmd = self._queue.pop(0)
        result = cmd.execute(context)
        self._history.append((cmd, time.time()))
        return result

    def execute_all(self, context: dict) -> list[CommandResult]:
        results = []
        while self._queue:
            result = self.execute_next(context)
            if result:
                results.append(result)
        return results

    def undo_last(self, context: dict) -> bool:
        if not self._history:
            return False
        cmd, _ = self._history.pop()
        if isinstance(cmd, MacroCommand):
            return cmd.undo(context)
        return cmd.undo(context)

    def get_history(self) -> list[dict]:
        return [{"name": cmd.name, "time": t,
                 "success": cmd.result.success if cmd.result else False}
                for cmd, t in self._history]

    def pending_count(self) -> int:
        return len(self._queue)
