# castle — notes

**Read before editing the model. Update when you learn something.**

Numbers live in `model.py`. This file says why.

## Design intent

**The drawing is inspiration; the face is the specification.** `inspiration/castle.png` is a flat elevation whose colours are a depth map. Everything geometric here was re-derived — the drawing's crenellations measure 2 mm and its portcullis bars 1.3 mm, both well under what is worth printing at this size. What is *not* negotiable is that the lower castle reads as a face.

**Depth is the free dimension; height is not.** Three chambers stacked, each having to swallow a 30 mm puck, plus a spire above them, consumes nearly all the bed's height. Depth had nothing competing for it. That asymmetry decided several things that otherwise look arbitrary — most visibly that the castle is a box with a sculpted front rather than the stepped relief the drawing implies.

**`paper_spread` is a guess, and it is no longer allowed to veto a shape.** The face's features are ~30 mm apart in z and one puck lights ~15 mm of that directly; the assumption that a glued-on paper diffuser carries the rest is a number nobody has measured. It began as a hard assertion and started refusing positions that were *chosen* rather than derived — at which point a guess is overruling a design. Openings that cannot be shown to be lit now say so (`assert_lit=False`) instead of being moved to suit the arithmetic. The blind-pocket and nothing-behind-it checks still apply to them; only the reach of the flame is left open, and the print settles it.

Pedestals were removed for the same reason: raising pucks to satisfy the sum was solving a calculation rather than a problem, while the architecture was still moving.

**`FACE_X` is not zero on purpose.** The castle above the face wanders right of centre, which is inherited from the drawing and kept because it is haunted. A face centred on the geometric middle of an asymmetric building reads as applied to it rather than as belonging to it.

**Chamber separation is structural, not incidental.** The solid bands between chambers are what make one puck light its own windows and nobody else's, so the chamber floors and tops are not free numbers. `check()` asserts the gaps.

**The unlit turrets are bored into the chamber below them.** A sealed turret is a dark turret, and a dark window reads as a black slot rather than as part of a lit castle. The shafts are the whole reason those windows have any light at all.

## Hard-won knowledge

**A build123d primitive joins whatever builder is open when it is *constructed*.** A helper that returns `Pos(...) * Box(...)`, called from inside `with BuildPart()`, contributes its shape **twice**: once where the caller places it, and once unplaced at the origin. The result is a valid solid, passes every check, and renders as a plausible castle with a phantom slab through it — the bounding box was the only thing that gave it away. Every primitive here now carries `mode=Mode.PRIVATE` *and* is constructed before the builder is entered. Belt and braces, because the failure is silent.

**A cone on a rectangular block is not the same as a cone on a cylinder.** The tower roofs share an axis with the cylinder beneath them and are supported for free. The spire cones sat on a block, centred on their tier's *front face* — so the front half of each hung over open air, with nothing under it and no path sideways to anything. That is 201 islands, not overhangs: they cannot droop into place. Setting each cone a full radius back from the face fixed it outright. Zero islands now, and the check is what found it, not the render.

**A semicircular head can only exist on a tall opening.** The original `_arch` capped a slot with a half-circle, so once the width approached twice the height there was no slot left and the opening was simply a disc — the first mouth was 22 mm across and 15 mm tall and came out a perfect circle. Every opening is a **pointed** arch now, struck as the intersection of two discs whose centres sit on the springing line, which is how one is drawn on paper. It has the property the semicircle lacks: the apex height is chosen and the radius follows, so an opening can be as wide as it likes. `_arch` asserts the one case it cannot do (head shorter than half the width) rather than quietly degenerating.

**A pupil has to meet the sill, not float in the middle.** Retained material inside a hole is the failure that destroyed `raven_lantern`'s lettering. The first attempt hung an oval in mid-opening and rescued it with a 1.3 mm neck, which is thin enough to be the next thing that breaks.

