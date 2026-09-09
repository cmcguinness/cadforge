# castle — print log

One entry per physical print. This closes the outer loop: the renders and the checks can only judge geometry, and everything else is discovered here.

Record a print even when it succeeds. A design that works and nobody wrote down *why* it works is one refinement away from losing the property by accident.

## Template for an entry

### YYYY-MM-DD — iteration #N (`<params digest>`)

- **Settings:** material, layer height, supports, orientation on the plate.
- **Result:** what came out.
- **Measured vs. modeled:** the numbers that differed, and by how much. This is what turns a `nominal` constraint in spec.md into a `measured` one.
- **Verdict:** and then run `cad accept <part> good|bad|mixed "<why>"` so the iteration history carries it too.

---

### Iteration #25, **printed at 50% scale**

- **Settings:** PLA, 0.2 mm layers, tree supports, upright as exported (`PRINT_ROTATION` is zero — the mesh is already in the print pose). Scaled to 50% in the slicer: 68 × 46 × 89 mm. ~2 hours against ~9 at full size.
- **Why half size:** a sanity check on the design, not on fidelity. A shaded orthographic render cannot say whether the face reads as a face across a room, whether four tiers register as receding depth when light rakes across them, or whether the thing reads as a castle rather than as boxes with battlements. Two hours is a cheap way to ask.
- **Result: really good.** The design holds up.

**What a 50% print could not settle, and why — so nobody reads this as more than it is:**

- **Nothing about lighting.** The face chamber halves to 62 × 23 mm and a puck is 35 across and 30 tall. No tea light fits, so every lit criterion in spec.md is still open, including whether `paper_spread` is anywhere near right.
- **Two features were below what the nozzle can draw**, and were expected to fail before the print started:
  - the bat's eyes, 1.10 → 0.55 mm, under 1.5 extrusion widths. They survived slicing, and the 0.40 mm divider between them survived with them, but at that size the slicer leaves a gap between extrusions rather than tracing a perimeter, so the result says nothing about 1.1 mm at full size.
  - the gate's bars, 1.40 → 0.70 mm, about 1.7 extrusions.

  Everything else cleared comfortably: walls 3 lines, teeth 3.2, merlons 5.

**Changed after this print:** the five non-canine upper teeth were shortened by 20% **of their own length** so the two canines read as fangs rather than as two teeth that happen to be pointed. Of their own length, not a flat amount: the arch clips the outer teeth short, so a fixed cut would have taken as much off a 4 mm tooth as off a 20 mm one and levelled them. The outer teeth hanging lower than their neighbours is what gives the arch its shape, and it was kept on purpose.

- **Verdict:** `mixed` — the shape is right and the lighting is untested.

---

### Iteration #30, full size, **~11 hours** — first attempt, FAILED

- **Mesh:** `castle.stl`. 103,070 triangles, watertight, zero islands. 136 × 92 × 178 mm, 179.5 cm3.
- **Settings:** PLA, 0.2 mm layers, tree supports, upright as exported. **`Remove small overhangs` ON** — without it the slicer props every mortar course, on the show side. See SLICING.md.
- **Estimate: ~11 hours** — ordinary for 178 mm of this much geometry, but worth writing down, because it is the ratio that matters when planning a change: **the 50% test was two hours against eleven.** That is why it was worth doing, and why a surface-wide change — a different block size, a different mortar depth — is better judged from a detail crop or a cropped test piece than by putting the whole castle on the plate again.

- **Result: FAILED partway up the first floor**, and was killed by hand. The support that collapsed was an internal tree headed for the **second**-floor slab — so it fell long before reaching what it was there to hold. It was building an 88 mm column and did not survive the first third of it.

  **The cause was a slicer setting, not the geometry.** `Support on build plate only` was ON. Every chamber floor in this model is *model material*, so that setting forbids a support from starting on one — it can only start on the plate. The slicer's remaining option was to originate supports outside the footprint and lean them in through the open back, which turns a short column into a tall unbraced one:

  | support stands on | free column height |
  |---|---|
  | the chamber floor it holds up | 45.2 / 35.6 / 31.6 mm |
  | the build plate | 47.6 / **87.6** / 121.6 mm |

  An 87 mm free-standing tree, leaning, inside a cavity, is a topple waiting to happen. **The open back is the trap**: it makes the interior reachable, so the slicer will happily route supports through it rather than refusing.

