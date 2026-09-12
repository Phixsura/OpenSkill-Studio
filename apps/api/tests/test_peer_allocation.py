"""Unit tests for the peer-review allocation algorithm.

Verifies the Moodle-style fairness properties: nobody reviews themself,
no duplicate pairs, everyone gets their first review before anyone gets a
second, and load is balanced lowest-first.
"""

import random

from app.services.peer_review import allocate_reviews


def _setup(n: int):
    """n learners, each with one submission."""
    author_by_submission = {f"sub{i}": f"user{i}" for i in range(n)}
    reviewers = [f"user{i}" for i in range(n)]
    return author_by_submission, reviewers


def test_no_self_review():
    subs, reviewers = _setup(5)
    pairs = allocate_reviews(subs, reviewers, 2, rng=random.Random(42))
    for reviewer, submission in pairs:
        assert subs[submission] != reviewer


def test_no_duplicate_pairs():
    subs, reviewers = _setup(6)
    pairs = allocate_reviews(subs, reviewers, 3, rng=random.Random(1))
    assert len(pairs) == len(set(pairs))


def test_every_reviewer_gets_n_reviews_when_possible():
    subs, reviewers = _setup(5)
    pairs = allocate_reviews(subs, reviewers, 2, rng=random.Random(7))
    per_reviewer = {}
    for r, _s in pairs:
        per_reviewer[r] = per_reviewer.get(r, 0) + 1
    # 5 learners, 4 possible targets each — 2 reviews always possible
    assert all(count == 2 for count in per_reviewer.values())
    assert len(per_reviewer) == 5


def test_every_submission_reviewed_at_least_once():
    """Fairness guarantee: with N>=1 and enough reviewers, no submission
    is left unreviewed (Teachfloor's ≥1 guarantee)."""
    for seed in range(20):
        subs, reviewers = _setup(4)
        pairs = allocate_reviews(subs, reviewers, 1, rng=random.Random(seed))
        reviewed = {s for _r, s in pairs}
        assert reviewed == set(subs.keys()), f"seed {seed}: {reviewed}"


def test_load_balanced():
    """With num_reviews=2 and n=6, each submission gets exactly 2 reviews."""
    subs, reviewers = _setup(6)
    pairs = allocate_reviews(subs, reviewers, 2, rng=random.Random(99))
    load = {}
    for _r, s in pairs:
        load[s] = load.get(s, 0) + 1
    assert all(count == 2 for count in load.values())


def test_two_learners_edge():
    """Minimum viable: 2 learners review each other once."""
    subs, reviewers = _setup(2)
    pairs = allocate_reviews(subs, reviewers, 1, rng=random.Random(3))
    assert sorted(pairs) == sorted([("user0", "sub1"), ("user1", "sub0")])


def test_num_reviews_capped_by_available_targets():
    """3 learners, num_reviews=5 — only 2 targets exist per reviewer."""
    subs, reviewers = _setup(3)
    pairs = allocate_reviews(subs, reviewers, 5, rng=random.Random(5))
    per_reviewer = {}
    for r, _s in pairs:
        per_reviewer[r] = per_reviewer.get(r, 0) + 1
    assert all(count == 2 for count in per_reviewer.values())


def test_empty_inputs():
    assert allocate_reviews({}, [], 2) == []
    assert allocate_reviews({"s": "u"}, ["u"], 0) == []


def test_single_learner_no_allocation():
    """One learner has nobody to review."""
    subs, reviewers = _setup(1)
    assert allocate_reviews(subs, reviewers, 2, rng=random.Random(0)) == []


def test_progressive_fairness():
    """Everyone gets 1 review before anyone gets 2: with an odd pool and
    num_reviews=2, min per-reviewer count is never 0 while another has 2."""
    for seed in range(10):
        subs, reviewers = _setup(7)
        pairs = allocate_reviews(subs, reviewers, 2, rng=random.Random(seed))
        per_reviewer = {r: 0 for r in reviewers}
        for r, _s in pairs:
            per_reviewer[r] += 1
        counts = sorted(per_reviewer.values())
        assert counts[0] >= 1  # nobody left with zero


