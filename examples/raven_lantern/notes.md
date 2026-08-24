# raven_lantern — notes

**Read before editing the model. Update when you learn something.**

Why the numbers are what they are. Never restate a dimension here — name the symbol and explain the reasoning that is invisible in the source.

## The lit window is the scarce resource

Everything about this design is downstream of one measurement: the puck is **opaque for its whole lower half**. It is a flame-style LED tea light, so the light comes from a short narrow column standing on an opaque base rather than from a glowing top face.

`tealight_holder` assumed a flat emitting top face and was built on published figures nobody had checked. That was not merely an imprecise number, it was the wrong *shape* of fact. The correction is in `assemblies/halloween_lantern.py`, measured, and shared by the whole set.

The consequence that governs the design: the canvas is **short**. Roughly the flame's own height, and no design choice buys more of it. So:

- The band's floor is hard and asserted. Below it there is grey plastic and an opening there is a dark hole.
- The band's ceiling is **soft**, and the paper liner is why. The flame is close to a line source; the paper intercepts it and re-emits over its whole surface, turning it into a lit column. That is what evens out height variation, and it is confirmed in the hand from the earlier holder rather than theorised. The assertion on the ceiling therefore objects to *drifting* far above the flame rather than forbidding anything above it.
- Spending vertical space is the expensive decision here. That is what the `shared` layout is for: word and birds on the same band, on different arcs, so the height is spent once.

## The raven is traced, not drawn

The first raven was a hand-authored 17-point polygon and looked like one. The outline in the model now is a **trace of supplied reference artwork**: alpha composited onto white (the source PNG is RGBA, and converting straight to greyscale turns every transparent pixel black), largest connected component, holes filled, Moore-neighbour boundary walk, Douglas-Peucker at 4 px. 4637 boundary points reduce to 86 with no visible loss at print size.

Normalisation is the part worth preserving through any re-trace: height 1.0, centred in x. That is what keeps `raven_h` the only size knob.

### Feature size is what decides how much bird you get

The silhouette's own proportions, measured off the source bitmap rather than guessed:

| feature | fraction of bird height |
|---|---|
| toes | 0.005 – 0.012 |
| leg shafts | 0.033 |
| body | > 0.13 |

**These are openings, so each is a slot of that width in the wall.** Against a 0.4 mm nozzle that is decisive: the toes need a ~24 mm bird before they resolve, and the lit window cannot offer one. The legs need about 12 mm.

The failure mode is why this is asserted rather than left to judgement. A feature under one nozzle diameter does **not** disappear cleanly — the slicer fills it with gap-fill, so the bird acquires ragged blobby ankles. Cropping deliberately is strictly better than letting the machine crop it badly, so `feet` selects the crop and `check()` refuses a combination the nozzle cannot resolve.

### Thicken the toes; do not delete them

Cropping was the wrong instinct, and the correction is worth keeping because the reasoning generalises. Faced with detail below the nozzle, the first answer was to remove it — `feet="legs"` cropped the toes off. **A bird with legs and no feet reads as a mistake**, where a bird with slightly chunky feet reads as a bird. Removing a feature is not neutral just because it is the easy operation.

So the foot zone is dilated instead: the toes are fattened until they clear the nozzle, and nothing else is touched. Unthickened they would need an ~80 mm raven to resolve, so this is the only way `full` exists at all.

Deliberately **not** a uniform offset of the whole silhouette. That would fix the toes by bloating the beak, rounding off the tail notch, and shifting every proportion — paying for one region with all the others.

The honest cost is that the gaps between toes are the same order as the toes and close as they fatten, so the foot tends toward a paddle. It still reads as a foot, and at the current setting the toes stay distinct.

**Thicken to a target, not by an amount.** The first version took the dilation in millimetres, and the feet came out visibly too fat. The arithmetic says why: a fixed 0.3 mm per side turns a 0.07 mm toe into 0.67 mm, while the leg it hangs off is 0.46 mm. The foot ended up thicker than the leg.

The traced toe scales with `raven_h`, so a fixed millimetre figure over-fattens a small bird and under-fattens a large one. The parameter is now a **finished width** — in nozzle diameters, so it survives a change of machine — and the dilation is derived from it.

That in turn made the real constraint statable: **a toe must not finish thicker than the leg it hangs off.** It is now asserted. Nothing in the printability checks would ever have caught it; the only symptom was that the bird looked wrong, which is not something the harness can see. This is the third bug in this part whose sole symptom was appearance — see also the retaining bars landing on the counter edge, and the tail being squared off by a full-width crop. Where a proportion can be written down, write it down.