The shape that works is a whole **ellipse whose lower part falls below the sill**. Nothing clips it: the pupil is subtracted from the window, and below the sill there is no window to subtract from, so the sill crops it for free. Two wrong answers were tried first — an arch (straight sides, reads as another little window) and a slot with a round cap (same). Burying part of the oval is what makes it an eye rather than a bead.

**The castle needed a scale before its architecture could be sized.** Every architectural dimension here was originally chosen by eye against the nozzle — big enough to print, small enough to look fine — which is a printability constraint doing a job it cannot do. The result was a parapet as tall as a two-storey building and merlons six feet wide, and nothing in the model could have objected, because at no point did any number claim to mean anything in the world. Declaring `FOOT` fixed that: a feature that exists in the world has a size in the world, and the honest way to pick it is to convert and then check the nozzle can draw it. Where the two disagree, printability still wins — but now the disagreement is visible instead of being the only input.

**A parapet stands on a roof; it is not a notch through a building.** The crenellations were cut the full depth of each block, which in plan turns the whole roof into a square wave and leaves nothing to walk on. It survived several reviews because **a front elevation cannot show it** — the error is entirely in plan and section, and the face was where everyone was looking. Worth generalising: a facade part will hide any mistake that lives in the depth direction, and the top and section views are the only two that can catch it.

**A flat overhang is usually a step that should have been a slope.** Every conical roof oversailed its tower by widening abruptly, which leaves a horizontal annulus with nothing under it. That is legal — it is attached all the way round, so it droops rather than falling — but it droops on every tower, and it was the worst surface on the part. Growing the same 1.2 mm out over 3 mm of height turns each one into a 68° cone: no flat face, no droop, and **the silhouette is identical**, which is the point. It cost seven flat overhangs out of twenty-three and nothing at all in appearance. Worth looking for the same shape elsewhere before reaching for supports.

**Which way a feature points decides whether it prints.** This is the rule the whole face turned out to rest on, and it is not symmetric:

- an **opening that reaches down into material** — a canine slot ending inside the gum line — has solid material all round it. Free.
- **material that reaches down into an opening** — a tooth hanging into the mouth — has air beneath its tip and no path sideways along that layer. That is an island on every layer of its length, and it needs supports *inside the mouth*, where removing them leaves scars on the show side.

Three separate face features hit this: the floating pupil, the hanging fang, and the upper teeth before there was a gum line to stand them on. Each time the fix was the same — turn the feature round so the hole points into the material rather than the material into the hole. It is worth checking any new face feature against this before modelling it, because the render cannot show it and only the islands check will.

**Face design is the user's, not the model's.** A version with angled wedge eyes and an elliptical grin was tried, was more obviously menacing in the abstract, and was wrong — the castle is gothic and the wedges read as a pumpkin bolted to a building. Two iterations were spent discovering that the reference drawing's own vocabulary (pointed arches, portcullis bars, a pupil in a window) was the answer. The general lesson is the one `ARTWORK.md` already states from the other direction: adapt the artwork to the part, but do not invent a *different* artwork because the geometry was easier.

**Openings must be probed off-centre.** Two diagnostic passes reported the face "not cut" because the sample points landed exactly on a mouth bar and inside a pupil — the parts that are *supposed* to be solid. Sampling a grid and reporting the open fraction says something true; probing one point says whatever the point happens to hit.

**A facade hides every mistake that lives in the depth direction.** Three got through in one session, each invisible in the front elevation and obvious the moment anyone looked at `top` or `section`:

- crenellations cut the full 82 mm depth of each block, so in plan every roof was a square wave with nothing to walk on;
- a 7 mm buttress given a storey's depth, which became a fin running the length of the castle at a height nothing else occupied;
- a platform sized from the puck it carried and never checked against the room it stood in — it went through the great tower's side walls into open air.

