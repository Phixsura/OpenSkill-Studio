"""Raft Consensus (Simplified) — leader election and log replication.

Simplified in-memory Raft for understanding the algorithm:
- Leader election with term numbers and majority vote
- Log replication from leader to followers
- Commit when majority acknowledges
- Leader heartbeat timeout detection
- No real networking — simulates message passing
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import random
import time


class NodeRole(str, Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"


@dataclass
class LogEntry:
    term: int
    index: int
    command: str
    committed: bool = False


@dataclass
class RaftNode:
    node_id: str
    role: NodeRole = NodeRole.FOLLOWER
    current_term: int = 0
    voted_for: str = ""
    log: list[LogEntry] = field(default_factory=list)
    commit_index: int = -1
    leader_id: str = ""
    last_heartbeat: float = 0.0


class RaftConsensusService:
    def __init__(self):
        self._nodes: dict[str, RaftNode] = {}
        self._cluster_size = 0

    def add_node(self, node_id: str) -> RaftNode:
        node = RaftNode(node_id=node_id, last_heartbeat=time.time())
        self._nodes[node_id] = node
        self._cluster_size += 1
        return node

    @property
    def majority(self) -> int:
        return self._cluster_size // 2 + 1

    def start_election(self, candidate_id: str) -> dict:
        """Candidate requests votes from all nodes."""
        candidate = self._nodes.get(candidate_id)
        if not candidate:
            return {"elected": False, "reason": "Node not found"}

        candidate.current_term += 1
        candidate.role = NodeRole.CANDIDATE
        candidate.voted_for = candidate_id

        votes = 1  # vote for self
        for nid, node in self._nodes.items():
            if nid == candidate_id:
                continue
            vote = self._request_vote(node, candidate_id, candidate.current_term,
                                       len(candidate.log) - 1)
            if vote:
                votes += 1

        if votes >= self.majority:
            candidate.role = NodeRole.LEADER
            candidate.leader_id = candidate_id
            # Notify all followers
            for nid, node in self._nodes.items():
                node.leader_id = candidate_id
                if nid != candidate_id:
                    node.role = NodeRole.FOLLOWER
            return {"elected": True, "term": candidate.current_term,
                    "votes": votes, "needed": self.majority}
        else:
            candidate.role = NodeRole.FOLLOWER
            return {"elected": False, "term": candidate.current_term,
                    "votes": votes, "needed": self.majority}

    def _request_vote(self, voter: RaftNode, candidate_id: str,
                      candidate_term: int, candidate_log_index: int) -> bool:
        """Node decides whether to grant vote."""
        # Higher term always wins
        if candidate_term < voter.current_term:
            return False
        # Already voted for someone else this term
        if voter.voted_for and voter.voted_for != candidate_id and \
           voter.current_term == candidate_term:
            return False
        # Candidate's log must be at least as up-to-date
        voter_log_index = len(voter.log) - 1
        if candidate_log_index < voter_log_index:
            return False

        voter.current_term = candidate_term
        voter.voted_for = candidate_id
        return True

    def append_entry(self, leader_id: str, command: str) -> LogEntry | None:
        """Leader appends entry to its log and replicates."""
        leader = self._nodes.get(leader_id)
        if not leader or leader.role != NodeRole.LEADER:
            return None

        entry = LogEntry(term=leader.current_term,
                         index=len(leader.log), command=command)
        leader.log.append(entry)

        # Replicate to followers
        acks = 1  # leader counts
        for nid, node in self._nodes.items():
            if nid == leader_id:
                continue
            if self._replicate_to(node, entry, leader.current_term):
                acks += 1

        # Commit if majority
        if acks >= self.majority:
            entry.committed = True
            leader.commit_index = entry.index
            # Notify followers of commit
            for nid, node in self._nodes.items():
                if nid != leader_id and entry.index < len(node.log):
                    node.log[entry.index].committed = True
                    node.commit_index = entry.index
            return entry

        return entry

    def _replicate_to(self, follower: RaftNode, entry: LogEntry,
                      leader_term: int) -> bool:
        """Replicate log entry to a follower."""
        if leader_term < follower.current_term:
            return False
        follower.current_term = leader_term
        # Append to follower's log
        while len(follower.log) <= entry.index:
            follower.log.append(None)
        follower.log[entry.index] = LogEntry(
            term=entry.term, index=entry.index, command=entry.command)
        follower.last_heartbeat = time.time()
        return True

    def get_committed(self, node_id: str) -> list[str]:
        """Get all committed commands on a node."""
        node = self._nodes.get(node_id)
        if not node:
            return []
        return [e.command for e in node.log
                if e and e.committed]

    def get_leader(self) -> str | None:
        for nid, node in self._nodes.items():
            if node.role == NodeRole.LEADER:
                return nid
        return None

    def get_status(self) -> dict:
        return {nid: {"role": n.role.value, "term": n.current_term,
                       "log_length": len(n.log), "commit_index": n.commit_index,
                       "leader": n.leader_id}
                for nid, n in self._nodes.items()}
