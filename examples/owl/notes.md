# owl — notes

**Read before editing the model. Update when you learn something.**

Numbers live in `model.py`. This file says why.

## The one number the design turns on

`shelf_z` is derived: `eye_centre − (opaque_h + emit_top)/2`. Centring the puck's emitting band on the eyes lights them and, because the beak sits directly below them, leaves the beak behind the puck's opaque base. One number does both jobs, and the 15 mm of opaque plastic that has been an obstacle in every other lit part here is the thing that makes this one work.

The optimum is sharp — 4 mm either way drops eye coverage from 92% to about 60% — which is exactly why it must not be a typed constant. `check()` asserts the *coverage*, not the number, so the assertion still means something after a rescale or a re-trace.

**Centre it on the eyes' vertical SPAN, not their centroid.** The eyes are angled crescents with more area at their outer ends, so their centroid sits 1.2 mm below the middle of their height. Centroid is the natural thing to reach for and it costs 11 points of coverage. The quantity being optimised is how much of the eyes' *height* the LED covers, so height is what the derivation must use. The assertion caught this on the first build.

## Five bugs, and every one of them looked perfect from the front

This part is a facade, and facades hide their mistakes in the depth direction. The castle learned that about crenellations cut full-depth. The owl found five more in a single session, and the front elevation — the view anyone actually reads — was flawless through all of them:

**1. `.locate()` threw away the rotation.** `pieces()` rotated the plate flat, then called `.locate()` to drop it to z = 0. `locate` sets an *absolute* location and discards whatever transform the shape already carried, so the rotation vanished. The plate went to the plate standing 140 mm tall with **389 islands**. It built, passed validity, and rendered as a perfectly good owl. Use `.move()` for anything relative.

**2. `Plane.XZ` extrudes along −Y.** A bare `extrude()` on a sketch in that plane builds *backwards*, so the body occupied y ∈ [−3.2, 0] and the shelf hung off the owl's **face**. Every check passed: one valid solid, on the bed, no islands. The extrusion direction is explicit everywhere now.

**3. `BRANCH_TOP` was the wrong maximum.** The branch's highest point is a raised fork tip at the far end; its top *under the owl* is 14 mm lower — and negative, because the artwork draws the owl floating with the forks flanking it. The slot was therefore cut in thin air and the pieces never engaged at all. The trace now emits `BRANCH_TOP_AT_SLOT` alongside the global maximum, and the owl grows a tab downward to reach it. **Raising the branch instead would have dragged the forks 12 mm up the owl's chest and changed the composition** — adapt the part to the artwork's intent, not the artwork to the arithmetic.

**4. The shelf touched the plate instead of entering it.** It started at `y = plate_t`, the plate's back face: coincident faces, no shared volume, two solids that still render as one owl. Same failure the castle met on pillars, decks, cone apexes and tower bands. **Interpenetrate, never touch.**

The generic checks caught none of these. What caught them was assertions aimed at *specific surfaces that should exist* — and writing those is the only defence a facade part has.

## `add()` places a shape on the CURRENT WORKPLANE

The fifth bug, and the worst, because it produced a feature that looked deliberate.

`_plate()` built the body with `BuildSketch(Plane.XZ)`, then called `add(_shelf(...))`. **`add()` does not place an absolutely-positioned solid where it is; it places it relative to the builder's current workplane** — still `Plane.XZ`. The shelf was re-mapped: its vertical extent became horizontal, and the owl grew a **47 mm slab out of its feet**, 50 mm wide, looking for all the world like an intentional base.

Standalone, `_shelf()` returns geometry at z 38.8–79.4. Added, it landed at z 0. Nothing in the checks noticed — one valid watertight solid, on the bed, no islands — and the front elevation showed nothing, because the whole thing lived in the depth direction.

Charles spotted it by eye and called it "a foot sticking out the back". Finding it took a grid probe of the plate's interior, because every summary statistic said the part was fine.

**Fuse absolutely-positioned solids with `+` outside the builder.** `add()` is for things you want placed *on* the workplane you are working on. Anything already located in world coordinates — a shelf at a derived height, a pair of feet at a derived depth — must be unioned, never added.

## Two rotations, and only one of them lays the plate flat

