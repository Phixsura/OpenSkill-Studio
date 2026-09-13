# R206 — CrossHair symbolic-execution contracts

Unlike Hypothesis (bounded random sampling), CrossHair drives an SMT solver
to PROVE each `post:` condition for ALL inputs in the `pre:` domain, or emit
a concrete counterexample. These target the integer/boolean logic core of
the money engine where the solver is strongest.

Run (not part of the default pytest run — solver is slow, CI-nightly):

    cd apps/api
    uv run --with crosshair-tool crosshair check tests/symbolic/ --per_condition_timeout=25

Exit 0 + no output == every contract proven. A counterexample prints the
exact failing input. 10 contracts across both files proven clean (R206):
leap rule, month-length bounds, cost reversal antisymmetry + sign-follow,
min-fee-never-flips-credit, semver patch-monotone / release>prerelease /
reflexive, proration net==component-sum, days_left bounds.
