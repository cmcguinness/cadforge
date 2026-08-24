---
name: cad-spec
description: Draft or refine a part's spec.md through questioning, before any geometry exists. Use when starting a new part, or when a review or a failed print shows the spec was wrong rather than the model. Triggers on "new part", "spec out", "design a ...", "refine the spec".
---

# Refining a spec

The spec is the durable artifact; `model.py` is disposable. When a design goes wrong it is almost always because the spec was thin.

**What a spec actually is:** the objective function for a search. Its acceptance criteria are the only part the harness can act on and the only part that settles a review. Adding a criterion narrows the space of acceptable designs; adding prose does not.

**Start wide.** A rough first spec is correct, not lazy. A detailed spec written before anything has been seen narrows the search to whatever the author first imagined, and the alternatives never surface. Tighten as you learn what matters.

**Constrain the outcome, not the method.** This is the distinction to hold onto when helping someone tighten a spec:

- *"The opening must sit clear of the emitter"* — prunes designs that cannot work. This narrows the search. Good.
- *"Trace the profile through these ten points"* — does not narrow the search, it replaces it. The human has now done the design by hand, and over-prescribed specs measurably produce worse parts.

The test for any proposed line: **does it change what counts as success, or only how to get there?** If the latter, it belongs in `notes.md` as a suggestion, or nowhere.

## Do this

1. `./cad status` to see the landscape. If the part exists, read its `spec.md`, `notes.md` and `history.md` first — especially `history.md`, so you do not re-propose a ruled-out direction.
2. If it is new: `./cad new <name>`, which scaffolds at the `spec` stage.
3. **Interrogate before writing.** The spec is only as good as the questions. Ask about, in roughly this order:
   - What it holds, where it sits, who handles it and how often. Not "a holder".
   - What it must fit. For every measurement, establish `measured` or `nominal` — and say so in the spec. An unmeasured nominal is the single most common cause of a failed print, and labelling it is what keeps the risk visible.
   - What is already known to be true about the objects and materials involved. These facts about the *world* often turn out to drive the whole geometry: "this LED emits only from its top face and is opaque below" decides where an opening can go; "PLA has almost no elastic range" decides how a clip has to be proportioned. Get them into the spec, because they will not be rediscovered from the model.
   - How it will be printed, and whether that is actually free.
   - What "good" looks like, in terms someone could disagree with. Use AskUserQuestion for the forks that would change the geometry. One 30-second question beats a day of modelling the wrong thing.
4. Write the spec, keeping the template's three criteria sections. **Write the function criteria first** — "does it do its job" is the axis that gets skipped, and an axis nobody states stays unconstrained however precise the others get. A spec with seven construction criteria and none about function will certify a part that is built perfectly and does nothing; that is not hypothetical, it happened here.

   Each criterion must be settleable by a render, a check, or a print. "Looks nice" is not a criterion; "the opening is clear of the emitter" is. Anything that can become an assertion in `check()` should — that is one evaluation the human never has to make again.

   `cad build` refuses to be quiet about an empty function section, and `cad next` flags it as urgent.
5. `./cad stage <name> model` when the criteria are settled. Then `./cad next` — it will tell you and the user what follows.

## Revising a spec on an existing part

Editing the acceptance criteria **moves the target**. The harness treats that as a new generation: iteration history from before the edit no longer constrains the search, because those verdicts answered a different question.

That is the right move when several iterations have gone by without a `good` — the search is not failing to find the target, the target is wrong. Say so plainly rather than proposing another parameter tweak. `cad next` raises this automatically after five laps.

## Do not

- Do not start modelling to "explore". Geometry written before the spec becomes the spec by default.
- Do not write dimension values into the spec. Constraints belong there; the numbers that satisfy them belong in `model.py`.
