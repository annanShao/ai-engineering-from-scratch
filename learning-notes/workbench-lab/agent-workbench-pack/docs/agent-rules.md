# Agent Rules

The human-readable, reviewable contract. Each rule is a heading with machine-readable
fields. `check` names a function in `rule_checker.py`. This file DECLARES policy;
enforcement lives in the checker (detective) and — from L36 — the write tool (preventive).

## Forbidden

### no-edit-tests
- category: forbidden
- severity: block
- description: Never edit test files to make them pass. Tests are authoritative.
- globs: **/test_*.py
- check: check_forbidden_paths

### stay-in-scope
- category: forbidden
- severity: block
- description: Only modify files in task T1's allowed set.
- allowed: **/user_service.py
- check: check_scope

## Definition of done

### t1-tests-green
- category: dod
- severity: block
- description: T1 is done only when validation tests pass and happy-path stays green.
- check: check_tests_green
