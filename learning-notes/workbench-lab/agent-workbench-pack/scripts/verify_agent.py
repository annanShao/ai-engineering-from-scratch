"""verify_agent.py — the deterministic verification gate (L38).

Reads artifacts the agent already produced (git diff, scope contract,
rules, and re-runs acceptance) and makes the call. No LLM judges here —
this gate answers "did it pass?", not "is it good?" (the reviewer, L39,
does the qualitative part). Fails closed: any block finding forbids
passed:true. Block findings can only be overridden by a human, recorded.

This is the confluence of L33 (rules), L36 (scope), L37 (feedback).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

LAB = Path(__file__).parent
sys.path.insert(0, str(LAB))

from scope_checker import scope_check, CONTRACT          # noqa: E402
from rule_checker import run_checks as run_rule_checks    # noqa: E402
from run_with_feedback import run_with_feedback, succeeded  # noqa: E402


def verify(task_id: str, changed_files: list[str]) -> dict:
    findings = []

    # 1. scope: no forbidden / off-scope writes (L36)
    for v in scope_check(changed_files):
        findings.append({"check": "scope", "severity": "block",
                         "detail": f"{v['file']}: {v['reason']}"})

    # 2. rules: all block-severity rules pass (L33)
    for r in run_rule_checks(changed_files):
        if not r["passed"] and r["severity"] == "block":
            findings.append({"check": f"rule:{r['rule']}", "severity": "block",
                             "detail": r["detail"]})

    # 3. acceptance: every acceptance command actually ran and exited 0 (L37)
    for cmd in CONTRACT["acceptance_criteria"]:
        rec = run_with_feedback(cmd.split(), agent_note=f"acceptance for {task_id}",
                                cwd=LAB.parents[1])
        if rec["exit_code"] is None:
            findings.append({"check": "acceptance", "severity": "block",
                             "detail": f"null exit (no proof it ran): {cmd}"})
        elif not succeeded(rec):
            findings.append({"check": "acceptance", "severity": "block",
                             "detail": f"exit {rec['exit_code']}: {cmd}"})

    blocked = [f for f in findings if f["severity"] == "block"]
    report = {"task_id": task_id, "passed": len(blocked) == 0, "findings": findings}
    out = LAB / "outputs" / "verification"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{task_id}.json").write_text(json.dumps(report, indent=2))
    return report


def _show(title, report):
    print(f"=== {title} ===")
    for f in report["findings"]:
        print(f"  BLOCK  {f['check']:20} {f['detail']}")
    verdict = "PASS (-> reviewer L39)" if report["passed"] else "REFUSE done, surface to human"
    print(f"  verdict: passed={report['passed']}  -> {verdict}\n")


if __name__ == "__main__":
    # Scenario A: agent stayed in scope, edited only user_service.py
    _show("A: clean, in-scope",
          verify("T1", ["learning-notes/workbench-lab/toy-repo/user_service.py"]))

    # Scenario B: scope creep + edited a forbidden test file
    _show("B: creep + forbidden write",
          verify("T1", ["learning-notes/workbench-lab/toy-repo/user_service.py",
                        "learning-notes/workbench-lab/toy-repo/test_user_service.py",
                        "learning-notes/workbench-lab/toy-repo/email_helper.py"]))
