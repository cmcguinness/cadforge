# castle_base — print log

One entry per physical print. This closes the outer loop: the renders and the checks can only judge geometry, and everything else is discovered here.

Record a print even when it succeeds. A design that works and nobody wrote down *why* it works is one refinement away from losing the property by accident.

## Template for an entry

### YYYY-MM-DD — iteration #N (`<params digest>`)

- **Settings:** material, layer height, supports, orientation on the plate.
- **Result:** what came out.
- **Measured vs. modeled:** the numbers that differed, and by how much. This is what turns a `nominal` constraint in spec.md into a `measured` one.
- **Verdict:** and then run `cad accept <part> good|bad|mixed "<why>"` so the iteration history carries it too.


### The base, with the castle in it

- **Result:** it works. The castle seats in it and the whole thing reads. Charles: *"The base is tested with the castle and it's great!"*
- **What that settles, and only a print could:** the seat accepts the printed castle without hand-fitting, the assembly stands, and the forecourt does its job — the gate posts are far enough forward that they no longer stand in front of the face. That last one was a real defect caught by eye, not by any check: in plan the posts looked fine, and it took a view from where a person actually stands to see them cutting the sightline to the mouth.
- **Still open:** everything about the moving parts. The hinge clearance, whether the bridge stays down under its own weight, what chain suits the posts, and whether the roughing reads as dirt rather than as rubble at arm's length.

**The defect this print generation existed to fix was found by hand, not by the model.** The pin could not be fitted: the hinge axis sat exactly on the forecourt's front face, so the pin would have had to be threaded through fifteen millimetres of solid stone. Every check passed — right diameter, bores aligned, no interference between pieces, a perfect assembled render. The part was simply impossible to put together, which is a question a render cannot ask.

Standing the hinge off the face was not enough either, and the assertion written for it said so with numbers: 301 mm³ of base in the pin's path, about 15 mm of clear run against a 30 mm pin. **The bores are now slotted open at the top** — push the pin through the deck's lug on the bench and drop the pair in. The bridge lifts straight off again, which turns out to be useful for painting.

The general lesson, which is the one worth carrying to other parts: **a check that the assembled object is correct is not a check that it can be assembled.** They are different questions and only the first one is easy to write.


### Read off the photograph, under raking light

Photographed deliberately with harsh side lighting to bring the ground texture up. `finished_castle_base_with_castle.jpg`.

- **The roughing reads — but as rubble and broken rock, not as loose dirt.** That is worth saying plainly because it is not what the parameter is named for. At 0.7 mm deep on ~6 mm scallops the ground looks like a boulder field, which suits a castle and nobody has complained, but if the intent were really *piled dirt* the amplitude would have to come down and the grain with it, and the coverage rule makes that expensive. Filed as a thing that is good rather than a thing that is right.
- **The cobbles read at arm's length**, both on the forecourt and down the ramp, and the change from lane-width to full-forecourt paving was the right call — the courtyard now reads as a courtyard.
- **The posts read as coursed stone** clearly, at a glance, in black. Smaller stones than the castle's was the correct decision: at this size the castle's megalithic courses would have given a pier two blocks tall.
- **The planks read**, running across the span as intended.
- **Black was a good choice** for everything the castle is not. The moat floor stays smooth and unlit and reads as water in shadow; against the purple it separates cleanly.

**Still open, and now the only things left:** whether the hinge swings freely rather than merely fitting, whether the bridge stays down under its own weight, and how the chains hang once fitted.


### The hinge, in the hand

**It swings freely and the bridge stays down.** Both were open questions no assertion could close, and both came out right first time, so the numbers behind them are worth pinning down rather than leaving as luck:

- `hinge_clear` at 0.4 mm per side gave a working printed pin hinge at 3 mm pin diameter, in PLA at 0.2 mm layers, with the pin printed rather than cut from filament. Free, not sloppy.
- The deck stays down under its own weight alone — no counterweight, no detent. The deck is 4 mm of solid PLA over a 33 mm span and the hinge friction is low enough not to hold it up, which is the balance that had to come out right and could have gone either way.
- The notch depth rule held: `hypot(knuckle_r, island_h - axis_z)` plus clearance. The pier's far corner never catches the deck anywhere in its travel, which is the thing that would have shown up as a bridge jamming part-way up.

That leaves only the chains, which are on order.


### Aborted on the first layer, and it was the plate

The reprint carrying the sign and the reworked bank tore on the first layer badly enough to abort. **A freshly washed plate fixed it and the reprint is holding.**

Recorded because the symptom pointed the wrong way and cost a diagnosis. Tearing — lines splitting, the nozzle dragging through what it just laid — reads as a nozzle set too low, and the first instinct was Z-offset and first-layer flow. It was adhesion. Unstuck line gets picked up on the following pass, and on this part there is a great deal of following pass: the base's underside is a **single flat 251 cm² face**, checked in the mesh at 130 triangles with no slivers and no overlaps, matching the nominal plan to 2 mm². The geometry was never in question.

What makes this part expose a marginal plate when nothing else here does is the size and the solidity of that face. A small footprint holds on a plate that is not quite clean, and when it does fail it *lifts*, which announces itself. At 251 cm² of solid every square millimetre is bearing, and one contaminated patch in the middle tears instead. Filed to `SLICING.md` under geometry rather than machine, because it will apply to the next large flat-bottomed part and not to the machine in general.

Still open on this print: whether the sign's pegs fit their sockets, whether the lettering at 2.4 mm of relief survives handling, and whether the reworked bank reads as earth rather than as scoops.


### The sign, in two colours, and how deep lettering actually needs to be

