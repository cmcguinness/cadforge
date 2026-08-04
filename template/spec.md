---
stage: spec
---

# _template

> **The spec is the durable artifact. `model.py` is disposable.**
> When a design goes wrong it is almost always because the spec was thin, not
> because the geometry was hard. Spend the time here.

## What it is for

One or two sentences a stranger could act on. Not "a holder" — *what* is held,
*where* it sits, *who* handles it and how often.

## Constraints

The things that are true regardless of how it is designed. Each one should be
falsifiable.

- **Fixed by the world:** measurements of objects it must fit, mate with, or
  sit inside. Mark each as `measured` or `nominal` — a nominal value that is
  never measured is the single most common source of a failed print, and
  labelling it is what makes the risk visible later.
- **Fixed by the process:** printable without supports; fits the A1 mini bed;
  PLA. Deviations get stated and justified.
- **Fixed by taste:** how it should read. Vaguer, but real, and worth writing
  down so a later refinement does not optimise it away.

## Acceptance criteria

Checkboxes, because `cad build` prints them next to the renders and they are
what the visual review is read *against*. Without them, review degrades into
"looks fine to me" and a part gets built with the right shape and the wrong
purpose.

Write them so a render or a check can settle them. "Looks nice" cannot be
settled; "the opening is clear of the emitter" can.

- [ ] …
- [ ] …

### Only a print can settle these

Some criteria cannot be judged from geometry — stiffness, feel, how light
behaves, whether it is annoying to use. List them separately so nobody claims
them from a render.

- [ ] …

## Open questions

What is genuinely undecided, and what would settle it. Delete a question only
when it is answered, and move the answer into notes.md.
