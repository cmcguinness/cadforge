---
stage: done
---

# owl

A creepy owl that stares at you, cut as a flat plate and slotted into a printed branch. A tea light sits on a shelf behind its head, level with the eyes, inside a square sleeve that keeps its light off the sides.

## What it is for

A Halloween ornament for a shelf or a mantel, looked at from the front in a dim room. Three pieces, printed separately and assembled dry: the owl plate, a branch it perches on, and a sleeve the tea light lies inside. It takes the same battery tea light as every other lit part here.

It is not a member of the `halloween_lantern` project. It reads that project's measured `PUCK` and nothing else.

## Constraints

- **The tea light is `measured`** (`projects/halloween_lantern/shared.py`): 35.0 mm across, 15.0 mm of opaque base, LED to 25.0, flame tip at 30.0.
- **The puck lies on its SIDE**, on the shelf, aimed forward at the back of the plate. That was improvised on the first print with rolls of tape and is now designed in. It is the decision `shared.py` says every part taller than its light source must make deliberately, and it changes what the sleeve is for: walls beside a flame block sideways light and pass forward light, where walls over a flame just take light away.
- **The sleeve's bore is `measured`** — settled by `tealight_sleeve`'s three-bore fit sweep, not re-derived here. Its **length is not** that part's length: it runs the whole height of the puck rather than stopping at the opaque base, which is the opposite bound and is correct for a puck on its side. See notes.md.
- **The artwork is supplied and settled** — `inspiration/owl.png`, owl in black, branch in red. It survives a 0.4 mm nozzle at **99.6% of its area** at every size from 100 mm up, in one connected piece once four single-pixel antialias flecks are dropped. It needs no simplification, only cleaning.
- **The owl has three apertures**: two eyes and the beak. All three must be cut. A solid beak is invisible — black plastic against a black body — so the beak reads only as a hole.
- **The eyes are centred at 67.1% of the owl's height**, and the beak sits directly below them. Both measured from the artwork, not chosen.
- **The plate prints flat on the bed**, which is why the feathered outline is affordable at all. Every layer-support rule that governs the lantern motifs is void here: the artwork's plane is horizontal during printing, so downward spikes, valleys and multiple peaks cannot fail. Do not import those constraints.
- **Black filament.** `castle` established that light PLA transmits and glows at these thicknesses. Black does not, which is what makes the apertures the only light on the object.
- **Fixed by taste:** it must read as a creepy owl unlit as well as lit. The stare is the design.

## Acceptance criteria

### Does it do its job?

- [ ] **The eyes are the brightest thing on it**, and the beak is clearly subordinate — visible, not competing.
- [ ] **The shelf is positioned so the puck's LED band straddles the eyes and its opaque base shadows the beak.** This is a derived quantity, not a chosen one: `shelf = eye_centre − (opaque_h + emit_top)/2`. At 140 mm it lands at 74.0 mm and covers 92% of the eye height. **Asserted**, because the optimum is sharp — 4 mm either way costs a third of the eye coverage.
- [ ] **It reads as a creepy owl unlit**, in daylight, to someone not told.
- [ ] **The stare reads as menacing rather than startled.** Eye spacing is what decides this and it comes from the artwork; if it is wrong, it is a parameter and worth a sweep.
- [ ] **A tea light can be placed and removed by hand** without lifting the owl off the branch or reaching past anything sharp.
- [ ] **The puck cannot fall off the shelf** if the ornament is knocked.
- [ ] **It does not tip backwards.** The puck is rearward mass at eye height. Asserted against where that mass *acts* — the branch must reach behind the puck's centre of mass, plus a margin for a nudge. Reaching behind its rear *face* was the first version and demanded a branch heavier than the owl it holds.
- [x] **The shelf is not visible from the front.** The body is far wider than the puck at that height, so this is a matter of not making the shelf wider than it needs to be. **Now also about the sleeve, which is the tall thing back there**: lying down it is as tall as it is wide, so it reaches well above the eyes and far above the shelf rim. Asserted against the traced silhouette at every height the sleeve occupies, rather than at one place.
- [x] **The light does not spill sideways off the shelf.** Settled by the print: a sleeve running the full length of the puck shrouds it. Rearward spill is accepted — it is only visible from behind the ornament.
- [x] **The sleeve does not push the flame off the eyes.** It raises the flame axis, because the puck rests on a wall and sits centred in a bore instead of resting on its own cylinder. Asserted to stay inside the eye band.
- [ ] **The joint between owl and branch does not read as a joint** from the front — the branch's top covers the tab and a little of the body.

### Is it built correctly?

- [x] **Three pieces, each one connected solid and a watertight mesh**, declared through `pieces()`.
- [ ] **The four single-pixel flecks are gone** and the traced outline is a single closed region with exactly three apertures.
- [x] **The slot is a clearance fit, not an interference fit.** A tight slot in PLA either will not assemble or splits the branch. The clearance was originally chosen as a *glue gap*; in the event no glue was needed and the same clearance seats the plate under its own weight. Do not tighten it to add grip — the seat already works, and a snugger one only risks the split the clearance exists to prevent.
- [ ] **The joint sits where the artwork puts it.** The bar under the owl is 4 mm *below* the owl's drawn base — the artwork has the owl floating with the raised forks flanking it — so a few millimetres of tab are visible between them, exactly as drawn. The owl grows a tab downward to reach the slot; the branch is not lifted to meet the owl, which would drag the forks up its chest.
- [ ] **The plate is thick enough to be opaque** and stiff enough not to bow, and thin enough that an aperture does not become a tunnel that vignettes the eye off-axis.
- [x] Fits the configured bed; `PRINT_ROTATION` stated for every piece, and the plate is exported lying flat, the sleeve on end.
- [x] **The sleeve fits inside the shelf's rim**, in width and in depth. Its width is the tightest clearance on the part.
- [ ] **The artwork is in the repo** so the trace can be re-run.

### Only a print can settle these

- [ ] **Whether the eyes read as eyes when lit**, through printed paper, rather than as two bright holes.
- [ ] **Whether the beak is subordinate or distracting.** Geometry says the opaque base shadows it completely, but that is line-of-sight — bounce and the diffuser will lift it off black by some unknown amount. Note that with the puck on its side the opaque base is *beside* the flame and shadows nothing, so the geometric argument no longer holds; it has been judged acceptable by eye twice.
- [ ] **Whether the branch holds it steady** in use, not just in arithmetic.
- [x] **Whether the joint holds without glue.** It does — the plate rests in the slot under its own weight and stays put, so the ornament is never glued. Lifted by the owl rather than by the branch, which is what people will do, the two pieces separate; that is a handling habit rather than a failure, and it buys flat storage in exchange.
- [ ] **Whether it reads as a creepy owl across a lit room**, to someone not told.

## Open questions

- **How big?** 140 mm is the working assumption for the owl. It makes the tab 42.6 × 8.0 mm and puts the shelf at 74.0 mm. Nothing is committed to it; every derived number follows the height.
- **How deep is the branch, and where is the slot in it?** Depth is free — nobody looks at it — but material is not. Extruding the branch straight back wastes volume; splaying the forked ends in depth, one tip forward and one back at each end, gives the same footprint as a cross rather than a slab. The slot should sit **forward of the branch's centre** so more of it lies behind the owl.
- **Paper behind the eyes only, or across the whole face?** Paper redistributes light rather than adding it, so paper across the beak would pull light into the feature we are trying to subdue. Start with eyes only.
- **Does the beak want its own smaller aperture?** It is currently the artwork's beak at full size. If it proves distracting, shrinking it is cheaper than moving the shelf.
