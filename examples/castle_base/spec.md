---
stage: print
---

# castle_base

A moated plinth for [`castle`](../castle/), with a drawbridge that lets down over the water on a pin hinge, two gate posts to hang chains from, and a lettered sign planted in the ground beside the approach. The castle sits in it; the two are one object cut into printable pieces, and the numbers along the cut live in `assemblies/castle_ground.py`.

## What it is for

The castle is an ornament that stands on a shelf and is looked at, lit, from the front. It currently stands on nothing — it ends at a flat rectangle, which is the one place the illusion stops. This part gives it ground to stand on and a way in.

**The drawbridge is the point of the object, not a detail on it.** It is the thing a visitor will reach for, so it moves: hinged, liftable by hand, and it stays where it is put when down. Everything else on this part is scenery around that one moving feature.

**The gate opens onto a forecourt.** Flat ground runs from the castle's gate out to the drawbridge posts, and only then does the bridge cross the water. This is not decoration: with the posts up against the facade they stood directly in front of the mouth, and the castle's own spec says the face is the design and anything that makes it less face-like is the wrong change. The posts have to be far enough forward that the sightline to the mouth is clear.

The moat wraps the front and the flanks and **stops before the back**, tapering away rather than ending in a wall. It did go all the way round for a while, and closing that ring was a real correction; it was given up deliberately to buy the depth the forecourt needed. The back of the castle is not a show side — it is open and full of tea lights — so it was the cheapest thing on the part to sell.

The original reasoning, kept because the mistake is instructive:

~~The moat goes all the way round: the castle stands on an island.~~ It is a broad pond in front of the gate where the road comes in, pinching to a narrow channel down the flanks and closing behind.

**That correction is worth recording.** This part was first built with the moat stopping a quarter of the way down each side, on the reasoning that a full wrap needed a base wider than the plate. It does not. Width limits how *wide* the flank channel can be — the castle is 134 mm across on a 170 mm plate — and says nothing about how far *back* it runs. Closing the ring costs depth, and depth was never tight. Two different constraints had been collapsed into one, and the cost was a moat that stopped for no reason.

## Constraints

**Fixed by the world**

- **The castle's ground plan, exactly**, from `assemblies/castle_ground.py`: a curtain wall ±63.65 mm across running y 0.35 → 82, two r = 9 mm corner turret discs centred at (±58, 0) of which 225° stands proud, and a gate surround 0.35 mm forward between x −15 and +19. Extremes ±67 wide, y −9 → 82.
- **The gate is at x = +2, not x = 0**, and is 28 mm wide. The castle's whole face is built about that line because the castle is asymmetric on purpose.
- **The gate threshold is 2.4 mm above the castle's underside** — it opens onto the castle's floor slab, not onto the ground. A bridge lying level with the ground outside is 2.4 mm below the floor it leads to unless the seat takes the difference out.
- The castle is **printed, published and 178 mm tall**. Nothing here may require reprinting it. That is what puts the chain anchors on posts belonging to this part.
- **Real chain, supplied by the user, not yet measured.** The anchor holes are a named parameter and generous; they are sized to a measurement when there is one.
- Bed and nozzle from `printer.toml`. **Width is the binding constraint**: the castle is 134 mm across the ground and the usable plate is 170.

**Fixed by the process**

- Base prints flat, island upward, in one piece. Every hollow — moat, seat, hinge sockets — opens upward.
- The drawbridge prints as a **separate piece**, flat, and so does the hinge pin if it is printed rather than cut from filament.
- **The base is a large flat slab and must not be a solid one.** Its mass is a slicer setting, not a geometric feature, and the spec says so here so that nobody solves it in geometry.

**Fixed by taste**

- **The castle rises out of the water at the sides.** No decorative lawn between wall and moat — a real moated wall meets its water directly, and the plate has no width to spare for a lawn anyway.
- Ground level outside the moat matches ground level inside it at the water's edge. Beyond that the outer bank falls away toward the front, because the approach has to arrive from somewhere rather than off a cliff.
- **The ground is dug, not poured.** Dirt piled up and loosely compacted: the surface undulates at roughly the scale of a shovelful. A flat extruded plane reads as plastic however good the shape around it is, and this part is mostly ground.
- **The moat's two edges are different kinds of thing.** The inner one is revetted masonry against the castle wall and is straight, following the building exactly. The outer one was dug and wanders. Making both a constant distance apart is what made the first version read as a lap pool.
- **The gate posts are masonry**, like the castle, but **smaller stone** — the castle is megalithic because it is a fortress wall seen across a room; a gate pier is small, close to the eye, and dressed. Sized in feet from the shared scale so the two read as the same world.
- The stonework does not have to match the castle's megalithic coursing, but the **revetment — the vertical face between island top and water — is masonry and should read as built rather than as extruded plastic.**
- **The sign is square to the front.** The plinth is a rectangle seen straight on; one object in it set at an angle reads as knocked over rather than placed. It faces the way everything else does.
- **The sign is oversized, on purpose, and for the same reason the cobbles are.** At the castle's scale a readable board would be a billboard. A real one would carry lettering a quarter of a millimetre tall. Where printability and the scale disagree, printability wins and the disagreement gets stated.
- **The ground is heaped, not carved.** The approach falls away in front of the moat and that fall is earth: its crest rolls over rather than creasing, and nothing on it reads as having been scooped out.
- Haunted. Nothing owes anything a mirror, and the bridge being off-centre is a feature of the castle that this part inherits rather than corrects.