---

### Iteration #30 (`083466d5`), full size, reprint

Same mesh, `castle.stl`. Nothing in the model changed.

- **Settings changed from the failed attempt:**
  - **`Support on build plate only` → OFF.** The fix. Supports now stand on the chamber floors, which is what the table above is about.
  - Tree **branch angle 45° → 30°**, so branches lean less far from vertical. Not to be confused with the *threshold* angle, which decides which model faces get support at all; this one governs the support's own geometry.
  - **Bottom shell layers 3 → 5**, so a chamber ceiling has more solid material resisting the peel when supports come away. Worth knowing: the second-floor slab is 2.4 mm — twelve layers at 0.2 — so 5 bottom plus 3 top leaves about four layers of infill. That slab is effectively solid.
  - Tree style **Hybrid**.
  - **Top Z distance left at 0.2 mm** (one layer), deliberately. Removal was never the observed problem; the collapse was. Changing a fourth variable would have muddied which of them mattered.

- **Result: PERFECT.**

- **What this settles:** the masonry reads as stone at full size rather than as noise, the spires print clean, and the support question the spec raised is answered — the chamber ceilings *do* need support, and the answer is to let it stand inside the castle rather than outside it.

- **What it does not settle:** everything about light. No puck, no paper. Every lit criterion in spec.md is still open, and `paper_spread` is still a guess.

- **The lesson worth carrying:** an eleven-hour print failed and the model was never at fault. When a print fails, ask what the *slicer* was forbidden to do before changing geometry — a setting that is merely conservative on a solid part can be actively harmful on a hollow one. Filed in SLICING.md, because the next hollow, open-backed part will meet it again.

**Lit, same day, no paper yet — passes UAT.** Tea lights dropped in bare, with no diffuser of any kind, and it got high marks from a household reviewer. That is a stronger result than it looks, and worth being precise about *why*:

- The paper diffuser was designed in as the thing that makes the face work — `paper_spread` exists because a bare puck is close to a point source and the eyes and mouth are far apart. **The face reads without it.** So the paper is an improvement to a design that already works, not a load-bearing part of it. That is a much safer place to be, and it was not the expected one.
- It also means the pucks go in and come out by hand, and the thing stands and reads at room distance, all confirmed by handling rather than by inference.

**With the paper in**, glued behind the face and behind the bat window, on a shelf at room distance:

- **`paper_spread` carries.** Both eyes and the whole mouth light evenly from a single puck, and the eyes are the far corners of the face — the openings the spec flagged as "placed in defiance of" the guess. The guess was good enough. It remains a guess rather than a measurement; what is settled is that it is not *wrong*, which is what the criterion asked.
- **The flat back took the glue.** One sheet over the eyes and mouth together, as designed. No fiddling with separate pieces.
- **The bat window lights cleanly** and the bat reads unmistakably at a glance — ears, wing sweep, body. The traced outline was worth the trouble; the by-eye version would not have survived being this legible.
- **The masonry reads as stone at room distance**, irregular rather than a lattice, which is the thing no render in this repo was able to show.

**The pupils read, and the face is doing exactly what it was drawn to do.** Seen close up and lit, each eye is a warm arch with a dark round-topped pupil sitting low in it, both converged inward — the "looking at something close up" effect that took several iterations to land. The gate surround is visibly clear of coursing while the wall around it is fully bricked, so `gate_margin` is doing its job at the size that matters.

