---
stage: done
---

# castle

A haunted castle facade, lit from behind by tea lights, standing on a shelf. `inspiration/castle.png` is **inspiration, not a specification**; `inspiration/source-bat-image.png` is artwork that gets traced. The only part of either that is load-bearing is the face.

## What it is for

An ornament that sits on a shelf or a mantel and is looked at, lit, from the front. Tea lights go in from behind and come out again to have their batteries changed — often enough that fishing for them must not be a chore.

**The bottom of the castle is a face.** Two windows are eyes and the gate is a mouth. That is the design; the arch profiles, the tooth count and the window outlines serve it. If a change makes the castle more architecturally correct and less face-like, it is the wrong change.

The back is not a show side. Braces, shelves, baffles and whatever else the interior needs are welcome there.

## Constraints

**Fixed by the world**

- **The tea light is not a glowing disc.** It is an opaque base 35 mm across with a 10 mm flame above it — see `projects/halloween_lantern/shared.py`, which carries the measured figures. Its base cannot go anywhere its 35 mm will not fit; its flame can go up a 23 mm shaft.
- All puck dimensions are `measured` (calipers).
- **Paper diffusers, applied by hand.** Behind the face, and potentially lining a turret shaft. Glue-stick and printer paper; the person gluing judges the fit.
- **PLA, effectively opaque.** Anything that must glow has to be an opening.
- Bed and nozzle come from `printer.toml`. **Height is nearly spent**: the castle is 178 mm on a 180 mm machine.

**Fixed by the drawing**

- The colours of `inspiration/castle.png` are a depth map — higher is further back. Four tiers: curtain wall, keep, great tower, top turret.
- The elevation is what exists. There is no back and no sides in the source.

**Fixed by the scale**

- The castle reads as a **120 ft keep**, so a foot is about 1.4 mm. Every architectural feature is sized in feet and then checked against the nozzle, rather than chosen to suit the nozzle and left meaning nothing.

**Fixed by the process**

- Prints in one piece, upright, on the configured bed. Open at the back.
- **The exported mesh must be watertight**, not merely a valid solid. Those are different questions and the slicer asks the second one.

**Fixed by taste**

- **The surface is giant brick and mortar** — megalithic blocks, nine feet by four and a half, not domestic brickwork. Irregular: varied block lengths and jittered courses, because a perfect bond reads as machine-laid tile.
- **The roofs are tiled, not built.** Shingle courses that get finer as each cone closes in.
- **Not everything is stone, and the masonry must say so.** The gate is wrought iron, the pupils are eyes, the bat is a creature in a window, and each merlon is a single block. None of them carries coursing.
- **Haunted, so asymmetry is an asset.** Nothing here owes anything a mirror.
- Lit, it should look like a building with people in it.

## Acceptance criteria

### Does it do its job?

- [x] **It reads as a face.** Someone who was not told sees eyes and a mouth before they see architecture, lit and unlit, at a normal distance.
- [x] **The mouth reads as a mouth** — seven upper and seven lower teeth, with the second and sixth drawn down into canines. Fewer reads as a vent.
- [x] **The bars read as bars**, thin iron with light between them, not as a perforated panel. Teeth roughly twice the bar.
- [x] **The eyes read as eyes** — oval pupils, cropped by their sills, converged slightly inward.
- [x] **The bat is recognisable as the supplied animal**, at its own proportions, with its ears, muzzle and both eyes present.
- [x] **Every motif is anchored.** Nothing retained inside an opening is held by less than the wall around it. Asserted: zero islands.
- [x] **Every opening opens into something.** No blind pockets. Asserted.
- [x] **Nothing stands behind an opening** — no corbel, deck, pillar or riser between a window and its chamber. Asserted against the built solid.
- [x] **Each lit opening lies within its puck's reach**, or explicitly declines to claim it does. Asserted for those that claim it.
- [x] **The flank slits glow** rather than reading as black. The **four corner turrets are deliberately dark** — they take no puck, lighting them is not worth what it would cost, and unlit windows suit a haunted castle.
- [x] **Every puck can be inserted and retrieved by hand.**
- [x] **The back of the face is flat**, with margin to glue paper over the eyes and mouth at once.
- [x] **It stands stably** and does not want to fall forwards.
- [x] **The surface reads as stone** at arm's length — irregular, not a lattice.
- [x] **The masonry stops where the castle stops being masonry:** no coursing across the gate or its surround, on a pupil, on the bat, or on a merlon.
- [x] **Nothing the masonry cuts escapes the surface it belongs to.** Grooves stay on their own block and never break through a wall, a floor or a parapet. Asserted for the flat faces; verified by probe for the towers.

### Is it built correctly?

- [x] **One connected solid**, and a **watertight mesh** — no degenerate triangles, no non-manifold edges.
- [x] Four tiers, ordered as the drawing's colours.
- [x] **Every parapet is a railing on a roof**, not a notch through a building, with a walkway of at least six feet behind it. Asserted.
- [x] **Every tower stands wholly on something.** Asserted.
- [x] Fits the configured bed in the pose it is exported in.
- [x] `PRINT_ROTATION` is stated, and the overhang check runs in that pose.
- [x] **Nothing is thinner than the nozzle can draw.** The gate's bars are the exception, at three extrusion widths, deliberately.
- [x] **The artwork is in the repo** — `inspiration/castle.png`, `inspiration/source-bat-image.png` — so every trace can be re-run.

### Only a print can settle these

- [x] **It reads as a face across a lit room**, to someone not told.
- [x] **How far a paper diffuser actually carries light.** `paper_spread` is a guess and several openings are placed in defiance of it.
- [x] **Whether a paper-lined shaft lights the turret's four windows.** **Not pursued — the turrets stay as they are.** This is an abandoned criterion rather than an unmet one, and the distinction matters: lighting them means either more pucks or four separate light paths, against a facade whose depth is already spent on what a puck needs. That is a lot of structure for a small effect on an object where some windows being dark is *correct*. The same call was already made for the four corner turrets; this extends it to the top one.
- [x] **The brick reads as brick**, not as noise.
- [x] **The spires print clean** — no stringing between them.
- [x] **Changing a battery is not annoying.** Livable. The pucks come out through the open back by hand and go back in, and nobody has been driven to redesign anything — which is the bar this criterion was really setting. Not delightful, and if it becomes a chore the answer is wiring rather than geometry.
- [x] **How much support the chamber ceilings actually need**, and whether the scars matter where they land.

## Open questions

- **Where the tea lights finally go.** Deliberately unsettled while the architecture moves; the pedestals were removed for that reason.
- **Filament colour.**
- **Whether `paper_spread` is anywhere near right**, and what it should be.
- **Whether the puck facts should move out of `projects/halloween_lantern/`.** They are a fact about an object, not about Halloween, and this is the second consumer.
