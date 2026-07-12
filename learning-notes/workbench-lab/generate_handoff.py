"""generate_handoff.py — the session-end handoff packet (L40).

Generated, not written: reads the workbench artifacts (state, gate
verdict, review, feedback) and emits handoff.md (human) + handoff.json
(next agent). The agent's job is to leave the workbench summarizable, not
to write the summary. A cleanup CHECK runs first — a handoff built on a
dirty tree is a forwarded mess, not a handoff. next_action is the
load-bearing field: without it this is a status report, not a handoff.

Trigger primitive: a session-end trigger writes it; the next session's
startup trigger reads it.
"""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

LAB = Path(__file__).parent
REPO_ROOT = LAB.parents[1]


def cleanup_check() -> list[dict]:
    """Emit blocking issues; empty list is the precondition for a handoff."""
    issues = []
    # working tree: uncommitted changes inside the lab look like intent to the next agent
    dirty = subprocess.run(["git", "status", "--porcelain", "learning-notes/workbench-lab"],
                           capture_output=True, text=True, cwd=REPO_ROOT).stdout.strip()
    if dirty:
        issues.append({"check": "working_tree", "detail": f"{len(dirty.splitlines())} uncommitted path(s)"})
    # temp artifacts
    tmps = list(LAB.rglob("*.tmp"))
    if tmps:
        issues.append({"check": "temp_artifacts", "detail": f"{len(tmps)} stray *.tmp"})
    return issues


def load_snapshot() -> dict:
    state = json.loads((LAB / "agent_state.json").read_text())
    verdict = _maybe(LAB / "outputs" / "verification" / f"{state['active_task_id']}.json")
    review = _maybe(LAB / "outputs" / "review" / f"{state['active_task_id']}.json")
    feedback = _load_feedback(LAB / "feedback_record.jsonl")
    return {"state": state, "verdict": verdict, "review": review, "feedback": feedback}


def _maybe(p: Path):
    return json.loads(p.read_text()) if p.exists() else None


def _load_feedback(p: Path, k=3):
    if not p.exists():
        return []
    recs = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    # keep last K + every non-zero/null exit (the failures matter)
    fails = [r for r in recs if r.get("exit_code") not in (0,)]
    return (recs[-k:] + fails)[-10:]


def generate_handoff(snap: dict) -> tuple[str, dict]:
    st = snap["state"]
    payload = {
        "summary": f"Task {st['active_task_id']}: {st['next_action'].get('step', 'in progress')}",
        "changed_files": st.get("touched_files", []),
        "commands_run": [f["command"] for f in snap["feedback"] if "command" in f],
        "failed_attempts": [f for f in snap["feedback"] if f.get("exit_code") not in (0, None)],
        "open_risks": [a for a in st.get("assumptions", []) if not a.get("verified")],
        "next_action": st.get("next_action"),   # load-bearing
        "verdict_pointer": {
            "verification": bool(snap["verdict"]) and snap["verdict"].get("passed"),
            "review": bool(snap["review"]) and snap["review"].get("verdict"),
        },
    }
    md = f"""# Handoff — {payload['summary']}

**Next action:** {payload['next_action']}

- changed files: {[f.get('path') for f in payload['changed_files']] or 'none recorded'}
- gate passed: {payload['verdict_pointer']['verification']}
- review verdict: {payload['verdict_pointer']['review']}
- open risks (unverified assumptions): {[r.get('claim') for r in payload['open_risks']] or 'none'}
- failed attempts: {len(payload['failed_attempts'])}
"""
    return md, payload


if __name__ == "__main__":
    issues = cleanup_check()
    if issues:
        print("CLEANUP BLOCKS handoff — dirty workbench, not summarizable:")
        for i in issues:
            print(f"  - {i['check']}: {i['detail']}")
        print("\n  (commit/clean first; a handoff on a dirty tree is a forwarded mess)")
    else:
        print("cleanup clean — safe to leave.")
    md, payload = generate_handoff(load_snapshot())
    print("\n=== handoff.md ===")
    print(md)
    if not payload["next_action"]:
        print("WARNING: no next_action — this is a status report, not a handoff.")
