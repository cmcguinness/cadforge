# castle_base — why the numbers are what they are

## The constraint that decided the shape

Width. Everything else had room.

The castle is 134 mm across at the ground and the usable plate is 170, so a moat that goes all the way round has 18 mm a side to work with — and that has to cover shore, water and outer bank. It does not fit, and a base that splits into tiles puts a join across the ground in front of the castle, which is the one surface a person actually looks at.

So the moat wraps the front and dies into rising ground part-way down each flank. From anywhere you would stand to look at this object it reads as continuous. `moat_back` is where it stops, and it is set to a bit past the castle's front third rather than to anything derived — the constraint is *look*, not arithmetic.

Depth was never tight, and the design spends that freely — see *Width is spent, depth is free* below.

## The seat depth is not a choice

`seat_depth` is the castle's floor slab, taken from the contract, and it has to be exactly that.

The castle's gate opens onto its own floor, 2.4 mm above its underside. Sink the castle by exactly that slab and the floor inside comes level with the ground outside — so the drawbridge can lie flush and lead somewhere. Any other value puts a step at the threshold, which is the single place on this object where a person's eye is guaranteed to travel, because that is where the bridge points it.

This is asserted rather than commented, and the assertion compares two derived quantities rather than checking that a parameter equals a constant. If either the contract or the island height moves, it fires.

## The gate is off-centre and so is everything

`ground.GATE_X` is +2, not 0. The castle's whole face is built about that line because the castle is haunted and owes nothing a mirror.

Every part of the bridge, both piers, both posts and both chain holes are placed from that symbol. None of them is placed from this part's own centreline, and the assertion that the deck's midpoint equals the gate's is there because a 2 mm error is invisible in a render and obvious in the hand.

## The abutment exists because the shore is 2 mm

A moated wall meets its water directly — a lawn between them reads as a model of a castle rather than as a castle — and the plate has no width for a lawn anyway. So `ledge` is 2 mm.

But a hinge needs ground behind it, and 2 mm is not ground. Hence the abutment: a pier projecting forward of the castle's face, which is what the hinge is carried on. Having built it, it is also the only flat surface wide enough for the gate posts to stand on, so they stand there. That was luck rather than planning, and it is the reason `abut_half` is wide enough for the posts rather than just for the bridge.

## What the shore actually measures

`ledge` is 2.0 and the material that gets printed is 1.7, because the seat is cut into the shore and takes `seat_clear` back out of it. At the turrets it stands the full depth of the water.

The first version had `ledge` at 1.5, which printed as 1.2 — three extrusions — and passed an assertion that was checking `ledge` against the nozzle. Checking a parameter instead of the thing derived from it is how a wall gets certified at a width it never has. The assertion now names the difference.

## The hinge, and the one number that is not obvious

The pier's far corner is the whole problem.

The deck sweeps the front-upper quadrant about the axis. The pier stands in that quadrant, so the deck must be notched at the pier positions, and the notch has to be deeper than the pier's most distant corner — not deeper than the pier, which is the number you reach for first and which is too small. `notch` is `hypot(knuckle_r, island_h − axis_z)` plus clearance, which comes out half again as deep as the pier itself. Notch it to the pier's depth and the bridge jams part-way up, having built, rendered and asserted perfectly.

Related, and the reason the piers are boxes rather than the half-buried cylinders that a hinge usually gets: a cylinder there is a 8 mm-wide overhang hanging over open water. A pier standing out of the moat is both printable and what the thing would actually be built as.

The lug on the deck is a *full* cylinder about the axis, not a half one, so the pin is enclosed rather than sitting in an open channel it can lift out of. That is what the cylindrical relief cut into the abutment is for. It costs no overhang because it opens upward and forward at once.

## Interference, not solid count

The obvious assertion for a three-piece assembly is that it is three solids. It is wrong here, and the way it is wrong is worth keeping.

Lowered, the deck **rests** on its landing. Base and deck meet on a face and fuse into one solid, so the count is two — which is the correct physical answer and a useless test.

What has to be true is that no two pieces occupy the same space, so the check is the volume of their intersection. Faces in contact have zero volume, so resting is free; every way this part can be got wrong — lug fouling its relief, pier catching the notch, a pin too fat for its hole — shows up as a positive number in one place.

## The chain is taut when the bridge is UP

This took a wrong turn worth recording. The criterion first written was "taut raised, slack lowered", which sounds obviously right and is geometrically impossible for a fixed-length chain: the tip travels from far-and-low to near-and-high, so any anchor above the hinge gives a *shorter* distance raised. A chain long enough to let the bridge down is 21 mm slack when it is up.

Real drawbridges resolve this with a winch — the chain's length changes. A model cannot, so the chain's length is the raised distance, it is what *holds* the bridge up, and lowering means unhooking it. That is honest, it is what a hand-operated model does, and it puts the chain visibly under load in the state you would display the object in.

