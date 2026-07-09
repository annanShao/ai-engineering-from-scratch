"""scope_checker.py — the preventive/detective boundary for scope creep (L36).

Reads the scope_contract.json (the promise) and the actual git-changed files
(the result, ground truth — L26: don't trust the agent's self-report) and
returns violations. forbidden wins over allowed (least privilege). A file
that is neither allowed nor forbidden is off-scope creep.

Used two ways:
- Preventive: a write tool calls `is_write_allowed(path)` BEFORE editing.
- Detective: the verification gate (L38) calls `scope_check(changed)` AFTER.
"""
from __future__ import annotations
import fnmatch
import json
import subprocess
from pathlib import Path

LAB = Path(__file__).parent
CONTRACT = json.loads((LAB / "scope_contract.json").read_text())


def _match(path, globs):
    return any(fnmatch.fnmatch(path, g) for g in globs)


def is_write_allowed(path: str) -> tuple[bool, str]:
    """Preventive check — call this inside the write tool before editing."""
    if _match(path, CONTRACT["forbidden_files"]):
        return False, "forbidden_files"
    if not _match(path, CONTRACT["allowed_files"]):
        return False, "off-scope (not in allowed_files)"
    return True, "ok"


def git_changed_files():
    out = subprocess.run(["git", "diff", "--name-only", "HEAD"],
                         capture_output=True, text=True,
                         cwd=LAB.parents[1]).stdout  # repo root
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def scope_check(changed):
    """Detective check — call this in the verification gate after the turn."""
    violations = []
    for f in changed:
        ok, reason = is_write_allowed(f)
        if not ok:
            violations.append({"file": f, "reason": reason})
    return violations


if __name__ == "__main__":
    print("=== Preventive: is_write_allowed(path) ===")
    for p in ["learning-notes/workbench-lab/toy-repo/user_service.py",
              "learning-notes/workbench-lab/toy-repo/test_user_service.py",
              "learning-notes/workbench-lab/toy-repo/email_helper.py"]:
        ok, reason = is_write_allowed(p)
        print(f"  {'ALLOW' if ok else 'BLOCK':6} {p.split('/')[-1]:22} {reason}")

    print("\n=== Detective: scope_check(simulated creep diff) ===")
    creep = [
        "learning-notes/workbench-lab/toy-repo/user_service.py",   # in scope
        "learning-notes/workbench-lab/toy-repo/test_user_service.py",  # forbidden
        "learning-notes/workbench-lab/toy-repo/email_helper.py",   # off-scope creep
    ]
    v = scope_check(creep)
    for row in v:
        print(f"  VIOLATION {row['file'].split('/')[-1]:22} {row['reason']}")
    print(f"\n  {len(v)} violation(s) — verification gate would REFUSE this turn.")
