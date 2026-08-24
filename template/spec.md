---
stage: spec
---

# _template

> **Start vague. Tighten deliberately.**
>
> Designing a part here is a search, and this file is the objective function. A thin spec searches a wide space — which is what you want at the start, because you do not yet know which design you prefer. A meticulous spec written before you have seen anything narrows the search to whatever you happened to imagine first, and you never find out what else was available.
>
> So a rough first pass is the correct opening move, not a confession. Tighten as you learn what you actually care about.

## What it is for

One or two sentences a stranger could act on. Not "a holder" — *what* is held, *where* it sits, *who* handles it and how often.

## Constraints

The things that are true regardless of how it is designed. Each one should be falsifiable.

- **Fixed by the world:** measurements of objects it must fit, mate with, or sit inside. Mark each as `measured` or `nominal` — a nominal value that is never measured is the single most common source of a failed print, and labelling it is what makes the risk visible later.
- **Fixed by the process:** printable without supports; fits the configured bed (`./cad setup`, or `printer.toml`); the configured material. Deviations get stated and justified.
- **Fixed by taste:** how it should read. Vaguer, but real, and worth writing down so a later refinement does not optimise it away.

## Acceptance criteria

**This section is the whole spec, mechanically speaking.** Prose sets context; only a checklist can settle a review. `cad build` prints these under the renders, and a reviewer answers them instead of forming an opinion from scratch — which is the difference between an evaluation that takes a minute and one that takes ten.

Two rules, both learned the hard way:

1. **Constrain the outcome, not the method.** "The opening must clear the emitter" prunes designs that cannot work. "Trace this profile through these ten points" does not narrow the search — it replaces it, and you have done the design by hand. If removing a line would not change what counts as success, it does not belong here.
2. **State every axis you care about.** An axis you leave unstated stays unconstrained no matter how precise the others get. This is not theoretical: this repo's first worked example had seven criteria, all of them about construction, and produced a part that was built perfectly and could not hold anything.

Editing these lines opens a new **generation** — the target has moved, so earlier verdicts no longer apply and the iteration history starts fresh. Editing the prose above does not.

### Does it do its job?

The axis that matters, and the one that gets skipped. Write these first. Settleable from a render where possible; say what to look at.

- [ ] …

### Is it built correctly?

Geometric and structural invariants. Cheap to write, easy to over-weight — most of these should end up asserted in `check()`, where they cost you nothing to evaluate ever again.

- [ ] …

### Only a print can settle these

Stiffness, feel, how light behaves, whether it is annoying to use. Kept separate so nobody claims them from an image, and so `cad next` knows the part is not finished until it has met the physical world.

- [ ] …

## Open questions

What is genuinely undecided, and what would settle it. Delete a question only when it is answered, and move the answer into notes.md.