**Printed with a manual pause at the board's face and a second filament for the type, and stopped deliberately three layers into the lettering because it already looked right.** That accident is the finding.

**Contrast and depth are substitutes, and contrast is much the cheaper one.**

| printed | letters need | why |
|---|---|---|
| two colours | **3 layers** (0.6 mm) | the colour carries it entirely |
| one colour | **~12 layers** (2.4 mm) | the shadow the type throws is the only thing making it read |

A one-colour sign at 4 layers read as an outline rather than as letters, and tripling the relief was what fixed it — so the depth was never about depth, it was about buying a shadow. Give the letters their own filament and there is nothing left for the depth to do.

Worth taking the win rather than treating it as a curiosity, because three layers is better in every respect once the colour is there. The stems stop being tall thin walls, so the most fragile thing on the piece stops being fragile — at 2.4 mm each stem was a 0.75 mm wall standing three times its own width, and handling it was a question. There is less print above the pause. And there is less of the second colour for purge bleed to spoil, which matters when the whole feature is a few layers thick.

`sign_letter_relief` is now stated in layers rather than millimetres, because "three layers" is the actual finding and it should survive someone changing the layer height. The default is the two-colour value; a build below eight layers prints a note saying so, since which regime a sign is cut for is a fact about the print and nothing in the model can see it.

**The frame had to go for this to work at all** — see the previous entry and `sign_relief`. A raised frame prints in the same layers as the bottom of every letter, and a pause is per-layer rather than per-region.


### The two fits, in the hand

**The sign's pegs are right, and the number is worth keeping.** `sign_fit` at 0.25 mm per side, on a 6 × 3.6 mm peg in a socket cut after the roughing: goes in without persuasion, no wobble once seated. Charles: "Not enough slop to make it wobble, not too little so that it's hard to set the sign in." That is the whole window described from both edges, which is rarer than a number that merely worked — it says 0.25 is near the middle of the range rather than at one end of it. Reuse it for a printed peg-in-socket at this scale rather than re-deriving.

**The hinge pin turns well and is not held in.** Two separate findings.

- *Assembly has an order, and the model does not say so.* The deck has to be seated fully home before the pin will slide across. That follows from the bores being slotted upward and the lug being a closed bore, but nothing states it, and it is the sort of thing that gets rediscovered by forcing something.
- *The pin can walk out.* It is a plain 3 mm cylinder in a 3.8 mm bore with nothing wider than the bore at either end, so tilting the base slides it. Everything about the hinge that was asserted — clearance, interleave, swept travel, assembly access — is about whether it can go together and turn. **Nothing ever asked whether it stays together**, and that is a gap in `check()` rather than a surprise about PLA.

**If it gets glued, glue the pin to the DECK'S LUG, not to the base's piers.** Both fix the sliding; only one keeps the bridge removable. The lug is a closed bore around the pin, so a pin fixed in the base's piers captures the deck permanently — and lifting the bridge straight up, for painting, is a property this part was deliberately designed to have (see `_base_of`, on slotting the bores upward). Fixed to the lug instead, pin and deck become one piece that still drops in, still turns in the pier bores, and cannot migrate because the lug is trapped between the piers with 0.4 mm of end float. Keep the adhesive off the ends of the pin, which is where it runs in the piers.


### Chains on, and the pin stops being a problem

Chains fitted, holding the drawbridge **slightly raised** — a small lift, not a dramatic one. Two things settled at once.

**The prediction held, and the small lift is enough.** A fixed-length chain cannot be taut with the bridge up *and* permit lowering, so the spec accepted that it would stop the bridge short of vertical and argued that is what a real drawbridge looks like. It does. Charles: the chains hold it slightly up, "which is sufficient to illustrate the mechanics and look realistic."

That is the whole answer to the post-height question, and it is worth being precise about the degree: the bridge sits **slightly** off the ground, not half-raised. Anyone reading this later and expecting to see it standing at forty-five degrees will think something is wrong. Nothing is. A few degrees of lift is all it takes to read as a mechanism rather than as a plank, because what sells it is the chain being taut and the deck being off its seat — not how far it has travelled.

**And the pin no longer walks out** — the chain tension binds it in its bores. Good outcome, no reprint, but recorded in `notes.md` rather than ticked off, because **the thing doing the retaining is outside the model**: it lapses the moment the chains come off, and it must not be read as a reason to tighten `hinge_clear`, which is correct at 0.4 mm and was verified free before the chains went on.

Still unmeasured: link size and chain length. Worth taking, since `chain_up` and `chain_down` are reported by every build precisely so real chain can be checked against them.


### Tore on the first layer again, and again it was the plate

Aborted on the first layer for the second time. Every first-layer-relevant setting in the `.3mf` was checked against the resolved `0.20mm Standard @BBL A1M` profile and **matched stock exactly** — speed, flow, bed temperature, elephant foot, skirt, brim, bottom pattern. There was no misconfiguration to find. A fresh wash with Ajax fixed it, as it did in August.

**The finding is not the cause, it is that the cause is invisible.** Charles: "It's just hard to look at the plate and see that it needs that in advance." Both aborts were preceded by looking at the plate and judging it fine. A plate carrying enough contamination to tear a 251 cm² slab is indistinguishable by eye from one that is not, so any procedure that begins "check whether the plate needs washing" will keep failing — the check cannot return the right answer.

So `SLICING.md` now carries it as a **precondition rather than a diagnosis**: wash before slicing a large flat-bottomed part, unconditionally, without looking. Two minutes against several hours, on a part that has now spent two first layers proving it.

**The reprint after the wash completed clean.** Two aborts and one good print, with no setting changed between any of them — which is the strongest form the finding could take: the variable was never in the slicer.