`pieces()` rotates the plate to print face-down. It must be `rotate(Axis.X, 90)`, which maps +Y to +Z and sends the shelf *upward*. The other way lays it shelf-down: the plate then rests on the shelf's rim, and the entire owl face — **9229 mm², the whole silhouette** — becomes a flat overhang 47 mm above the bed.

The overhang check caught this one immediately, which is what it is for. Worth noting the contrast with the bug above: a wrong *rotation* shows up in the statistics, a wrong *placement* does not.

## The branch is a branch, not a plinth

The first version counterweighted the puck by being 46 mm deep, which made a slab weighing 128 g to hold up a 67 g owl — more plastic in the stand than in the object. Stability does not want depth everywhere; it wants the support to reach past the rearmost mass at two points, which is all a tripod needs.

So the branch is now a normal 24 mm section and two narrow feet reach back under the fork ends, where it is already thick. Same stability, 45 g instead of 128. The assertion moved with it: it now tests where the *feet* reach, and separately that they are actually joined to the branch rather than floating behind it.

Gussets went to 1.6 mm and about half the drop at the same time. A tea light weighs roughly 17 g; the gussets exist to stop the shelf/plate joint being a hinge, not to carry a load.

## A global extremum is not a local one — three times, now

This is the mistake this part kept making, in three different costumes, and it is worth naming as a pattern rather than as three bugs.

- **`BRANCH_TOP`** was the branch's highest point *anywhere* — a raised fork tip at the far end. What the slot needed was its height *under the owl*, 14 mm lower and negative. The slot got cut in thin air.
- **`branch_bottom`** was the branch's lowest point *anywhere*. What the feet needed was the underside *at their own x*. The traced outline wanders about 0.2 mm along its length, so the feet sat 0.13 mm proud and the ornament rested on three scattered points that could rock. Charles spotted it by eye.
- **`EYE_CENTRE`** was the eyes' centroid, weighted by area. What the shelf needed was the midpoint of their vertical *span*. Cost 11 points of coverage.

Every one is the same shape: **a summary statistic of a whole outline, used where a local property was wanted.** A traced polygon is not a rectangle — its extremes occur at particular places, and those places are almost never where the mating feature is.

The defence is the same each time: derive the quantity *at the location that uses it*, and assert it there. `check()` now measures the underside at each foot's own x rather than trusting a global minimum.

## Where the feet go is a property of the outline, not a number

The feet were first placed at x = ±38 by eye, which put their outer edges at ±42.5 — **outside the branch's ground-contact patch**, which ends at ±40.6. They stuck out past the branch's own footprint.

The branch does not touch the table along its whole length: it lifts at the forks. So "how wide is the branch" is the wrong question, and its bounding box is the wrong answer. What the feet need is the width of the part that actually *touches*, and that has to be measured by walking the traced outline.

`_contact_half()` does that, and `foot_x` is derived from it: `contact_half − foot_margin − foot_w/2`. The only thing chosen is the margin. `check()` asserts a foot's outer edge stays inside the patch.

This is the same lesson as the section above, arriving from the other direction: the bounding box of a traced organic outline describes almost nothing useful about where it meets a mating feature.

## The branch base is trimmed to a real plane

The traced underside wanders by about 0.2 mm — noise from the artwork, not design — so the branch's "bottom" was a wobbly curve and an ornament resting on it touched at whichever few points happened to be lowest.

`base_trim` shaves the underside to a plane. That gives the branch a genuine footprint, and gives the feet something to be flush *with*: without a plane, "flush" has no meaning to assert against. The fork ends still lift off it, which is correct — a branch should not touch the table along its whole length.

## What an assembly assertion can and cannot say

A solid count is nearly useless on a two-piece assembly here, and the reason is worth remembering.

The joint is a **clearance fit**, so the pieces legitimately do not fuse — two solids is correct. But the tab also **bottoms out on the slot floor**, because that contact is what locates the owl vertically, and coincident faces make the kernel fuse them into one. Both counts are legitimate, so the count proves nothing.

What does prove something is a **probe**: there must be branch material directly beneath the tab, and clear air where the tab has to go. Unlike a count, that says *where the pieces are relative to each other* — which is the thing that was actually wrong when the branch sat 46 mm in front of the owl.

