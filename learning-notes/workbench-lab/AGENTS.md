# Agent Workbench Router

Short by design. This file routes; details live in deeper files loaded only when needed.

Read before acting:
- **State (where you are):** `agent_state.json`
- **Task board (what's left):** `task_board.json`
- **Rules (startup, every session):** `docs/agent-rules.md` — checked by `rule_checker.py`

## Enforcement
Rules are DECLARED in `docs/agent-rules.md` and ENFORCED two ways:
- Detective (now): `python3 rule_checker.py` reads git-changed files and flags `block` violations.
- Preventive (L36): the write tool will refuse forbidden/out-of-scope paths before the edit.

## Verify
```
python3 -m pytest -q learning-notes/workbench-lab/toy-repo
```
Done = all validation tests pass AND happy-path tests stay green.

## Scope (task T1)
- **Allowed:** `toy-repo/user_service.py`
- **Forbidden:** `toy-repo/test_user_service.py` — tests are authoritative; do not edit them to pass.

<!-- Router only. When this file grows past a screen, push detail into docs/ and keep this a map. -->