**A note on reviewing from a photograph**, because it cost a wrong entry in this file: an earlier frame from a downscaled, compressed animation showed the eyes as plain even arches, and that was written down here as "the pupils are not reading", with a theory about the diffuser flattening them. It was an artifact of the scaling. A detail crop of a full-resolution still showed them immediately. The repo already knows that a render cannot show surface texture at whole-part zoom; the same trap applies to *photographs* of the finished object, and the same answer applies — **look at a detail crop before concluding a feature failed.**

**The four corner turrets stay dark, by decision.** Their windows read as black holes in the wide shot rather than glowing, and the spec had assumed ambient spill would reach them. It does not. Lighting them would mean either more pucks or routing light into four separate shafts, and Charles's call was that it is not worth what it would cost — unlit windows suit a haunted castle. The criterion was rewritten to say so rather than left open, because an unmet criterion and an abandoned one are different things and only one of them is a defect. The middle-storey flank slits, which do sit in a lit chamber, glow correctly.

**Still open:** whether a paper-lined shaft lights the top turret's four windows, and whether changing a battery is tolerable.

### The paper went in, behind the bat window and the face

Photographed lit, in purple PLA, with three tea lights and paper diffusers fitted behind the **bat window** and behind the **face** — see `finished_castle.jpg`, which is now the part's headline image. This is the configuration the ornament actually lives in, and the earlier "no paper yet" entry above describes only the first evening.

Two things it confirms, neither of which the model could have said:

- **The paper does its job on the openings it is behind.** The bat reads crisply against an even field and the eyes and gate read as a face, rather than as three bright hotspots with a flame visible in each.
- **The walls glow.** In purple at `wall = 2.4` the facade transmits, so the object reads as lit stone rather than as a dark box with holes in it — the opposite of the silhouette polarity the model was drawn to. That is a **filament-colour** effect, not a geometry one, and it is the single largest visual variable in the part. Black would give the silhouette the model actually describes.

**The turret shafts were never lined, and now they will not be.** Charles's call: the turrets stay as they are. That closes the criterion as **abandoned rather than unmet**, which is the same distinction already recorded for the four corner turrets — lighting them costs either more pucks or four separate light paths, against a facade whose depth is already spent on what a puck needs, and on a haunted castle a dark window is not a defect.

**Batteries: livable.** The pucks come out through the open back by hand and go back in. Nobody has been driven to redesign anything, which is the bar that criterion was actually setting. If it ever does become a chore, the answer is wiring the whole castle to one switch rather than changing any geometry — six tea lights is a lot of switches, and a single LED source removes the batteries entirely.

**With both settled, the castle is done.** Every acceptance criterion is now closed, by measurement, by looking, or by a decision recorded as a decision.

### Photographed on a turntable — six pucks, five of them sideways

A full 360° turn was filmed (`videos/finished_castle.mov`, reduced to `finished_castle.gif` for the README) and the back half of it records a configuration nothing in this repo predicted or models:

- **Six tea lights, not three** — three in the ground-floor chamber, two in the middle, one at the top. The design assumed one puck per chamber. That assumption was about *fit*, and it was read as a *quantity*. A chamber wide enough for a puck is wide enough for three, and three light the corners of a storey that one lights only the middle of.
- **The lower five lie on their sides, aimed out through the facade.** Only the top puck stands upright, where its flame is meant to be visible through the tower window. This is now the **third** part to end up sideways at the bench — after `owl` and `mini_castle` — which stops being a coincidence and starts being a default that the specs should state.
- **There is paper inside the chambers as well as behind the openings**, showing as bright white fields on the chamber floors and rear walls, bouncing light forward. The design treated paper as a diffuser *over an opening*; here it is also a reflector *behind a source*, which is a different job for the same sheet.

None of this is a defect and none of it required a geometry change. It is the outer loop paying out: the object in the room is more capable than the object that was specified, and the gap was invisible until somebody put six pucks in it and turned the light off.

**A dark turret window is visible in the turn too**, which independently confirms the abandoned criterion above rather than leaving it resting on one still.

### Printed clean, and the supports had to be demolished

The support settings that stop the feet letting go are the same ones that make the supports unremovable, and this print found the far end of that.