## Why the feathered outline is free

The plate prints flat, so the artwork's plane is horizontal during printing. Every layer-support rule that governs the lantern motifs — no downward spikes, no stalactites, prefer a single peak — describes a motif whose plane stands *vertical*. None of them can fail here.

That is why this outline keeps every feather lobe and both ear tufts, and why 99.6% of it survives three extrusion widths at any size from 100 mm up, against the witch's 98.4% after deliberate simplification. **Do not import vertical-plane constraints into a flat part**; `chatgpt-prompts/owl-cutout.md` says the same thing to whoever writes the next one.

## The sleeve's length is decided by which way the puck points

The puck lies on its **side** here, aimed forward at the back of the plate, and that single fact sets everything about the sleeve.

`tealight_sleeve` establishes at length that a sleeve wraps the puck's opaque base and stops there, because on an **upright** puck the walls stand over the flame and every millimetre of shroud is light taken from the thing being lit. That reasoning inverts when the puck lies down: the walls are then *beside* the flame, so they block the light going sideways and pass all of the light going forward. Shrouding becomes the function. This part therefore runs the sleeve the whole length of the puck and asserts the opposite bound to the one `tealight_sleeve` asserts — deliberately, and the pair of assertions is the record of why.

So the transferable rule is not "sleeves stop at the base". It is that **a sleeve is a chock when the puck stands up and a snoot when it lies down**, and the length follows from that, not from the shape.

The value is written as the puck's overall height rather than as twice its base, even though on this puck those are the same number. Twice-the-base is how it was arrived at — Charles scaled the shipped 15 mm sleeve 200% in Z in the slicer — but the puck's height is *why* it is right, and it is the form that stays right if the puck is ever re-measured with a taller flame.

## `shelf_z` is where the shelf floor begins, not where the puck rests

The puck stands on the **top** of the shelf's floor slab, one `shelf_t` above `shelf_z`. `geometry()` derives the LED band from `shelf_z`, so for an upright puck those heights are one slab-thickness low and the coverage assertion checks a band the puck does not occupy.

It is left as it is, which is a decision rather than an oversight. The part is printed and accepted, this puck lies down, and moving `shelf_z` to fix a case the part does not use would move a number on a working object. What was done instead is to name `floor_top` in `geometry()` and position the sleeve from **that**, so nothing new inherits the wrong datum. Anything else that ever sits on this shelf must do the same.

The sideways numbers in `prints.md` were computed from `shelf_z` before this was noticed, and the correction runs the other way to what anyone expected: the improvised sideways puck was landing almost exactly on the eye centre, not 2.5 mm below it. The recommendation there to raise the shelf would have broken a correct alignment.

## What the sleeve costs

Two things, both small, both asserted rather than assumed — because both are fine at 140 mm and neither is guaranteed to be fine at another size.

**It lifts the flame.** A bare puck rests on its own cylinder; a sleeved one rests on a wall and sits centred in a bore, so the axis is a wall thickness plus half the bore-to-diameter difference higher. The axis has to stay inside the eyes, and `check()` says so against the traced eye band rather than against a remembered margin.

**Lying down, its across-flats becomes its height**, which puts it far above the shelf rim and well above the eyes. "The shelf is not visible from the front" is therefore no longer a statement about the shelf: the thing that has to hide the sleeve is the owl's silhouette, which is a property of the traced outline at whatever size it is drawn. `check()` walks the silhouette over the sleeve's full height rather than checking one width at one place — the same lesson as the three global-versus-local bugs above, applied before it could cost anything.

## Open threads

- **The branch has 4 islands and 23 planar overhangs** on its underside, from the forks curving up off the bed. Under a branch nobody looks at, supports are the cheap answer — but this has not been printed, and the underside is what sits on the shelf, so scars there could rock it. Worth a look at the first print.
- **The eye spacing comes from the artwork and has never been swept.** Spacing is what makes a stare read as menacing rather than startled; it is a parameter and it is cheap to test.
- **Nothing here is committed to 140 mm.** Every artwork-derived number is a fraction of `owl_h`, and the assertions are written against derived quantities, so a rescale should carry through untouched. That claim is untested.