`post_h` is then set by how the chain looks rather than by structure: a taller post lengthens the taut chain. The geometry reports the taut length, and the assertion refuses a chain too short to read as one. Both distances are reported so they can be checked against real chain when there is some.

## The deck prints upside down

Laying the bridge down the way it sits on the castle is the obvious pose and it is wrong.

The hinge lug is a full cylinder centred on the deck's **underside**, so half of it hangs below that face. Printed the right way up, the deck balances on that bead with its entire 830 mm² underside floating 4 mm in the air. The overhang check caught it; nothing in the assembled render would have, because in the assembly the bridge is lying on ground that holds it up.

Flipped, the bead becomes a half-round sitting flat-side-down on the plate — self-supporting — and the road surface, which is the face that shows, goes against the plate where the finish is best.

The general form of this: **`pieces()` is not a formality.** A part that is correct in the assembly can be unprintable in the pose the assembly implies, and the two questions are asked in different views.

## Width is spent, depth is free

Front-to-back nothing competes, so `front_reach` is 34 and the water at the gate is 28 mm — twenty feet, a real moat, and enough that the raised bridge covers 90% of the gate opening rather than 60%.

Across the width there is nothing to give. The castle is 134 mm on a 170 mm plate, so after the shore and the outer bank the flank channel gets 9 mm — under seven feet. It reads as a channel from a three-quarter view and as a groove from directly above, and there is no version of a one-piece base that fixes it. Recorded as a fork rather than a defect: the answer, if it matters, is separate outer-bank wings that clip on at the flanks and put the join in the water where nobody looks.

## A moat is not an offset

The first version made the water a constant distance from the shore all the way round, and it came out looking like a lap pool. The fix is not more wobble, it is noticing that a moat's two edges are different kinds of thing: the inner one is revetted masonry against the castle's wall, so it is straight and follows the building exactly; the outer one was **dug**, so it wanders. Only the outer one should be irregular.

It is built by rolling a disc of varying radius along the shore and taking the union. A union of overlapping discs cannot self-intersect, which an offset curve very much can — this island has four reflex corners, where the gate pier meets the shore and where the turrets meet the wall, and an offset through those crosses itself and produces a face that looks fine until it is cut from something.

The radius varies with how far forward the point is and how far out to the side. The second of those is not styling: at the turrets the shore is already near the plate's limit, so a pond-width moat there would put the base over the bed. **The shape the plate allows and the shape a real moat takes happen to agree** — wide where the road comes in, pinched at the corners.

The crossing is a rectangle rather than discs, because rolling discs leaves a scalloped bank: between two neighbouring centres the union falls a few microns short of their radius. Everywhere else that is invisible; where the bridge lands it left 15-micron ridges of bank standing inside the deck, which the interference check found.

## The width constraint was misread, and then the ring was traded away anyway

This part was first built with the moat stopping part-way down each flank, on the reasoning that a full wrap needed a base wider than the plate.

That was wrong, and the way it was wrong is the useful part. **Width limits how wide the flank channel can be. It says nothing about how far back the channel runs.** Closing the ring behind the castle costs depth, and depth was never tight. Two independent constraints had been collapsed into one, and the result was a moat that stopped a quarter of the way down the castle's side for no reason at all — with a confident explanation attached.

The ring was then given up deliberately, which is a different thing from never having had it: the forecourt needed the depth, and the back of the castle is not a show side. Knowing the ring was *available* is what made that a trade rather than a limitation.

## Roughing ground: cut, never add

Dirt wants to look piled and loosely compacted rather than poured, so the ground is roughed with shallow spherical dishes on a jittered grid.

The first attempt also **buried spheres to raise mounds**, which is the obvious way to get hills and is wrong here. A sphere sunk until only its cap shows has its far side most of a diameter below the surface — which is below the underside of the plinth, so the part grew lumps on the face it stands on. Near the shore the same spheres bulged sideways into the moat below the waterline. It built, it was watertight, and it rendered perfectly from every angle except the one nobody looks at.

Cutting can only ever remove material from the envelope. Adding has to be clipped to it, and the clip is the whole problem. There is now an assertion that the base never leaves its own envelope — nothing below the underside, nothing outside the plan it was sized from.

**Order matters more than anything else here.** Rough first, then cut the seat, the landing and the hinge. Those come back exactly flat without the terrain needing to know they exist, and the ground still runs continuously up to their edges. Roughing last would pit the seat and leave the castle rocking.

## The terrain's numbers are set by the kernel, not by taste

Two couplings, both learned by hitting them:

**Coverage.** For the scallops to merge instead of leaving isolated dimples, the bite depth must be at least `grain² / 8R`. At the current grain and sphere that is 0.675 mm — so the amplitude in the file is the *shallowest* one that gives continuous ground. Gentler undulation is not a matter of turning it down; it needs a finer grain or a bigger sphere.

