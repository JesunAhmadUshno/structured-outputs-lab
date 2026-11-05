# LinkedIn post draft: P14 structured-outputs-lab v1.0

Status: DRAFT NOT POSTED
Date drafted: 2026-11-04
Author: Jesun Ahmad Ushno
Rule for this platform: the link goes in the first comment, not in the
post body. The first comment line is at the end of this file.

## Post body

An LLM application does not need output it can read. It needs
output it can trust: present, typed, in range, with no surprises.
So I built the defence in the open, and measured where repair
helps and where it quietly harms.

structured-outputs-lab v1.0 is done: Learn, Build, and a
compressed Deep, Python standard library only. No model, no API.

Learn: a strict schema validator and a validate-then-dispatch
gate for function calling. On 10 designed cases, 10 of 10 matched:
4 valid calls dispatched, 6 invalid calls rejected before dispatch,
each at its named error path, from $.unit and $.date to
$.keywords[1] and $. 16 tests.

Build: a document extraction pipeline over 16 synthetic documents
in 3 types, with every output validated. 16 of 16 matched: 8
accepted, 8 rejected, extraction 40 of 40 fields, catch rate 8 of
8, and 0 false accepts. 18 tests, 34 in total.

Deep (compressed): a self-healing parse loop over the 8 Build
rejections, named repair rules only, every attempt logged. 3
healed and 5 still rejected: repair rate 0.375. The only clean
heal was dropping an additional field. The other 2 heals are
flagged clamps, and both count as silent failures: silent failure
rate 0.667. A clamped total is a valid shape carrying a false
fact, and the loop flags it instead of hiding it. Missing fields
are never invented and enum values are never guessed, which is
why 5 records honestly stay rejected. 0 of 8 accepted records were
altered. 55 tests in total.

The honest limits, in the post and not in a footnote: synthetic
designed sets only, one defect per malformed document, no real
model output and no real documents, deterministic regex
extractors, and a validator that is a strict subset of JSON
Schema. The rates are properties of this set and these rules, not
of self-healing in general. The rest of the Deep scope is named
as the v1.1 backlog in the repo, not claimed as done.

If you ship structured outputs: do you let your system repair a
rejected record, and if so, which repairs do you refuse on
principle?

## First comment (post this as the first comment, per the standing rule)

Repo, releases v0.1, v0.5, and v1.0, and the full tutorial: https://github.com/JesunAhmadUshno/structured-outputs-lab
