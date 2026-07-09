"""reviewer_agent.py — the qualitative reviewer, a separate role (L39).

Runs AFTER verify_agent.py passes. Reads the artifacts (diff summary,
state, feedback, gate verdict) READ-ONLY and writes a review report. It
never patches the diff — if it says "fix this", the next builder turn
does the fix. Role separation (different prompt, different inputs, no
write access to code) is the discipline, not a different model.

Scorers are deterministic stubs here; a real reviewer calls an LLM per
dimension with bias mitigations. The Worker shape (read-only on diff,
write-only on report) is the real lesson.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path

LAB = Path(__file__).parent


@dataclass
class ReviewerInputs:
    task_goal: str
    changed_files: list          # what was touched
    assumptions: list            # from agent_state.json
    acceptance_proved_goal: bool # did the acceptance test the REAL goal?
    state_next_action: dict      # is handoff clean?
    gate_passed: bool


def score(inp: ReviewerInputs) -> dict:
    d = {}
    # problem_fit: did it touch the file the task is about, nothing weird?
    d["problem_fit"] = 2 if inp.changed_files == ["user_service.py"] else (
        1 if "user_service.py" in inp.changed_files else 0)
    # scope_discipline: only the allowed file?
    d["scope_discipline"] = 2 if inp.changed_files == ["user_service.py"] else 0
    # assumptions: written down AND flagged unverified?
    d["assumptions"] = 2 if inp.assumptions and all(
        "verified" in a for a in inp.assumptions) else (1 if inp.assumptions else 0)
    # verification_quality: acceptance proved the REAL goal, not a weaker one?
    d["verification_quality"] = 2 if inp.acceptance_proved_goal else 0
    # handoff_readiness: next_action present and points at a task?
    d["handoff_readiness"] = 2 if inp.state_next_action.get("task_id") else 0
    return d


def review(task_id: str, inp: ReviewerInputs) -> dict:
    scores = score(inp)
    total = sum(scores.values())
    verdict = "pass" if total >= 7 else ("soft_fail" if total >= 5 else "hard_fail")
    report = {"task_id": task_id, "scores": scores, "total": total,
              "verdict": verdict,
              "note": "reviewer reads-only; fixes go to the next builder turn"}
    out = LAB / "outputs" / "review"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{task_id}.json").write_text(json.dumps(report, indent=2))
    return report


def _show(title, r):
    print(f"=== {title} ===")
    for dim, s in r["scores"].items():
        print(f"  {s}/2  {dim}")
    print(f"  total {r['total']}/10 -> {r['verdict']}\n")


if __name__ == "__main__":
    clean = ReviewerInputs(
        task_goal="add input validation to create_user",
        changed_files=["user_service.py"],
        assumptions=[{"claim": "email uses simple regex", "verified": False}],
        acceptance_proved_goal=True,
        state_next_action={"task_id": "T1", "step": "done"},
        gate_passed=True)
    _show("A: clean change", review("T1", clean))

    # right tests green, but acceptance proved a WEAKER version (not the real goal)
    wrong = ReviewerInputs(
        task_goal="add input validation to create_user",
        changed_files=["user_service.py"],
        assumptions=[],                       # undocumented assumptions
        acceptance_proved_goal=False,         # tested a weaker thing
        state_next_action={"task_id": "T1", "step": "done"},
        gate_passed=True)                     # gate PASSED — this is what gate can't catch
    _show("B: right tests, wrong problem (gate passed!)", review("T1b", wrong))