Rescaling after thickening matters: fattening grows the silhouette downward, so without it `raven_h` would quietly stop meaning the bird's height.

### The aspect assertion tests the artwork, not the design

It fired after thickening was added, and the assertion was wrong rather than the shape. Cropping and fattening are deliberate transforms that legitimately move the aspect ratio; what the check exists to catch is `_RAVEN_OUTLINE` being edited into something that is no longer a raven. So it now measures the **raw** outline — uncropped, unthickened. An assertion evaluated on a derived shape becomes a tripwire on every future design decision, which trains people to widen the bounds until it means nothing.

### The crop is a rectangle, not a horizontal line

Worth stating because the obvious implementation is wrong and looks *almost* right. The legs hang under the body at x ∈ [+0.05, +0.33], but the **tail sweeps down behind to y ≈ 0.13** — lower than the belly. So a full-width horizontal cut at the belly line takes the tip off the tail as well, and the bird comes out with a squared-off tail. It renders as a plausible bird and nothing complains.

Limiting the cut in x removes the legs and leaves the tail whole. The bounds come from a column-by-column scan of the source bitmap, not from estimating off the rendered outline.

### Height is cheap, so the bird got bigger

Stated preference: *too tall is not the issue that too short is.* That converts the lit window from a hard budget into a soft one and changes what is worth optimising. The bird went to 14 mm — enough that the leg shafts clear the nozzle and `feet="legs"` becomes available, which it was not at 8 mm.

The ceiling assertion was relaxed to match. It is now a backstop against absurdity rather than a design constraint, because a cramped motif is a design that failed while a lantern taller than strictly lit is just a lantern.

Cropping happens in normalised space **before** scaling, so `raven_h` always means the height of the bird you actually get. Cropping afterwards would make one `raven_h` mean three different sizes depending on `feet`, and a set of lanterns would quietly stop matching.

## One-way cutters, and why this differs from the heart holder

`tealight_holder` extrudes each heart cutter **both** ways, so one subtract pierces near and far wall at once. That is exact — not approximate — because a heart is left–right symmetric, so the silhouette punched through the far wall is the same heart.

**Neither a letter nor a raven is symmetric.** The same trick here would stamp `eromreveN` across the back and a mirrored bird beside it. So cutters are extruded a single direction and rotated into place individually. It costs more subtracts and it is the only correct option.

## Each glyph is cut on its own radial plane

The word spans a real fraction of the circumference. Cutting the whole word as one flat prism would make the cut increasingly oblique toward the ends — the outer letters smear, and the word only reads from exactly dead-on.

So every character gets its own plane, square to its own patch of wall, with positions computed as arc length converted to angle. Each letter is undistorted and the word curves. The cost is **kerning**: cutting per glyph throws away the font's pair kerning, which is what `letter_gap` exists to compensate for by hand. It is a spacing fudge, not a typographic one, and it will never be as good as the font's own.

Glyphs are aligned `Align.MIN` in Y so y=0 is the baseline. Letting each glyph centre itself would set `N` and `e` on different lines, because they are different heights — the lowercase would visibly float. The raven silhouette is normalised the same way, sitting on y=0 and centred in x, so both kinds of opening are positioned by their bottom edge and a band is as tall as it was asked to be rather than as tall as the outline happened to span.

## Three separate decisions make the lettering legible

They were made together and it is worth keeping them apart, because each one carries its own reasoning and they can be revisited independently.

**All caps.** Not a styling choice. Lowercase `e` is the worst glyph in this word to pierce — a small counter that any retaining bar has to cross, and crossing it removes the top of the bowl so the letter reads as an `o`. Capital `E` has no counter at all. Going uppercase takes three of the nine letters out of the problem entirely, leaving only `R` and `O` holding anything.

**A chunkier face.** The retaining bar has a hard minimum width set by the nozzle. It cannot get thinner, so the only way to make it a smaller *fraction* of the letter is to make the letter's strokes heavier. Weight buys legibility here in a way that font size alone does not — scaling the whole word up scales the counter up too, and the bar stays the same absolute width either way.

**Full-height bars rather than stubs.** The bar runs from below the baseline to above the cap height, through the counter, instead of stopping where it has done its job. This sounds like more material and is less: a bar anchored in solid wall at *both* ends can be far thinner than one cantilevered off a single end, and thin is the whole objective. It also reads better — a short stub is a blob interrupting a letter, where a full-height hairline reads as a seam and the eye stops noticing it.