All three were valid solids that passed every check. The lesson is not "look at the top view", it is that **a feature sized from one constraint must be asserted against its surroundings**: the walkway rule, the platform-inside-its-chamber rule and the nothing-behind-an-opening rule are all the same shape of check, and each was written after the render caught what the model could not.

**Kissing is not joining.** Two solids that meet exactly face-to-face or edge-to-edge tessellate into non-manifold edges — four triangles round one edge — and a cone that comes to a true point tessellates into slivers with two coincident vertices. Slicers reject both. **OCC calls the solid valid throughout**, because BRep topology and a watertight triangle mesh are different questions, and only the second one is what gets printed. Everything here now overlaps deliberately: pillars run up into decks, decks bite into walls, roof cones stop at a 0.4 mm tip. A tip finer than the nozzle was fiction anyway.

**A window near a ceiling forbids a corbel.** Corbelling the chamber ceilings cut the flat unsupported area by 45%, and walled up half the windows doing it, because a corbel closes in exactly where most of the windows are. The fix was not a smaller corbel but a derived one — the limit is the head of the highest opening the chamber serves, which on this castle leaves almost nothing. That is the right answer, not a disappointing one.

**Artwork: the aspect ratio is what an eye-trace gets wrong.** The bat was drawn freehand from a thumbnail at 1.64 wide-to-tall; it is 1.071. Squashed flat, it was unrecognisable in a way that was hard to name and easy to see. Tracing it properly from the file — a boundary walk, Douglas-Peucker at 3 px — fixed it in one pass, and its height is now *derived* from that ratio so it can never be stretched to fill a box again.

Three further things the bat taught, in rough order of how much they cost:

- **A motif must clear the opening that frames it.** Drawn at their true height the ears reached the head of the window and merged into the wall above, so the animal lost the two points that say "bat" more than anything else.
- **A pointed arch cannot be wide.** Its head must exceed half its width in height, so a wide opening becomes all head and closes over whatever it was cut to show. Wide motifs need segmental heads.
- **Small features get placed by the material available, not by the reference.** The bat's eyes are 3.1% of its half-width in the source — 0.4 mm here, a gap between two extrusions. Enlarged to something printable they no longer fitted where they sat, and both the near-tangency at the head's edge and the 0.44 mm strip between them surfaced as **islands**. Nothing in any render showed it.

**A hollow object has to be reachable, and nothing in the model knew that.** Internal pillars with corbelled capitals were built to cut the slicer's supports, and on that measure they worked: flat unsupported area fell from 20474 mm2 as designed, to 17051 with tapered decks and coned shafts, to **7075 with pillars — a 65% cut**. Every constraint anyone had written down was satisfied. They were placed by search rather than by eye, tested against three rules: the capital fits its chamber, it clears the puck, and it does not stand between that puck and a window it lights.

They were removed anyway, because **a hand has to get in there**. A puck is placed by reaching through the open back, and paper is glued behind the windows from inside. A 32 mm capital at chest height in a 45 mm-tall chamber does not stop a puck fitting — it stops an arm. None of the checks could see it, because every one of them reasons about geometry, light and printability, and access is none of those.

The lesson is not "do not use pillars". It is that **the model had no representation of the human who has to assemble the thing**, so it could optimise freely against every constraint it knew about and still produce something unusable. The missing check has a shape: a clear corridor from the back opening to each puck station, and to the inside face of every window that gets paper — wide enough for a hand, not for a puck. Worth writing before anything is put inside a chamber again.

The supports stay. They land inside chambers where nothing shows, which is the cheap place for them, and `SLICING.md`'s rule is that supports are judged by what they touch.

## The masonry

**Build it as sketches, not as bricks.** A castle this size is some 1500 blocks, and cutting them one at a time is 1500 solid booleans — minutes of OCC. Each flat face's mortar is instead ONE sketch, its beds and perpends placed with grid locations, fused in 2D where it is cheap, then extruded and cut once. A roof's shingles use polar locations for the same reason. About a second a face.

