# Reviewer Checklist

The reviewer is a SEPARATE ROLE: read-only on the diff, write-only on this report.
It runs AFTER the verification gate passes. The gate proves deterministic facts;
the reviewer judges quality. Never ask the reviewer to redo what the gate proves.

Five dimensions, each scored 0-2 (total /10). Below 7 = soft fail; below 5 = hard fail.

| Dimension | Question |
|-----------|----------|
| problem_fit | Did the change solve the task as stated, not a nearby task? |
| scope_discipline | Were edits confined to the contract, or was it grown deliberately? |
| assumptions | Are all hidden assumptions written down somewhere reviewable? |
| verification_quality | Does the acceptance command prove the goal, or a weaker version? |
| handoff_readiness | Could the next session pick up cleanly from current state? |

Bias mitigations (LLM-judge): evaluate both orderings and count only consistent
wins; reward conciseness; rotate judge model families; strip author names.
