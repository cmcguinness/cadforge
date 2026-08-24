# pumpkin_lantern — notes

**Read before editing the model. Update when you learn something.**

This file exists because the reasoning behind a dimension is invisible in the source: a number that looks arbitrary is usually load-bearing, and a number that looks load-bearing is sometimes arbitrary.

Do *not* restate dimension values here — they are in `model.py` and duplicated numbers drift. Name the symbol and explain the why.

## Design intent

Which parameter drives which, and what silently breaks if one is changed alone.

## Hard-won knowledge

Anything that cost a failed print or an hour of confusion. State what was believed, what turned out to be true, and the evidence. This is the highest value section in the repo; write it while the surprise is fresh.

When a discovery is better expressed as an invariant than as prose, assert it in `check()` and let this file explain the assertion.

## Open threads

Unmeasured values, untested clearances, deferred decisions — what the next session should distrust.

## Wall thickness was the open bet, and it paid

1.1 mm was chosen for **glow**, not for strength, before anything had been printed, and handling the aborted print suggested it might be structurally marginal.

It was deliberately not changed, and the reasoning is the part worth keeping: the aborted piece was an open, part-height shell. A finished lantern is a *closed* one — the dome closes over at the top, the ring caps the bottom, and both stiffen it out of all proportion to their own thickness. **Judging the final part's strength from a partial print is judging a different object.** The finished print is not marginal, and the glow is right.

So `wall` stays at 1.1. If a later requirement ever pushes it up, that is not a local edit — the shoulder's maximum slope is `max_dr_dz = 0.45 × wall / layer_h`, so more wall buys a rounder top as well as strength, and the rib amplitude (1.3 mm) is currently *larger* than the wall, which more wall would make ordinary again. It costs glow, which is the whole reason the number is what it is.

## The grin: two rows of holes make a third shape

The mouth is the only feature that took three attempts, and none of them failed geometrically. The version that printed first was **two rows of four triangles, apexes meeting**, separated by a 1.4 mm waist — exactly as modelled, cleanly printed, and it read as **three diamonds in a slot.** Each pair of opposed triangles fused into a lozenge in the eye, and the waist became a horizontal band holding them.

The fix is `n_teeth` up-triangles on the bottom against `n_teeth - 1` down- triangles on top, **interleaved on a shared period**, with `2 × tooth_row_h` deliberately *exceeding* `mouth_h` so the rows overlap rather than meeting. The material between them is then one continuous zigzag: nothing pairs, and there is no horizontal band for the eye to find.

**The general lesson: a hole is not the shape you see.** Regularly repeated openings generate a figure in the material between them, and *that* figure is what gets recognised. No assertion can catch it — the geometry was correct every time — so it belongs with the figure/ground reasoning in `ARTWORK.md`, not with the printability checks.

The mouth widened 30 → 36 mm at the same time, so the triangles come out roughly equilateral (7.6 × 7.2 mm) rather than tall and narrow. Two changes at once, which is normally a mistake; here the second was forced by the first, since interleaving on the old width would have made the teeth needles.