Consequently `bridge_w` is floored against the **nozzle**, not the two-perimeter minimum wall, which is a deliberate exception to the usual rule. The bar is a leash, not structure: anchored at both ends over its whole height, carrying nothing but a chip of plastic. A single-extrusion rib is correct, and every tenth of a millimetre saved is legibility gained.

### `Wire.center()` is not the centroid

A trap worth writing down because it is silent and the symptom is purely cosmetic. Placing each retaining bar at `wire.center().X` put every bar hard against the **side** of the counter it was meant to cross. For the `O` counter the glyph's bounding box runs −0.82 to +0.82 and `wire.center().X` returns **+0.823** — the right-hand edge, not the middle.

Nothing catches this on its own terms. The bar still connects the island, the part is still one solid, every printability check still passes. It just looks wrong, and looking wrong is not something the harness can see.

Use `wire.bounding_box().center().X`. And there is now an assertion that each bar is fully *contained* within its counter, clear of both edges — the general form of the bug, so a different font or a different glyph cannot reintroduce it by another route.

## Stencilling is done by construction, not by font

There is **no stencil typeface installed on this machine** — no Stencil, no Allerta. So the counters are bridged in code: each inner wire of a glyph gets a bar subtracted from the glyph, running from inside the counter up and out through the top of the letter.

Two things make this the right call rather than a workaround:

- It is **font-agnostic.** Any installed face works, which matters because the font is still an open question and swapping it must not silently break.
- The failure it prevents is **completely silent.** A counter with no bridge is an island of plastic inside a hole. The model builds, the render shows a perfect letter, and the chip falls out of the print. So the check counts remaining islands rather than trusting the bridging to have worked.

The bar runs upward for a reason that is worth stating: whatever shape a counter has, a bar extended past the glyph's top edge is guaranteed to exit. A shorter or sideways bar can stop inside the ink and connect nothing.

`bridge_w` is floored against the nozzle. A bridge below minimum wall slices as gap-fill and snaps, which turns the counter back into a loose chip — the exact failure the bridging exists to prevent.

## Chamfer before the openings, not after

The opposite of what `tealight_holder` does, and for a reason specific to this part. That part chamfers last so the rim selection cannot catch a heart edge.

Here, every opening reaches the outer surface and splits the cylindrical face, which splits the rim circle into arcs along with it. Selecting a whole rim is only possible while the shell is still a plain tube, so the chamfer moves to the front. Cutting afterwards cannot disturb it.

## Assertions that carry real knowledge

Beyond the obvious ones:

- **Raven aspect ratio.** A silhouette built from a mangled outline is still a closed shape and still renders as *something*. A perched raven is markedly wider than it is tall; if an edit makes it as tall as it is wide it has become a different animal, and nothing else in the pipeline would report that.
- **Open-area fraction, bounded at both ends.** Too little removed and it does not light. Too much and a black object stops having a silhouette — it reads as a colander. Both are real failures, neither is caught by any wall-thickness check, and the upper bound in particular is the kind of thing that only gets noticed after printing. It is approximate — silhouette area over the band's outer surface, with a fill factor for the raven's box — which is fine for a bound.
- **Retrieval.** Retrieving the puck means reaching in, pinching the flame, and pulling. So the measurement that matters is how far the flame tip is recessed below the rim, plus whether the bore leaves room for fingers either side of it — not how deep the well is and not where the openings are. `tealight_holder` lost its retrieval to a taller band and nothing in the model complained; the first version of this assertion here measured the wrong thing too.

## Open threads

- **Bridge direction hurts the `e`.** Running the bar straight up out of an `e` removes the top of the bowl, and the letter drifts toward reading as an `o` or a `u`. It is the price of a construction that works on any font. A per-glyph bridge angle, or a genuine stencil face, would both fix it.
- **The word wraps a long way round.** At the current size it is visible from well off-axis, which means no single viewpoint sees all of it comfortably. Smaller text, or a shorter word, are the two dials.
- **Paper liner thickness is an upper bound, not a measurement** — "under 0.2 mm". That is the right form for it, since it is consumed out of the fit clearance and what matters is the worst case. Do not tighten that clearance to cure a rattle; the liner is what takes up the slack.
- **Nothing has been printed.** Every criterion about light, legibility and strength is still open.