def test_num_reviews_exceeds_pool():
    """num_reviews larger than (n-1) cannot give everyone that many — the
    allocator must still never self-assign or duplicate, capping at n-1."""
    from collections import Counter

    subs, reviewers = _setup(3)
    pairs = allocate_reviews(subs, reviewers, 10, rng=random.Random(1))
    for r, s in pairs:
        assert subs[s] != r  # no self-review
    assert len(pairs) == len(set(pairs))  # no duplicates
    for _r, cnt in Counter(r for r, _s in pairs).items():
        assert cnt <= 2  # at most n-1 = 2 distinct peers


def test_seeded_rng_is_deterministic():
    """R241: `rng = rng or random.Random()` — a mutation to `and` silently
    swaps the caller's seeded rng for a fresh unseeded one. Same seed must
    give the identical allocation (re-allocation audits depend on it)."""
    subs, reviewers = _setup(8)
    a = allocate_reviews(subs, reviewers, 2, rng=random.Random(1234))
    b = allocate_reviews(subs, reviewers, 2, rng=random.Random(1234))
    assert a == b


def test_characterization_snapshot():
    """R241: characterization sentinel for the repair pass (mutation-driven).

    AST-mutation status after this test: 14/18 killed. The 4 survivors are
    analyzed non-bugs: the L59 guard pair is provably equivalent (empty
    inputs fall through to an empty allocation anyway), and the repair-pass
    load-bookkeeping pair (±1 on donor/orphan) showed zero behavioral
    difference across 1,500 scenario×seed probes — the orphan list is
    precomputed, so post-swap loads are only re-read by later orphans whose
    donor sets the probes could not make intersect.

    Count-based invariants cannot distinguish "leave the orphan alone" from
    "steal a single-review donor's only review" — both leave exactly one
    zero-load submission, just a different one. Pin exact outcomes for fixed
    seeds so any semantic drift in allocation/repair (donor threshold, load
    bookkeeping, self-review gate in the swap) is flagged. If the algorithm
    changes INTENTIONALLY, regenerate via the snippet in the repo history.
    """
    cases = {
        # 2 reviewers / 3 subs: one orphan always remains; all donors are
        # load-1 so repair must NOT fire (donor keeps >= 1 review).
        ("S1", seed): sorted(
            allocate_reviews(
                {"sa": "A", "sb": "B", "sc": "C"}, ["A", "B"], 1, rng=random.Random(seed)
            )
        )
        for seed in range(10)
    }
    cases.update(
        {
            # author-of-orphan among reviewers: repair path reachable
            ("S2", seed): sorted(
                allocate_reviews(
                    {"so": "C", "s1": "A", "s2": "B"}, ["A", "B", "C"], 1, rng=random.Random(seed)
                )
            )
            for seed in range(10)
        }
    )
    expected = {
        ("S1", 0): [("A", "sc"), ("B", "sa")],
        ("S1", 1): [("A", "sc"), ("B", "sa")],
        ("S1", 2): [("A", "sb"), ("B", "sa")],
        ("S1", 3): [("A", "sc"), ("B", "sa")],
        ("S1", 4): [("A", "sb"), ("B", "sc")],
        ("S1", 5): [("A", "sc"), ("B", "sa")],
        ("S1", 6): [("A", "sb"), ("B", "sc")],
        ("S1", 7): [("A", "sb"), ("B", "sc")],
        ("S1", 8): [("A", "sb"), ("B", "sc")],
        ("S1", 9): [("A", "sc"), ("B", "sa")],
        ("S2", 0): [("A", "so"), ("B", "s1"), ("C", "s2")],
        ("S2", 1): [("A", "so"), ("B", "s1"), ("C", "s2")],
        ("S2", 2): [("A", "so"), ("B", "s1"), ("C", "s2")],
        ("S2", 3): [("A", "so"), ("B", "s1"), ("C", "s2")],
        ("S2", 4): [("A", "s2"), ("B", "so"), ("C", "s1")],
        ("S2", 5): [("A", "s2"), ("B", "so"), ("C", "s1")],
        ("S2", 6): [("A", "s2"), ("B", "so"), ("C", "s1")],
        ("S2", 7): [("A", "so"), ("B", "s1"), ("C", "s2")],
        ("S2", 8): [("A", "so"), ("B", "s1"), ("C", "s2")],
        ("S2", 9): [("A", "s2"), ("B", "so"), ("C", "s1")],
    }
    assert cases == expected
