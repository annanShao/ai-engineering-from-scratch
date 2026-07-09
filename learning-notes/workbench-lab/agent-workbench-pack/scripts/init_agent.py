"""init_agent.py — startup health check (L35).

Runs BEFORE the agent does anything. Deterministic plumbing only: no
network, no LLM (those belong in the agent, not the probe). Fail loud,
fail fast, fail in one place — refuse to start when the workbench is
broken. Idempotent: run twice and the second run is a no-op but for the
timestamp. Wire into a Claude Code pre-task hook / CI setup job / Docker
entrypoint (Trigger primitive; Startup category from L33).
"""
from __future__ import annotations
import importlib.util
import json
import sys
from pathlib import Path

LAB = Path(__file__).parent


def probe(name, ok, detail, severity="block"):
    return {"probe": name, "status": "pass" if ok else "fail",
            "severity": severity, "detail": detail}


def run_probes():
    probes = []

    # 1. runtime version — wrong version = silent wrong-version bugs
    v = sys.version_info
    probes.append(probe("python>=3.8", v >= (3, 8), f"{v.major}.{v.minor}"))

    # 2. dependency availability — catch a missing package now, not mid-task
    has_pytest = importlib.util.find_spec("pytest") is not None
    probes.append(probe("dep:pytest", has_pytest,
                        "importable" if has_pytest else "MISSING"))

    # 3. test command resolvable — the agent must know how to verify (L33 verify)
    toy = LAB / "toy-repo"
    probes.append(probe("test-target", (toy / "test_user_service.py").exists(),
                        str(toy)))

    # 4. rules present — else rule_checker can't run (L33)
    probes.append(probe("rules-file", (LAB / "docs" / "agent-rules.md").exists(),
                        "docs/agent-rules.md"))

    # 5. state fresh + schema-valid — stale/corrupt state is a footgun (L34)
    try:
        from state_manager import StateManager, SchemaError  # noqa
        sm = StateManager(LAB / "agent_state.json", LAB / "agent_state.schema.json")
        st = sm.load()
        probes.append(probe("state-valid", True, f"active={st['active_task_id']}"))
    except Exception as e:  # SchemaError, FileNotFoundError, JSONDecodeError
        probes.append(probe("state-valid", False, f"{type(e).__name__}: {e}"))

    # 6. board parseable
    try:
        board = json.loads((LAB / "task_board.json").read_text())
        n = len(board.get("tasks", []))
        probes.append(probe("board-valid", True, f"{n} task(s)"))
    except Exception as e:
        probes.append(probe("board-valid", False, str(e)))

    return probes


if __name__ == "__main__":
    sys.path.insert(0, str(LAB))
    probes = run_probes()
    report = {"probes": probes, "generated": "2026-07-09T00:00:00Z"}
    (LAB / "init_report.json").write_text(json.dumps(report, indent=2))

    for p in probes:
        mark = "OK  " if p["status"] == "pass" else f"FAIL[{p['severity']}]"
        print(f"  {mark:12} {p['probe']:14} {p['detail']}")

    blocked = [p for p in probes if p["status"] == "fail" and p["severity"] == "block"]
    if blocked:
        print(f"\n  HALT: {len(blocked)} block probe(s) failed — workbench not ready, "
              f"surface to human. Agent will NOT start.")
        sys.exit(1)
    print("\n  READY: workbench healthy, agent may start.")
