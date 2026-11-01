"""Actor Model — message-passing concurrency with supervision trees.

Implements:
- Named actors with mailboxes (message queues)
- Synchronous message dispatch (simulated async)
- Ask pattern (request/response)
- Supervision strategies: restart, stop, escalate
- Actor lifecycle: created → running → stopped
- Parent-child actor hierarchy
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque
import time


@dataclass
class Message:
    sender: str
    content: dict
    msg_type: str = "tell"  # tell (fire-and-forget) or ask (expect reply)
    timestamp: float = 0.0
    def __post_init__(self):
        if not self.timestamp: self.timestamp = time.time()


@dataclass
class Actor:
    name: str
    handler: callable  # (actor_context, message) -> response
    parent: str = ""
    children: list[str] = field(default_factory=list)
    mailbox: deque = field(default_factory=deque)
    state: dict = field(default_factory=dict)
    status: str = "running"  # created, running, stopped, failed
    processed: int = 0
    errors: int = 0
    supervision: str = "restart"  # restart, stop, escalate


class ActorModelService:
    def __init__(self):
        self._actors: dict[str, Actor] = {}
        self._dead_letters: list[Message] = []
        self._replies: dict[str, dict] = {}  # for ask pattern

    def spawn(self, name: str, handler: callable, parent: str = "",
              supervision: str = "restart",
              initial_state: dict | None = None) -> Actor:
        if name in self._actors:
            raise ValueError(f"Actor '{name}' already exists")
        if parent and parent not in self._actors:
            raise ValueError(f"Parent actor '{parent}' not found")
        actor = Actor(name=name, handler=handler, parent=parent,
                      supervision=supervision,
                      state=initial_state or {})
        self._actors[name] = actor
        if parent:
            self._actors[parent].children.append(name)
        return actor

    def tell(self, target: str, content: dict, sender: str = "system") -> bool:
        """Fire-and-forget message."""
        actor = self._actors.get(target)
        if not actor or actor.status != "running":
            self._dead_letters.append(Message(sender, content))
            return False
        actor.mailbox.append(Message(sender=sender, content=content, msg_type="tell"))
        return True

    def ask(self, target: str, content: dict, sender: str = "system") -> dict | None:
        """Request-response message."""
        actor = self._actors.get(target)
        if not actor or actor.status != "running":
            return None
        msg = Message(sender=sender, content=content, msg_type="ask")
        actor.mailbox.append(msg)
        self._process_one(target)
        return self._replies.pop(target, None)

    def process(self, target: str, max_messages: int = 10) -> int:
        """Process up to N messages from actor's mailbox."""
        processed = 0
        for _ in range(max_messages):
            if not self._process_one(target):
                break
            processed += 1
        return processed

    def _process_one(self, target: str) -> bool:
        actor = self._actors.get(target)
        if not actor or actor.status != "running" or not actor.mailbox:
            return False

        msg = actor.mailbox.popleft()

        class ActorContext:
            def __init__(ctx_self, svc, actor_ref):
                ctx_self._svc = svc
                ctx_self._actor = actor_ref
            @property
            def state(ctx_self):
                return ctx_self._actor.state
            def tell(ctx_self, target_name: str, content: dict):
                ctx_self._svc.tell(target_name, content, ctx_self._actor.name)
            def reply(ctx_self, content: dict):
                ctx_self._svc._replies[ctx_self._actor.name] = content
            def spawn_child(ctx_self, name: str, handler: callable, **kwargs):
                return ctx_self._svc.spawn(name, handler, parent=ctx_self._actor.name, **kwargs)

        ctx = ActorContext(self, actor)
        try:
            actor.handler(ctx, msg)
            actor.processed += 1
        except Exception as e:
            actor.errors += 1
            self._handle_failure(actor, str(e))
        return True

    def _handle_failure(self, actor: Actor, error: str) -> None:
        if actor.supervision == "restart":
            actor.status = "running"  # reset, keep state
            actor.mailbox.clear()
        elif actor.supervision == "stop":
            actor.status = "stopped"
            self._stop_children(actor)
        elif actor.supervision == "escalate" and actor.parent:
            parent = self._actors.get(actor.parent)
            if parent:
                self._handle_failure(parent, f"Child {actor.name} failed: {error}")

    def _stop_children(self, actor: Actor) -> None:
        for child_name in actor.children:
            child = self._actors.get(child_name)
            if child:
                child.status = "stopped"
                self._stop_children(child)

    def stop(self, name: str) -> bool:
        actor = self._actors.get(name)
        if not actor:
            return False
        actor.status = "stopped"
        self._stop_children(actor)
        return True

    def get_stats(self) -> dict:
        return {
            "total_actors": len(self._actors),
            "running": sum(1 for a in self._actors.values() if a.status == "running"),
            "stopped": sum(1 for a in self._actors.values() if a.status == "stopped"),
            "dead_letters": len(self._dead_letters),
            "total_processed": sum(a.processed for a in self._actors.values()),
        }
