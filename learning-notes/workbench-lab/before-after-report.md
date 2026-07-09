# Before / After — Task T1 through two pipelines

Task: add input validation to `create_user` (reject empty username, negative age,
malformed email) and prove it with tests, without touching the test file.

The workbench pipeline actually ran end-to-end on this lab. Numbers below are real.

| Outcome | Prompt-only | Workbench-guided |
|---|---|---|
| `tests_actually_run` | claimed, unverifiable | **yes** — exit 0 captured via feedback runner (L37) |
| `acceptance_met` | maybe (5/5? unknown) | **yes** — 5 passed, exit 0 (was 3 failed before) |
| `files_outside_scope` | scope creep likely | **0** — gate saw only `user_service.py` (L36/L38) |
| `handoff_quality` | "we made progress" | **full packet** with next_action (L40) |
| `reviewer_total` | none | **10/10 pass** (L39) |

## Pipeline trace (workbench-guided)

1. **init (L35)** — READY: workbench healthy.
2. **build** — edited only `toy-repo/user_service.py` (scope-allowed).
3. **acceptance via feedback runner (L37)** — pytest exit 0, `succeeded()=True`.
4. **verification gate (L38)** — `passed=True`, 0 findings.
5. **reviewer (L39)** — 10/10, pass.
6. **counterfactual** — a prompt-only run that also edited the forbidden test file:
   gate `passed=False`, 3 block findings. The workbench refuses; prompt-only ships it.

## The point

Same model, same task. The difference is not intelligence — it is the surfaces
around the model: scope refused the creep, the feedback runner made "tests passed"
verifiable, the gate refused on ground truth, the reviewer caught quality, and the
handoff left the next session a real starting point. Harness, not model.