**Do not texture what is buried.** The great tower rises from the ground but is not seen below the keep's roof; the top turret's shaft is invisible below 124. Skipping the buried parts cut the cutter-construction time by two thirds and changes nothing visible. The rule needs both axes, though — testing only the x overlap hid the keep towers to z=90 when they bulge forward of the keep and are in plain sight from 50.

**Size the grid to fit rather than clipping it to fit.** Overshooting a face and intersecting a rectangle over it was most of the cost of the entire masonry pass: a 2D boolean against several hundred rectangles, once per face. Counting the courses that fit costs nothing.

**Jitter, but deterministically.** A running bond with a strict half-brick offset is still a perfect lattice and reads as tile. Every course starts at its own offset and every block is a different length — from a hash of the course index, never `random`, because a build must give the same castle every time or the history and the oscillation guard are comparing different objects.

**A cutter knows nothing about the surface it is grooving.** This produced three separate escapes in one afternoon, and they are worth listing together because they are one bug wearing three hats:

- the tower's vertical joints run from the ground up, and at the bearings facing back into the castle there is no tower face there at all — just floor. They punched three square holes clean through the base slab, visible only from underneath, which is a view nobody had rendered.
- a course band is a full annulus, and where a tower is embedded in a wall the arc runs almost along the depth axis at the flanks — so it stopped grooving a tower and started sawing lengthways through a 2.4 mm wall, leaving slots you could see daylight through.
- the perpend loop admits a course whenever its BED fits, then stands the joints a full block higher, so the top course overshot its face by up to a block and carved up through the parapet above. Each merlon is one stone in the world and they were arriving quartered.

The first two are fixed by clipping to where the surface actually exists; the third by clipping the joints to what is left above the bed. All three are the same lesson as the platform that went through the great tower's wall: **a feature sized from one constraint must be checked against its surroundings.** The flat-face case is now asserted — every masonry cutter's bounding box must stop at its block's roof line.

**Kissing is still not joining.** Clipping the tower bands at the tier's front plane put their clip face exactly where the wall's own bed grooves start, at exactly the same course heights, since both are struck from the same pitch. Two cutters meeting face-to-face there tessellate into non-manifold edges. Clipping 1.5 mm behind the plane instead buries the overlap inside the wall and shows nothing.

**A slicer's "remove small overhangs" filters by AREA, not by span.** A mortar bed and a shingle course leave identical ledges — a third of a millimetre, which any printer bridges — but the bed's face is a flat strip and the shingle's is a ring wrapped round a cone, so the ring's area clears the threshold while its span is just as trivial. The checkbox fixed the walls and left every roof course growing its own supports.

The fix is not a better setting. **Taper each groove shut at its head**, so there is no horizontal face to find: 730 downward faces became 517, and the largest on any roof went from a ~47 mm2 ring to 13 mm2. It also looks more like tiles, which overlap the one below and cast exactly that shadow. Supports on the show side would have scarred the very thing they were propping.

**The render cannot show surface texture at whole-part zoom, and said so convincingly.** `sheet.png` showed smooth walls when the mortar was cut correctly, because the renderer's depth-jump threshold scales with the view — 0.66 mm across the whole castle, against a 0.6 mm groove — and a groove's side walls are edge-on while its floor shares the wall's normal, so there is no crease either. Nothing was wrong with the model. Had it been trusted, the obvious "fix" would have been to deepen the mortar until the renderer noticed, changing the part to suit a rendering threshold. **Detail features need a detail crop**, the way the face and the bat have.

**A full print is about eleven hours; the half-scale one was two.** Unremarkable for the size, but the ratio is what makes the test print worth doing and what makes a surface-wide change — block size, mortar depth — something to judge from a detail crop rather than from another eleven hours on the plate.

## The wall turns out to be a filter, not a boundary

