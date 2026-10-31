from app.services.app_marketplace_extension_raft_consensus import (
    RaftConsensusService, NodeRole
)


def test_leader_election():
    raft = RaftConsensusService()
    raft.add_node("n1")
    raft.add_node("n2")
    raft.add_node("n3")
    result = raft.start_election("n1")
    assert result["elected"] is True
    assert result["votes"] >= 2  # majority of 3
    assert raft.get_leader() == "n1"


def test_term_increments():
    raft = RaftConsensusService()
    raft.add_node("n1")
    raft.add_node("n2")
    raft.add_node("n3")
    raft.start_election("n1")
    assert raft._nodes["n1"].current_term == 1
    raft.start_election("n2")
    assert raft._nodes["n2"].current_term == 2


def test_log_replication():
    raft = RaftConsensusService()
    raft.add_node("n1")
    raft.add_node("n2")
    raft.add_node("n3")
    raft.start_election("n1")
    entry = raft.append_entry("n1", "SET x=1")
    assert entry is not None
    assert entry.committed is True


def test_committed_visible_on_followers():
    raft = RaftConsensusService()
    raft.add_node("n1")
    raft.add_node("n2")
    raft.add_node("n3")
    raft.start_election("n1")
    raft.append_entry("n1", "SET x=1")
    raft.append_entry("n1", "SET y=2")
    committed_n1 = raft.get_committed("n1")
    committed_n2 = raft.get_committed("n2")
    assert committed_n1 == ["SET x=1", "SET y=2"]
    assert committed_n2 == committed_n1  # same data


def test_non_leader_cant_append():
    raft = RaftConsensusService()
    raft.add_node("n1")
    raft.add_node("n2")
    raft.add_node("n3")
    raft.start_election("n1")
    entry = raft.append_entry("n2", "INVALID")  # n2 is not leader
    assert entry is None


def test_five_node_cluster():
    raft = RaftConsensusService()
    for i in range(5):
        raft.add_node(f"n{i}")
    result = raft.start_election("n0")
    assert result["elected"] is True
    assert result["needed"] == 3  # majority of 5


def test_status():
    raft = RaftConsensusService()
    raft.add_node("n1")
    raft.add_node("n2")
    raft.add_node("n3")
    raft.start_election("n1")
    raft.append_entry("n1", "cmd")
    status = raft.get_status()
    assert status["n1"]["role"] == "leader"
    assert status["n2"]["role"] == "follower"
    assert status["n1"]["log_length"] == 1
