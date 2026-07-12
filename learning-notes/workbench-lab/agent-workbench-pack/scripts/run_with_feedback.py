"""run_with_feedback.py — every command goes through the runner (L37).

Closes the gap where an agent claims "tests pass" without a real result.
Each record carries the exact command, deterministically-truncated
stdout/stderr, the exit code (the unambiguous success signal), duration,
and a one-line agent note. The agent reads records next turn; the
verification gate reads them at task close.

Rule: no exit, no progress. A record with exit_code=null must NEVER be
read as success (L26: success is verified by external state, not claimed
by the agent).
"""
from __future__ import annotations
import json
import shlex
import subprocess
import time
from pathlib import Path

LAB = Path(__file__).parent
RECORD = LAB / "feedback_record.jsonl"
TAIL_LINES = 15

SECRET_MARKERS = ("Bearer ", "password=", "api_key=", "api-key=", "apikey=")


def _redact(text: str) -> str:
    # redact at WRITE time — the file on disk is what an attacker reaches
    out = []
    for line in text.splitlines():
        if any(m.lower() in line.lower() for m in SECRET_MARKERS):
            out.append("[REDACTED secret-shaped line]")
        else:
            out.append(line)
    return "\n".join(out)


def _tail(text: str, n=TAIL_LINES) -> str:
    lines = text.splitlines()
    if len(lines) <= n:
        return _redact(text)
    kept = lines[-n:]
    return f"...truncated {len(lines) - n} lines...\n" + _redact("\n".join(kept))


def run_with_feedback(command: list[str], agent_note: str, cwd=None) -> dict:
    started = time.time()
    try:
        r = subprocess.run(command, capture_output=True, text=True,
                           cwd=cwd or LAB, timeout=60)
        rec = {"command": " ".join(shlex.quote(c) for c in command),
               "stdout_tail": _tail(r.stdout), "stderr_tail": _tail(r.stderr),
               "exit_code": r.returncode,
               "duration_ms": int((time.time() - started) * 1000),
               "agent_note": agent_note}
    except Exception as e:
        # no exit captured -> exit_code null; agent MUST NOT claim success
        rec = {"command": " ".join(command), "stdout_tail": "", "stderr_tail": "",
               "exit_code": None, "error": f"{type(e).__name__}: {e}",
               "duration_ms": int((time.time() - started) * 1000),
               "agent_note": agent_note}
    with RECORD.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def succeeded(rec: dict) -> bool:
    """The only honest success test: a real exit code of 0."""
    return rec.get("exit_code") == 0


if __name__ == "__main__":
    print("=== command 1: run the toy-repo tests (should pass) ===")
    r1 = run_with_feedback(["python3", "-m", "pytest", "-q", "toy-repo"],
                           agent_note="expect 2 passed, 3 xfailed")
    print(f"  exit={r1['exit_code']} ({r1['duration_ms']}ms) succeeded={succeeded(r1)}")

    print("\n=== command 2: a command that fails (exit != 0) ===")
    r2 = run_with_feedback(["python3", "-c", "import sys; sys.exit(3)"],
                           agent_note="expect this to fail")
    print(f"  exit={r2['exit_code']} succeeded={succeeded(r2)}")
    print(f"  -> agent CANNOT claim success: succeeded()={succeeded(r2)}")

    print("\n=== command 3: a command that crashes before exit (null) ===")
    r3 = run_with_feedback(["/nonexistent/binary"], agent_note="expect no exit")
    print(f"  exit={r3['exit_code']} succeeded={succeeded(r3)}  <- null exit, no progress")

    print(f"\n  {sum(1 for _ in RECORD.open())} records now in feedback_record.jsonl")
