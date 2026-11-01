from app.services.app_marketplace_extension_finite_automaton import FiniteAutomatonService


def test_simple_dfa():
    dfa = FiniteAutomatonService()
    dfa.add_state("q0")
    dfa.add_state("q1")
    dfa.add_state("q2", accepting=True)
    dfa.set_initial("q0")
    dfa.add_transition("q0", "a", "q1")
    dfa.add_transition("q1", "b", "q2")
    assert dfa.accepts("ab") is True
    assert dfa.accepts("a") is False
    assert dfa.accepts("abc") is False


def test_binary_even_zeros():
    """DFA that accepts binary strings with even number of 0s."""
    dfa = FiniteAutomatonService()
    dfa.add_state("even", accepting=True)
    dfa.add_state("odd")
    dfa.set_initial("even")
    dfa.add_transition("even", "0", "odd")
    dfa.add_transition("even", "1", "even")
    dfa.add_transition("odd", "0", "even")
    dfa.add_transition("odd", "1", "odd")
    assert dfa.accepts("00") is True   # 2 zeros (even)
    assert dfa.accepts("0") is False   # 1 zero (odd)
    assert dfa.accepts("010") is True  # 2 zeros
    assert dfa.accepts("111") is True  # 0 zeros (even)


def test_process_details():
    dfa = FiniteAutomatonService()
    dfa.add_state("q0")
    dfa.add_state("q1", accepting=True)
    dfa.set_initial("q0")
    dfa.add_transition("q0", "x", "q1")
    result = dfa.process("x")
    assert result["accepted"] is True
    assert result["path"] == ["q0", "q1"]


def test_stuck():
    dfa = FiniteAutomatonService()
    dfa.add_state("q0")
    dfa.set_initial("q0")
    result = dfa.process("z")
    assert result["accepted"] is False
    assert result["stuck_at"] == 0


def test_from_pattern():
    dfa = FiniteAutomatonService.from_pattern("hello")
    assert dfa.accepts("hello") is True
    assert dfa.accepts("hell") is False
    assert dfa.accepts("helloo") is False


def test_wildcard_pattern():
    dfa = FiniteAutomatonService.from_pattern("a.c")
    assert dfa.accepts("abc") is True
    assert dfa.accepts("axc") is True
    assert dfa.accepts("ac") is False


def test_transition_table():
    dfa = FiniteAutomatonService()
    dfa.add_state("s0")
    dfa.add_state("s1", accepting=True)
    dfa.set_initial("s0")
    dfa.add_transition("s0", "a", "s1")
    table = dfa.get_transition_table()
    assert len(table) == 2
    assert table[0]["state"] == "s0"
    assert table[0]["initial"] is True


def test_reachable():
    dfa = FiniteAutomatonService()
    dfa.add_state("q0"); dfa.add_state("q1"); dfa.add_state("orphan")
    dfa.set_initial("q0")
    dfa.add_transition("q0", "a", "q1")
    reachable = dfa.get_reachable_states()
    assert "q0" in reachable
    assert "q1" in reachable
    assert "orphan" not in reachable


def test_empty_string():
    dfa = FiniteAutomatonService()
    dfa.add_state("accept", accepting=True)
    dfa.set_initial("accept")
    assert dfa.accepts("") is True

    dfa2 = FiniteAutomatonService()
    dfa2.add_state("reject")
    dfa2.set_initial("reject")
    assert dfa2.accepts("") is False
