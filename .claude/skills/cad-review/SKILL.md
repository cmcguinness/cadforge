---
name: cad-review
description: Build a part, look at the renders against its acceptance criteria, and propose refinements without oscillating. Use after any model change, and whenever asked whether a part "looks right". Triggers on "review", "check the model", "does this look right", "refine".
---

# Reviewing and refining a model

## Do this

1. **Read `history.md` first.** Before forming any opinion about what to change,
   know what has already been tried and what was rejected. This is not optional
   — it is the whole mechanism that keeps refinement from circling.
2. `./cad build <name>`. It builds, runs the part's assertions, runs the
   printability checks, writes the renders, and prints the acceptance criteria.
3. **Actually open the part's `build/review/sheet.png`** with the Read tool. Not the
   individual views — the sheet, which carries all four orthographic views plus
   the cutaway. If the part has internal geometry, the section is the frame that
   matters; a shaded exterior cannot show a pocket that is the wrong depth.
4. Go through the acceptance criteria **one at a time**, and for each say which
   frame settles it and what you actually saw. A criterion you cannot settle
   from the renders is not settled — say so rather than assuming.
5. Attend to the check output. `FAIL` blocks export. `WARN` is a decision, not
   noise: an overhang warning on a part with no `PRINT_ROTATION` may just mean
   the pose is wrong, and that is worth fixing rather than ignoring.

## Proposing a change

- Change **one thing at a time** where you can, so the history records a diff
  that means something.
- Say what you expect to happen before rebuilding. If the render does not match
  the expectation, the model is not the only thing that was wrong.
- Use `./cad sweep <name> <param>=<v1>,<v2>,<v3>` when the question is "how much
  is enough?". It renders the variants side by side, which is far cheaper than
  three prints or three guesses.
- If the build warns that the parameters were tried before, **stop**. Read the
  cited iteration. Either articulate what is different this time, or pick a
  different direction.

## After judging

Record the outcome: `./cad accept <name> good|bad|mixed "<why>"`. The `why` is
what a future session reads; "didn't work" is useless, "too flimsy at the rib
between the openings" is a constraint.

When a criterion the renders can settle is settled, advance:
`./cad stage <name> print`.

## When to escalate to the spec

If the geometry satisfies every criterion and the part is still wrong, the spec
was wrong. Say so plainly and go back to `cad-spec` rather than tuning numbers.