**Cost.** Both of those are superlinear, and that ruled out fine dirt entirely for a while: 332 dishes did not finish in five minutes, nor did 147 at an 18 mm sphere, against 47 seconds for 147 at 15 mm.

The way out was noticing **what** the cost is superlinear in. It is not the number of tools; it is the number of tools that overlap **each other**. The kernel has to resolve the whole tangle before it can subtract any of it, so five hundred mutually-overlapping spheres is one enormous problem rather than five hundred small ones.

Overlapping, though, is a property of the grid rather than of the job. Colour the grid with a stride wide enough that two dishes of the same colour can never touch — allowing for the jitter and for the largest radius the variation permits — and each colour is a set of **disjoint** tools. Disjoint tools are nearly free: no tangle, just N independent bites. Five hundred dishes become three dozen cheap cuts instead of one impossible one.

The stride is derived from the grain, the jitter and the maximum radius rather than written down, because if the guarantee ever silently stopped holding the only symptom would be builds mysteriously getting slow again. It is worth asserting it directly if this is ever ported: the worst within-batch gap should be comfortably positive.

**This generalises.** Any large set of scattered boolean tools on one body — rivets, perforations, texture, speed holes — has the same structure and the same fix.

**The second half of the cost was not the count at all.** Even batched, the build ran for many minutes once the approach slope was computed correctly — and the culprit was a few dozen dishes straddling the **kerb**, the vertical step where the paved road stands proud of the bank either side. A sphere cutting through a wall like that leaves slivers along it, and slivers are what the kernel spends its time on. Skipping any dish within about a radius of the road corridor took the build from minutes to seventeen seconds, and gave a cleaner kerb line as a bonus. The dishes were only ever cheap while they were *wrong*: before the slope was fixed they hung in the air over the bank and cut nothing at all, which is why the correct version looked like a performance regression.

**A dead end worth not repeating.** Roughing the flat ground FIRST, while the slab is still a bare prism and the boolean is at its cheapest, is the obvious optimisation and it does not work: the water cut against an already-roughed slab returns an EMPTY result, while the identical cut against a plain slab is fine. Carve first, texture last.

Two more traps in the same area:

- **Do not reach for `clean()`.** It is the obvious repair for the coincident edges that a hundred-odd overlapping cuts leave behind, and on a solid this size it ran for over five minutes without finishing. The real fix is upstream: never take a near-tangent bite. A sphere grazing the surface by microns leaves a sliver face the kernel cannot represent, and a hundred-odd chances at it is how the solid came out formally invalid while every other check passed.
- **`.move()` mutates.** It moves the shape in place and returns the same object; `.moved()` copies. That is harmless until the pieces are cached, at which point moving a cached piece moves it for every later caller — including the assembly the renders are made from. Verified rather than assumed.

## The approach looked scooped because of one missing normal

The front slope came off the printer looking like ice cream had been taken out of it, while the flat ground beside it — cut with the *same tools at the same settings* — read as loose dirt. That difference is a bug, not a matter of taste, and it is invisible in the source.

A dish is positioned by putting its centre a radius-minus-bite above the ground point it is cutting. On level ground that leaves exactly the bite asked for. On a slope of angle θ the sphere is still set against a *horizontal* plane, so what it actually takes out, measured perpendicular to the ground, is `r(1 − cos θ) + d cos θ`. The approach falls 8.5 mm over 13, which is 33°, and the term nobody wrote down is the one that dominates: an 8.5 mm sphere asked for 0.7 mm digs 1.9 mm. Three times the crater, from code that reads as correct.

So the surface is described once, by a helper that returns a height **and a normal**, and every dish is set along that normal. The same helper serves the crest, so the arc and the tools that cut into it can never disagree.

**The crease mattered as much as the craters.** Where flat ground met the slope there was a knife-edge, and nothing heaped by a shovel has one. It is rounded now by an arc tangent to both faces. The included angle is about 147°, which is shallow, so the radius has to be large to show at all — the rounding only reaches about `0.3 r` along each face, and 18 mm buys a soft shoulder rather than a bevel. It is cut as an extruded profile rather than as a fillet on an edge: the crease is broken into three pieces by the road, and an edge selector that has to find the right two will find the wrong ones the first time anything moves. The road keeps its sharp crest deliberately — it is a kerbed causeway, and its setts are laid on a flat plane.

**Two things that were tried and are not worth trying again.**