- **Settings:** as before, plus `Bottom Z distance` 0.2 → **0**, `Branch diameter angle` 5° → **12°**, `Branch diameter` 2 → **4**, `Independent support layer height` **off**. Everything else unchanged — `support on build plate only` still off, branch angle still 30°, `Remove small overhangs` still on.
- **Result: it printed.** No collapse, nothing came loose. The two previous attempts failed at the supports and this one did not, so the settings work.
- **The cost: removal was demolition.** The supports did not want to release. At 12° over a 36 mm column a 4 mm branch tip becomes a roughly 19 mm foot, and at zero bottom gap every bit of that is fused to the chamber floor — about five times the footprint of the original settings, all of it welded rather than resting.
- **Verdict:** printed. Keep the settings if a print that survives matters more than an easy strip; take the angle to 8° otherwise. Recorded in `SLICING.md` under the hollow-parts section, with the trade set out as a table.

**The general shape of it**, since this part has now taught it twice: each fix here creates the next failure one step along. Supports on the plate topple, so they were moved onto the chamber floors; feet on chamber floors let go, so they were welded and fattened; welded fat feet will not come off. None of the three settings is wrong and none of them is free.

**Agreed for next time: dial back both ends.** Branch diameter angle 12° → 8° for the feet, branch diameter 4 → 2 for the ceilings. Keep `Bottom Z distance` at 0 — it is the half of the pair that does the real work — and leave `Top Z distance` alone, because a wider gap is a ceiling that sags further and these chamber ceilings are wide.

**Both are reversions, and the second one is a correction.** Branch diameter was first written off here as nearly irrelevant, on the grounds that over a 36 mm column the taper swamps it. True of the foot, false of everything else: the tooltip calls it the diameter of support *nodes*, which is the **tip** — the end touching the ceiling. Taking it 2 → 4 doubled the weld at every ceiling while buying about 2 mm at the foot. It is the wrong knob at the bottom and the harmful one at the top.

**The `.3mf` is saved** at `accepted/castle.3mf` — the filename's date comes from the mesh it was built on, not from the slice, which is from this run. Reading its settings back is also what caught the error above: `independent_support_layer_height` is still **on** in it, so the recommendation to turn it off was never actually applied, and any reasoning that assumed it had been is void.

### The paper's own edge shows through the wall

Charles, fitting diffusers: the first-floor sheet has to run the **full width** of the wall, because a sheet that stops part-way across leaves "a noticeable shadow of the paper you can see through the castle walls".

This follows directly from something already recorded above — in purple at `wall = 2.4` the facade **transmits**, and reads as lit stone rather than a dark box. Once the wall is translucent, anything behind it is a silhouette, and that includes the diffuser meant to be invisible. A paper edge sitting mid-wall is backlit from one side and not the other, so it draws a line across the masonry.

**Nothing in this repo could have found it.** The renderer shades opaque solids; every assertion reasons about geometry, printability or line of sight from the flame. Translucency is a filament property that only exists in the object, and this failure is *caused* by the material rather than merely invisible to the model.

Two consequences, both now in `paper_templates.py`:

- **The sides of a sheet are not a glue margin, they are a lighting requirement.** They run out to where the flat wall ends, so the edge lands in a corner where the geometry changes anyway and there is nothing to see. The first-floor sheet is therefore 103 mm wide rather than the 72 mm that gluing alone would want.
- **The first-floor sheet has a right way round**, and getting it wrong reintroduces the fault. The face is built about the gate at x = +2 rather than the castle's centreline, so there is about 4 mm more wall to its left than its right; reversed, it overhangs one side by that and leaves a 4 mm gap on the other — and the gap is a backlit paper edge. The template is marked TOP / LEFT / RIGHT for that reason.

It is conditional on the filament: in an opaque black the walls do not transmit and none of this applies. The templates stay at full width regardless, because a sheet that is too wide costs a moment with scissors and one that is too narrow is visible from across the room.