## Acceptance criteria

### Does it do its job?

- [x] **The castle drops into its seat and sits flat**, without hand-fitting, and can be lifted out again. Asserted: the seat is the castle's footprint offset by the free clearance, and it clears the gate surround's 0.35 mm step.
- [x] **The drawbridge lowers to meet the gate threshold, not the ground.** Asserted: the deck's top surface, lowered, is level with the castle's floor slab, so there is no step to trip over in the one place a visitor looks.
- [x] **The drawbridge spans the water.** Asserted: lowered, the deck reaches the far bank with real bearing on it, and does not merely arrive at the edge.
- [x] **The bridge is centred on the gate**, at x = +2, and is no wider than the gate's surround can accept. Asserted against the contract, not against the castle's centreline.
- [ ] **The pin stays in — currently because of the chains, not because of the geometry.** A plain cylinder in a clearance bore with nothing wider than the bore at either end walks out when the base is tilted. In service the chains hold the bridge slightly raised and the tension binds the pin, which is a real fix and needs no reprint. Left open deliberately: it is satisfied by a force rather than by a shape, so it lapses the moment the chains come off. Every hinge criterion above asks whether the thing can be assembled and can turn; none asks whether it stays assembled.
- [x] **The hinge works and survives.** The pin is a clearance fit, the knuckles interleave without fouling, and the bridge swings from flat to upright without striking the castle or the bank. Asserted: swept clearance at both ends of travel.
- [x] **Raised, the bridge closes the gate** — it stands across the opening rather than beside it or short of it. This is what makes raising it mean something.
- [x] **The chain holds the bridge up, and is long enough to look like chain.** Two posts flanking the bridge, each with a through-hole, and matching holes at the bridge's outer corners. **The chain is taut with the bridge raised — that is what holds it there — and unhooked to lower it.** A fixed-length chain cannot be taut raised *and* permit lowering; the tip travels from far-and-low to near-and-high, so any anchor above the hinge is closer when the bridge is up. Real drawbridges take up the difference on a winch and a model cannot, so the chain does the job it can actually do. Asserted: the taut length is enough links to read as chain, and the two distances are reported so real chain can be checked against them.
- [x] **A hole a chain passes through is a hole a chain fits through.** Asserted against the nozzle, and left generous because the chain is unmeasured.
- [x] **It stands stably with the castle in it** and does not want to fall forwards. Asserted as the geometric fact the argument actually rests on, rather than by weighing anything: the base's footprint strictly contains the castle's on every side and all the mass this part adds lies inside it, so the support polygon grew and nothing moved outside it. The castle standing alone is an accepted criterion of `castle`; this is strictly better. Also asserted that the ground reaches further forward than back, because a facade with an open back carries its mass toward the front.
- [ ] **The lettering is cut for the way the sign is printed.** Contrast and depth are substitutes: three layers is enough wherever contrast comes from somewhere else — a second filament, or a paint pen on the raised letter tops — and about twelve are needed without it, because a bare one-colour sign is legible only by the shadow its type throws. Not assertable — which regime applies is a fact about the print — so the build says out loud which one the geometry assumes.
- [ ] **Inking has a floor of its own and it is unmeasured.** The relief must keep a pen's tip off the board between the stems, which is a different constraint from legibility and is the one number missing from the lettering table.
- [ ] **The sign is legible at arm's length, and reads as a made object.** Two lines of routed type on a plain board carried by two posts. Asserted: the type fits inside its margin, and its mean stroke is over one and a half extrusions — under that, routed lettering stops looking routed. Whether the wording is the right wording is read off the render.
- [ ] **One filament change recolours the lettering and nothing else.** The board is a whole number of layers thick and carries no raised frame, so everything above its face is a letter and a single pause at that height is a clean colour boundary. This is why the frame was dropped; it is a printing requirement, not a styling preference. Asserted: the board's thickness is an exact multiple of the layer height, and a build with a frame says out loud that the trick no longer works.
- [ ] **The sign stands where a sign would stand and blocks nothing.** Off to the left of the approach, read on the way in, clear of the sightline to the castle's mouth. Asserted: both post holes are on dry, level ground behind the crest and outside the road — the band of ground there is about eight millimetres wide in places, and a plan view does not show a leg going over the edge of it.
- [ ] **The sign lifts out.** It is a separate piece on two pegs, so it can be painted separately and removed. Asserted: peg and socket clear each other, the pegs are buried deep enough not to wobble, and the piece does not interfere with the base.
- [ ] **The approach reads as a bank of earth, not as a scoop of ice cream.** The crest rolls over; nothing on the slope is a distinct crater. Read off the render — and off the printed object, which is where the first version's craters showed and the render's did not.
- [ ] **The ground reads as dug earth, not as a moulding.** The surface undulates; nothing that shows is a flat plane. Read off the render, not asserted — the question is whether it looks like dirt, which no assertion knows.
- [x] **The outer bank is irregular and the inner one is not.** Read off the plan.
- [x] **The gate posts read as coursed stone at arm's length** — beds round all four faces, perpends staggered so no joint runs through, stones visibly smaller than the castle's.
- [x] **The sightline to the castle's mouth is clear.** Nothing this part adds stands in front of the face. Read off a render taken from where a person would stand, not from directly above — this is the criterion the first version failed while looking fine in plan.
- [x] **The road is paved and the ground is not.** Setts in staggered rows on the forecourt and the ramp, dirt everywhere else, and the two textures do not overlay each other.
- [x] **The drawbridge reads as timber.** Boards laid across the span, so the seams run across the direction you walk — which is how the thing is built, planks bearing on side rails.
- [x] **The road arrives.** The approach climbs from the front edge of the plinth to meet the bridge, rather than ending at a wall, and reads as a causeway rather than as a ramp cut in a block.
- [x] **The plinth never leaves its own envelope.** Asserted: nothing below the underside, nothing outside the plan it was sized from. The roughing is subtractive precisely so this is free — the version that raised mounds by burying spheres put lumps 3.5 mm below the face the whole thing stands on, and it built, passed validity and rendered perfectly from every angle except the one nobody looks at.
- [x] **The moat reads as water you could not simply step over.** Asserted **at the castle's own scale** — 1.37 mm to the foot, from the contract — rather than against a millimetre figure or an aspect ratio: at least twelve feet across at the gate, and at least four feet deep. A moat has a size in the world, and converting is the only honest way to pick one; sized by eye against the nozzle it comes out as a gutter round a model.

