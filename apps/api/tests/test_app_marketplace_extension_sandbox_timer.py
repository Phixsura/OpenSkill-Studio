from app.services.app_marketplace_extension_sandbox_timer import SandboxTimer


def test_start_and_check():
    st = SandboxTimer()
    st.start("t1", "ext-1", timeout=10.0)
    status = st.check("t1")
    assert status["timed_out"] is False
    assert status["remaining"] > 0
    assert status["timeout"] == 10.0


def test_immediate_timeout():
    st = SandboxTimer()
    st.start("t2", "ext-2", timeout=0.0, grace=0.0)
    status = st.check("t2")
    assert status["timed_out"] is True
    assert status["grace_expired"] is True


def test_stop_returns_elapsed():
    st = SandboxTimer()
    st.start("t3", "ext-3", timeout=60.0)
    elapsed = st.stop("t3")
    assert elapsed >= 0


def test_budget_management():
    st = SandboxTimer()
    st.set_budget("ext-4", 100.0)
    assert st.has_budget("ext-4") is True
    budget = st.get_budget("ext-4")
    assert budget["has_budget"] is True
    assert budget["remaining_seconds"] == 100.0


def test_budget_deduction():
    st = SandboxTimer()
    st.set_budget("ext-5", 1.0)
    st.start("t5", "ext-5", timeout=60.0)
    st.stop("t5")  # deducts elapsed
    budget = st.get_budget("ext-5")
    assert budget["remaining_seconds"] < 1.0


def test_no_budget_always_allowed():
    st = SandboxTimer()
    assert st.has_budget("ext-no-budget") is True  # no budget = unlimited


def test_unknown_timer():
    st = SandboxTimer()
    assert st.check("nonexistent")["error"] == "Timer not found"