- *Furrows along the contour.* Capsule-shaped scrapes in rows, on the reasoning that piled earth lies in courses. Courses of one width at one spacing read as fluting — a machined surface, worse than the scoops. Jittering the spacing, the depth and the width, and scattering dents over the top, made it busier without making it earth. The slope wants the same ground the rest of the part has; what was wrong with it was the depth.
- *Broader dishes for gentler undulation* — `terrain_r` 8.5 → 12 at the same grain. It is the right instinct and the solid comes back **formally invalid**: a shallower rim angle means more near-tangent bites, which is the sliver failure the minimum-bite rule already exists to prevent. Raising the radius means raising the minimum bite with it, and the two are coupled through the coverage rule as well. Not free, and not attempted again without a reason.

## The sign fits in a band of ground about eight millimetres wide

The board is parallel to the front edge, and getting there took the long way round. Turned toward the road it met a visitor face-on, and the yaw also swung its right-hand end forward, away from the water — which is a real constraint, because the strip of dry ground between the crest and the moat narrows from twenty millimetres at the left edge to about six in front of the gate. But the plinth is a rectangle seen straight on, and one object in it set at an angle reads as knocked over rather than placed. So the yaw went and the sign moved forward instead, to where the band is wide enough to take it square.

Both post holes are asserted to be on dry, level ground — behind the crest and clear of the water and the road — because that band is narrow enough that any change to the moat or to the board's width can push a leg off the edge of it, and a plan view will not show it.

**The lettering is sized by the nozzle and nothing else.** At the castle's foot the board is twenty-three feet across, which is absurd and is the same absurdity the cobbles already carry: a real six-foot sign carries quarter-millimetre letters, so either the sign is oversized or it is blank. Rockwell Bold at this size gives stems a bit over 0.7 mm — under two extrusions, which is where routed type stops looking routed. `check()` measures the type rather than trusting it: twice the area over the perimeter is the mean stroke width of a stroke-based shape, and it is asserted against the nozzle. The morphological opening that ARTWORK.md prefers is the better tool for a traced silhouette and cannot be used here — eroding a glyph raises an error the moment a counter closes, which is exactly when the answer would be interesting.

The socket floor, not the ground surface, is what sets how high the sign stands: it is cut to the peg's length from nominal ground level, *after* the roughing, so a dish that happens to cross the mouth of a hole cannot change the answer.

## The pin is retained by the chains, and the model cannot see that

The hinge pin is a plain cylinder in a clearance bore with nothing wider than the bore at either end, so on the bench it walks out when the base is tilted. **In service it does not, because the chains hold the bridge slightly raised and the tension binds the pin in its bores.** That is a real fix and the right one — it costs nothing, it is reversible, and it is what the chains are there for anyway.

It is written down because **the thing doing the retaining is outside the model**, which is the failure this repo has been bitten by before. Three consequences follow, and none of them is visible in the geometry:

- **The pin is only retained while the chains are on and under tension.** Take them off — to paint, to photograph, to reprint the deck — and the loose-pin behaviour comes straight back. That is not a regression, and nobody should go looking for what broke.
- **Do not tighten `hinge_clear` on the strength of this.** The hinge is free and correct at 0.4 mm per side, verified in the hand before the chains went on. The binding is a service condition, not a fit, and reading it as a fit would seize a hinge that currently works.
- **The open criterion stays open rather than being ticked.** "The pin stays in" is satisfied by a force, not by a shape, and the honest record says so. If the geometry is ever wanted to do the job on its own, the move is a head on one end of the pin — it drops in the same way, sits in open water outboard of the pier, and reads like a pintle head.

The chains also settled the prediction the geometry was designed around: **a fixed-length chain stops the bridge short of vertical**, which is what `chain_up` and `chain_down` were reported for and what the spec said a real drawbridge looks like anyway. The lift is *slight* — a few degrees, not a half-raise — and it is sufficient. What reads as a mechanism is the chain being taut and the deck being off its seat, not the angle it reaches. So the post-height ceiling that `check()` enforces, which caps the lift, costs nothing worth having.

## Caching, and why it became necessary

`_base` is built three times per `cad build` — once for the render, once for each half of the interference check, and again by `pieces()`. That was free when the part was a slab with some pockets. It is not free once the ground is roughed with a hundred-odd spheres, and it was the single biggest win available.

The wrappers keep the old `(p, g)` signature; `g` is ignored because it is always `geometry(p)`. Passing it was only ever a way of not recomputing it, which is what the cache is for now.

## The mass is a slicer setting

388 cm³ if it were printed solid — 481 g, which is most of a spool for a plinth.

It is not solved in geometry and should not be. A pocket in the underside would print as a ceiling over open air; the part is modelled island-up so that every hollow opens toward the nozzle, and hollowing it downward gives that up. Infill is the right tool and the spec says so explicitly, so that nobody later reads the volume figure and starts designing ribs.

## Deliberately not done yet

- **The revetment is smooth.** The vertical face between ground and water is a retaining wall and the castle above it is megalithic masonry; it should read as built. That is a texture pass, and texture passes are what this repo has learned to do last.
