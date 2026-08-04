# _template — notes

**Read before editing the model. Update when you learn something.**

This file exists because the reasoning behind a dimension is invisible in the
source: a number that looks arbitrary is usually load-bearing, and a number
that looks load-bearing is sometimes arbitrary.

Do *not* restate dimension values here — they are in `model.py` and duplicated
numbers drift. Name the symbol and explain the why.

## Design intent

Which parameter drives which, and what silently breaks if one is changed alone.

## Hard-won knowledge

Anything that cost a failed print or an hour of confusion. State what was
believed, what turned out to be true, and the evidence. This is the highest
value section in the repo; write it while the surprise is fresh.

When a discovery is better expressed as an invariant than as prose, assert it
in `check()` and let this file explain the assertion.

## Open threads

Unmeasured values, untested clearances, deferred decisions — what the next
session should distrust.