### Is it built correctly?

- [x] **One connected solid per piece**, and watertight meshes.
- [x] Fits the configured bed in the pose it is exported in, **with margin left over** — this part is within 8 mm of the plate's width and that is close enough to want stating.
- [x] `PRINT_ROTATION` is stated for each piece, and the overhang check runs in those poses.
- [x] **Nothing overhangs.** Every pocket opens upward in the print pose; the hinge is the only place this is even in question.
- [x] **Nothing is thinner than the nozzle can draw**, the hinge knuckles and the chain-hole walls included.
- [x] **The ground plan is read from `assemblies/castle_ground.py`**, with no castle dimension repeated as a literal here. `castle.check()` asserts the contract still describes the castle.

### Only a print can settle these

- [x] **Whether the hinge clearance is right** — a printed pin hinge at this size is one test print away from either seized or sloppy, and no assertion knows which.
- [x] **Whether the bridge stays down.** Its own weight should hold it; if it does not, that is a counterweight or a detent, and which one is a decision to make with the object in hand.
- [x] **Whether the moat reads as water** in the filament that gets used, or just as a trench. Related: whether it wants painting, flooding with resin, or leaving alone.
- [x] **What chain actually suits it**, and whether the posts are tall enough to make it look like it lifts the bridge rather than merely being tied to it. **Settled: chains fitted, holding the bridge slightly raised, and the posts are tall enough.** A few degrees of lift is sufficient to illustrate the mechanics and look realistic — what sells it is the chain being taut and the deck off its seat, not the angle reached. Link size and length still unmeasured.
- [ ] **How much the slab's mass and print time actually come to** at a sensible infill, and whether that is tolerable or the part needs a redesign to shed it.
- [ ] **Whether the revetment reads as masonry** at arm's length, or as texture.
- [x] **Whether the sign's pegs are the right fit** — a 0.25 mm slack peg in a printed socket is one test print from either tight or loose, and no assertion knows which. **Settled: 0.25 mm per side is right**, described from both edges — no wobble, no persuasion needed.
- [ ] **Whether the lettering survives the nozzle.** The stems are a shade over 0.7 mm. The mean-stroke assertion says it is drawable; only the print says it is readable.

## Open questions

- **Whether the base should carry a puck of its own.** The gate is lit from inside the castle; a lit moat is a different and probably worse idea, but nobody has looked at it.
- **Whether the two pieces should be one print or two.** They are separate pieces, but they could go on one plate; that is a slicer decision and depends on whether the bridge wants a different orientation for strength across the hinge.
- **Whether the hinge pin should be printed or cut from 1.75 mm filament**, which is free, perfectly round and stronger than anything printable at that diameter.
- **Whether the castle should ever be reprinted to meet this part properly** — with chain anchors in the facade where a real drawbridge's would be, and a gate arch that admits a raised bridge. Explicitly out of scope now; recorded because it is the obvious second generation.
