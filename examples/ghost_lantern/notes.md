# ghost_lantern — notes

**Read before editing the model. Update when you learn something.**

Why the numbers are what they are — the reasoning that is invisible in the source. Never restate a dimension here; name the symbol and explain the why.

## This part is inverted, and the other two are not

The set's other motifs are **holes**: a raven, a witch's head in profile. This one is the opposite — the ghost is the **material** and the window around it is the opening.

That is not a stylistic choice, and the rule behind it is the most transferable thing in this part:

> **A motif that reads from its outer contour can be the hole. A motif whose recognition lives in its interior cannot.**

A raven reads from head, beak, back and tail — all boundary. A witch in profile puts her nose, chin and brow on the outline, which is exactly why a *profile* works where a front-facing face does not. **A ghost has neither.** Take its face away and it is a blob; that was tried and it failed review.

Under the usual polarity the eyes and mouth would have to be chips of plastic floating inside a hole — the same failure that destroyed `raven_lantern`'s lettering. Inverting makes them **holes in material**, which costs nothing at all. It also reads better: a dark ghost with *glowing* eyes rather than a glowing ghost with dark sockets.

The construction was abandoned once, on a witch flying across a moon. That failure was about *her*, not about the construction: her pose needed thin interior gaps — arm from body, hand from broom — measuring 0.4–0.8 mm. A ghost needs one big mass and three large oval holes. Judge polarity B on whether the subject has **large** interior features and something that **reaches down**.

## The anchor that matters is the one at the bottom

With the subject as retained material it has to be held on, and it is easy to assume any contact will do. It will not.

**Support propagates upward.** A ghost touching the window only at its sides or top begins in mid-air and is an island however well "attached" it looks in plan. What holds this one is its robe reaching the **bottom** edge of the window and merging into the wall below.

The generated artwork had the robe stopping short inside the window. Extending it to the bottom edge by hand took the part from **29 floating islands to zero** — nothing else changed. That is the whole difference between needing supports and not.

## Four, not five

Judged at true scale, which is the only way to judge it — the earlier motif in this set was approved at 5× magnification and failed at 1×.

The windows here are nearly square, 18.7 mm wide against 19 mm tall, where the other motifs are tall and narrow. At five the solid between them falls to 41% of the motif width and the lantern reads as a band of light with dark bits in it. At four it is 77% and reads as a dark object with windows in it, which is what a lantern should be.

`min_rib_frac` is therefore a **fraction of motif width, not millimetres** — a fixed millimetre floor means different things on a 17 mm motif and a 40 mm one. Two thirds is a rule of thumb bracketed by those two judgements; see the parameter's own docstring for why the round number beats the precise midpoint, and why `raven_lantern` passing at 0.25 is not a contradiction.

## The ceilings are bridges

Each window's top is a flat horizontal span, because the artwork is cropped square at the top of the motif band. Those are ~5–6 mm and anchored at both ends by the ribs, so they bridge — but they are wider than anything the raven bridged, and they are the first thing to look at on a plate.

The automatic overhang check flags them at 90°, which is correct and not a problem: a span anchored at both ends is a bridge, and only a ceiling that *begins* unsupported is an island. The two are different failures and the `islands` check is the one that distinguishes them.

## Open threads

- **Whether the slicer asked for supports** was never recorded. Zero islands predicted not, and the print came out clean, but the prediction is untested as such.
- **Whether the flat window ceilings bridged cleanly** — same.
- The artwork is a hand-edited version of a generated image and lives at `inspiration/ghost.png`. `trace_ghost.py` re-derives the openings from it, so the outline is reproducible rather than a magic list of coordinates. The raven's source was lost to a per-session cache before that lesson was learned.
