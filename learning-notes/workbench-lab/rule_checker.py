"""Detective enforcement: turns agent-rules.md from a soft contract into runnable checks.

Design decisions baked in (L33 review):
- Checks read GROUND TRUTH (git-changed files), NOT agent_state.touched_files.
  A misbehaving agent may not record what it did (L26: verify by external state,
  don't trust the agent's self-report).
- One generic check per shape (path-based, test-based) so adding a rule that
  reuses a shape needs no new check function.
- Severity drives runtime behavior: only `block` refuses; warn/info report.

This file is the DETECTIVE layer. The PREVENTIVE layer (a write tool that
refuses forbidden paths before the edit happens) arrives in L36.
"""
from __future__ import annotations
import fnmatch
import json
import subprocess
from pathlib import Path

LAB = Path(__file__).parent


# ---- rule parser: one rule per "### slug" heading ----------------------------

def parse_rules(md_path: Path) -> list[dict]:
    rules, cur = [], None
    for line in md_path.read_text().splitlines():
        if line.startswith("### "):
            cur = {"slug": line[4:].strip()}
            rules.append(cur)
        elif line.startswith("- ") and cur is not None and ":" in line:
            k, v = line[2:].split(":", 1)
            cur[k.strip()] = v.strip()
    return rules


# ---- ground-truth source: what the agent ACTUALLY changed --------------------

def git_changed_files() -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--", "."],
        capture_output=True, text=True, cwd=LAB,
    ).stdout
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


# ---- checks: one function per `check` field ----------------------------------

def check_forbidden_paths(changed, rule):
    globs = [g.strip() for g in rule.get("globs", "").split(",") if g.strip()]
    hits = [f for f in changed if any(fnmatch.fnmatch(f, g) for g in globs)]
    return (not hits, f"edited forbidden: {hits}" if hits else "ok")


def check_scope(changed, rule):
    allowed = [g.strip() for g in rule.get("allowed", "").split(",") if g.strip()]
    leaks = [f for f in changed if not any(fnmatch.fnmatch(f, g) for g in allowed)]
    return (not leaks, f"out-of-scope edits: {leaks}" if leaks else "ok")


def check_tests_green(changed, rule):
    r = subprocess.run(["python3", "-m", "pytest", "-q", "toy-repo"],
                       capture_output=True, text=True, cwd=LAB)
    return (r.returncode == 0, "tests pass" if r.returncode == 0 else "tests failing")


CHECKS = {
    "check_forbidden_paths": check_forbidden_paths,
    "check_scope": check_scope,
    "check_tests_green": check_tests_green,
}


def run_checks(changed: list[str]) -> list[dict]:
    rules = parse_rules(LAB / "docs" / "agent-rules.md")
    report = []
    for r in rules:
        ok, detail = CHECKS[r["check"]](changed, r)
        report.append({"rule": r["slug"], "severity": r.get("severity", "warn"),
                       "passed": ok, "detail": detail})
    return report


if __name__ == "__main__":
    print("=== Scenario A: agent edited only user_service.py (good) ===")
    for row in run_checks(["toy-repo/user_service.py"]):
        mark = "PASS" if row["passed"] else f"FAIL[{row['severity']}]"
        print(f"  {mark:12} {row['rule']:16} {row['detail']}")

    print("\n=== Scenario B: agent edited the test file to cheat (bad) ===")
    report = run_checks(["toy-repo/test_user_service.py"])
    for row in report:
        mark = "PASS" if row["passed"] else f"FAIL[{row['severity']}]"
        print(f"  {mark:12} {row['rule']:16} {row['detail']}")

    blocked = [r for r in report if not r["passed"] and r["severity"] == "block"]
    (LAB / "rule_report.json").write_text(json.dumps(report, indent=2))
    print(f"\n  -> {len(blocked)} block-level violation(s); runtime would REFUSE this turn.")
