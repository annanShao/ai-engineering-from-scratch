# Agent Workbench Pack v1.0.0

A versioned, framework-agnostic pack that wires the seven workbench surfaces into
any repo. Built across Phase 14 L31-L42.

## Install
```
bin/install.sh /path/to/target-repo        # drops pack into .agent-workbench/
```

## What's inside (surface -> primitive)
| Surface | File | Primitive |
|---|---|---|
| Instructions | `docs/agent-rules.md` + `scripts/rule_checker.py` | policy + function |
| State | `schemas/agent_state.schema.json` + `scripts/state_manager.py` | session persistence |
| Init | `scripts/init_agent.py` | trigger (startup) |
| Scope | `schemas/scope_contract.example.json` + `scripts/scope_checker.py` | authorization policy |
| Feedback | `scripts/run_with_feedback.py` | queue |
| Verification | `scripts/verify_agent.py` | verification function (fails closed) |
| Review | `docs/reviewer-rubric.md` + `scripts/reviewer_agent.py` | worker (read-only on diff) |
| Handoff | `scripts/generate_handoff.py` | trigger (session-end) |

## What stays out
- Project-specific tasks (they live on the target repo's board).
- Vendor SDK calls (the pack is framework-agnostic).
- Onboarding prose (the pack sits next to onboarding, not inside it).

## Versioning
`VERSION` is semver. Schema/script changes needing migration bump major; doc-only
changes bump patch. The target's `agent_state.json` records the pack version it was
initialized against.
