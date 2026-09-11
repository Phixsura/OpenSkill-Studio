#!/usr/bin/env python3
"""Lightweight AST mutation harness (R202) — no mutmut.

For each target (file, function, fast-test-selection): enumerate high-value
mutants (comparison flips, and/or swaps, int boundary +-1, arith flips),
apply ONE at a time by rewriting the real file, run the selected tests,
record killed/survived, restore. Pure functions + property tests = seconds
per mutant."""
import ast
import json
import pathlib
import subprocess
import sys
import time

CMP_FLIPS = {ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt,
             ast.Eq: ast.NotEq, ast.NotEq: ast.Eq}
ARITH = {ast.Add: ast.Sub, ast.Sub: ast.Add}
BOOLF = {ast.And: ast.Or, ast.Or: ast.And}

def enumerate_mutants(tree, funcnames):
    """Yield (site_id, description, apply_fn) for nodes inside target functions."""
    sites = []
    class V(ast.NodeVisitor):
        def __init__(self): self.stack = []
        def visit_FunctionDef(self, n): self._f(n)
        def visit_AsyncFunctionDef(self, n): self._f(n)
        def _f(self, n):
            self.stack.append(n.name); self.generic_visit(n); self.stack.pop()
        def generic_visit(self, node):
            in_target = any(f in funcnames for f in self.stack)
            if in_target:
                if isinstance(node, ast.Compare):
                    for i, op in enumerate(node.ops):
                        t = type(op)
                        if t in CMP_FLIPS:
                            sites.append(("cmp", node, i, CMP_FLIPS[t],
                                          f"L{node.lineno}: {t.__name__}->{CMP_FLIPS[t].__name__}"))
                elif isinstance(node, ast.BinOp) and type(node.op) in ARITH:
                    sites.append(("arith", node, None, ARITH[type(node.op)],
                                  f"L{node.lineno}: {type(node.op).__name__}->{ARITH[type(node.op)].__name__}"))
                elif isinstance(node, ast.BoolOp) and type(node.op) in BOOLF:
                    sites.append(("bool", node, None, BOOLF[type(node.op)],
                                  f"L{node.lineno}: {type(node.op).__name__}->{BOOLF[type(node.op)].__name__}"))
                elif (isinstance(node, ast.Constant) and type(node.value) is int
                      and 0 < abs(node.value) < 10000):
                    sites.append(("const", node, None, node.value + 1,
                                  f"L{node.lineno}: {node.value}->{node.value+1}"))
            super().generic_visit(node)
    V().visit(tree)
    return sites

def apply_site(kind, node, idx, repl):
    if kind == "cmp":
        old = node.ops[idx]; node.ops[idx] = repl(); return lambda: node.ops.__setitem__(idx, old)
    if kind in ("arith", "bool"):
        old = node.op; node.op = repl(); return (lambda: setattr(node, "op", old))
    if kind == "const":
        old = node.value; node.value = repl; return (lambda: setattr(node, "value", old))

def run(path, funcs, test_cmd, limit=None, timeout=300):
    p = pathlib.Path(path)
    # Corruption guard: only mutate a git-clean file (a killed prior run can
    # leave an ast.unparse'd copy on disk — baking that in as "original"
    # permanently reformats the source). Restore via git if dirty.
    st = subprocess.run(["git", "status", "--short", str(p)], capture_output=True, text=True).stdout.strip()
    if st:
        # R250 post-mortem: auto-checkout WIPED an uncommitted fix on the
        # target file (and the then-red baseline made every mutant look
        # killed). A dirty target now aborts instead — commit or stash first.
        raise SystemExit(f"REFUSING to mutate dirty file {path} — commit or stash it first")
    original = p.read_text()
    tree = ast.parse(original)
    sites = enumerate_mutants(tree, set(funcs))
    if limit: sites = sites[:limit]
    print(f"{path} funcs={funcs}: {len(sites)} mutants", flush=True)
    killed, survived = 0, []
    t0 = time.time()
    try:
        for n, (kind, node, idx, repl, desc) in enumerate(sites):
            undo = apply_site(kind, node, idx, repl)
            p.write_text(ast.unparse(tree))
            try:
                r = subprocess.run(test_cmd, capture_output=True, timeout=timeout)
                rc = r.returncode
            except subprocess.TimeoutExpired:
                # a mutant that HANGS the tests (infinite loop/retry) is dead,
                # not a harness crash — count it killed and keep sweeping
                rc = -1
            undo()
            if rc == 0:
                survived.append(desc); tag = "SURVIVED"
            else:
                killed += 1; tag = "killed (timeout)" if rc == -1 else "killed"
            if tag == "SURVIVED" or (n+1) % 25 == 0:
                print(f"  [{n+1}/{len(sites)}] {desc}: {tag}", flush=True)
    finally:
        p.write_text(original)
    dt = time.time() - t0
    print(f"  DONE {killed} killed / {len(survived)} survived in {dt:.0f}s ({len(sites)/max(dt,1):.2f}/s)")
    return survived

if __name__ == "__main__":
    with open(sys.argv[1]) as _cfgf:
        cfg = json.load(_cfgf)
    all_surv = {}
    for t in cfg:
        s = run(t["path"], t["funcs"], t["cmd"], t.get("limit"), t.get("timeout", 300))
        if s: all_surv[f"{t['path']}:{','.join(t['funcs'])}"] = s
    print("\n═══ SURVIVORS ═══")
    print(json.dumps(all_surv, indent=1))