Lit, the whole castle **glows**. Not just the openings — the walls themselves transmit, so the object reads as lit stone rather than as a dark box with holes in it, and the second-storey block above the bat window is visibly brighter than the rest because less material stands between it and the puck.

**This was not designed for and is not what the part was modelled as.** Every opening here was drawn as a silhouette cut — material opaque, light only where the wall is absent — which is the polarity the whole lantern set uses. At `wall = 2.4` in a light-coloured filament that assumption is simply false: the wall is thin enough to be an optical element, and wall thickness is doing the job `pumpkin_lantern` documents, where it is a *filter* whose value sets how much light comes through rather than a boundary that either blocks or does not.

Two consequences worth holding on to, because both are invisible in a render:

- **It is why the thing looks good**, so do not "fix" it. A castle whose walls were genuinely opaque would read as a black cutout, which is a colder object.
- **It changes what a thicker wall costs.** Raising `wall` for strength or for print time now dims the whole facade, not just some margin. That trade did not exist when the wall was believed opaque, and a future session reasoning only from the model would not know it is there.

The effect depends on the filament, which is **not** a parameter of this part. The same geometry in black PLA is a different object.

## The corner turrets are dark on purpose

The four corner turrets have windows and no light behind them. The spec originally assumed spill from the face chamber would reach them; lit, it plainly does not, and they read as black holes.

**That was settled by decision rather than by geometry: they stay dark.** Reaching them means either more pucks or four separate light paths, against a facade whose depth is already set by what a puck needs — a lot of structure for a small effect, on an object that is meant to look like a haunted castle, where some windows being unlit is *correct*.

Worth writing down because it will look like an oversight to anyone reading the model later. It is not: it is a place where the cost of a feature was weighed against what it bought and the feature lost. If it is ever revisited, the cheapest route is almost certainly a lit shaft shared between two turrets rather than a puck each.

## If there is ever a second one

**There is no plan to build another.** This castle is finished and works. These are two faults found by *handling* the object — the kind nothing in the model, the renders or the checks can raise — and they are written down because that is the only way they survive to a version that may never exist.

- **The turret tips are genuinely sharp.** `tip_r = 0.4` truncates each cone to stop the apex tessellating into slivers, which was a mesh concern and nothing else. 0.4 mm of radius is a needle in the hand. If the cones are ever revisited, flatten the tips enough to be blunt — this is an ornament that gets picked up, carried and dusted, and a value chosen to satisfy the kernel happens to be a value that hurts. Worth generalising: **a number chosen for the mesh is not thereby safe for the hand.**

- **The chamber floors need a lip at the back.** Nothing retains a puck. Jar the castle and a tea light can slide out of the open back, which is the same opening that makes the pucks reachable in the first place. A few millimetres of upstand along the rear edge of each chamber floor would hold them without interfering with insertion — the puck drops in from above rather than sliding in horizontally, so a lip costs nothing to load against.

  This is the assembly-access constraint from the other direction. The spec learned to ask whether a puck can get *in*; it never asked whether it stays in. Both belong in any future part that holds a loose object behind an opening.

## Open threads

- **`paper_spread` is a guess** and the face depends on it. Measure it on the first print: how far past the flame does the paper actually carry light?
- **32 planar overhang faces**, worst 90°. Not yet examined one by one — the chamber ceilings and the crenellation undersides are the likely sources, and the crenellations at least are the same geometry the lantern set printed without trouble.
- **No assembly-access check.** See above; it is the constraint that killed the pillars and it is still unwritten.
- **No brickwork yet.** The spec asks for giant brick and mortar over the whole show side; the surface is currently flat. The cheap technique is one compound cutter of mortar grooves subtracted once, never brick by brick.
- **The great tower's puck goes in from the back, high up.** Whether that is actually reachable by hand has not been tested against a real puck.
- **The stub is a placeholder.** It exists because the drawing has an unmatched crenellated lump on the right, and asymmetry is wanted, but it currently reads as a mistake rather than as a building.
