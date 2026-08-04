---
name: cad-spec
description: Draft or refine a part's spec.md through questioning, before any geometry exists. Use when starting a new part, or when a review or a failed print shows the spec was wrong rather than the model. Triggers on "new part", "spec out", "design a ...", "refine the spec".
---

# Refining a spec

The spec is the durable artifact; `model.py` is disposable. When a design goes
wrong it is almost always because the spec was thin.

## Do this

1. `./cad status` to see the landscape. If the part exists, read its `spec.md`,
   `notes.md` and `history.md` first — especially `history.md`, so you do not
   re-propose a ruled-out direction.
2. If it is new: `./cad new <name>`, which scaffolds at the `spec` stage.
3. **Interrogate before writing.** The spec is only as good as the questions.
   Ask about, in roughly this order:
   - What it holds, where it sits, who handles it and how often. Not "a holder".
   - What it must fit. For every measurement, establish `measured` or `nominal`
     — and say so in the spec. An unmeasured nominal is the single most common
     cause of a failed print, and labelling it is what keeps the risk visible.
   - What is already known to be true about the objects and materials involved.
     These facts about the *world* often turn out to drive the whole geometry:
     "this LED emits only from its top face and is opaque below" decides where
     an opening can go; "PLA has almost no elastic range" decides how a clip
     has to be proportioned. Get them into the spec, because they will not be
     rediscovered from the model.
   - How it will be printed, and whether that is actually free.
   - What "good" looks like, in terms someone could disagree with.
   Use AskUserQuestion for the forks that would change the geometry. One
   30-second question beats a day of modelling the wrong thing.
4. Write the spec, keeping the template's sections. The acceptance criteria are
   the point: **each must be settleable by a render, a check, or a print**, and
   the print-only ones go in their own section so nobody claims them from an
   image. "Looks nice" is not a criterion; "the opening is clear of the emitter"
   is.
5. `./cad stage <name> model` when the criteria are settled.

## Do not

- Do not start modelling to "explore". Geometry written before the spec becomes
  the spec by default.
- Do not write dimension values into the spec. Constraints belong there; the
  numbers that satisfy them belong in `model.py`.
