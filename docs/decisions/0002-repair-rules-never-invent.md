# 0002: The repair loop never invents, never guesses, and flags every clamp

Date: 2026-11-04 (recorded 2026-11-08 from DEEP-SPEC.md, now in
PROPOSAL.md). Status: accepted. Decided by: Jesun Ahmad Ushno.

## Context

A repair loop can raise its repair rate by filling missing fields,
mapping bad enum values to a near valid one, or clamping out-of-range
values. Each of those produces a valid shape that may state something
the source never said.

## Decision

Only three named rules exist: drop_additional_field (safe),
coerce_numeric_string (safe, exact type only) and clamp_to_range
(value-changing, always flagged on the log and on the record status).
Missing fields and invalid enum values have no rule and stay rejected.
Every attempt is logged; a healed record never passes without its log.
A clamped heal counts as a silent failure, a definition fixed before
the Deep run.

## Consequences

The measured repair rate is low (0.375 on the 8 designed rejections)
and the silent failure rate is high (0.667), by design: the numbers
show the cost of clamping instead of hiding it. Changing this set
changes the system under study and needs its own labelled set and a
before-and-after measurement (the standing rules in PROPOSAL.md).
