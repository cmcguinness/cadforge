# owl — print log

One entry per physical print. This closes the outer loop: the renders and the checks can only judge geometry, and everything else is discovered here.

Record a print even when it succeeds. A design that works and nobody wrote down *why* it works is one refinement away from losing the property by accident.

## Iteration #6 (`897cfde5`) — accepted

- **Settings:** black PLA, two pieces, plate exported lying flat. Layer height, supports and slicer profile were not recorded at the time.
- **Result:** reads as an owl immediately and unprompted — ear tufts, feathered contour, and a stare that lands as menacing rather than startled. Three apertures, clean edges, no stringing. The joint does not read as a joint from the front and the shelf is not visible. **Verdict: good, and the part is done.**

### The diffuser paper can be coloured, and that is a new degree of freedom

Paper went behind the eyes and the beak, **affixed with a glue stick**, and the eyes were then coloured with a **green art marker**. This is worth writing down as a technique rather than as a detail of this print: **colour is a finishing variable that costs nothing at print time and adds detail no geometry can.** A single-colour part in black PLA can carry a two-colour face without a multi-material printer, an AMS, or a second piece — the aperture decides the shape, the paper decides the brightness, and the marker decides the hue. Three independent knobs on one hole.

**Glue stick is the right adhesive and that is now confirmed rather than assumed.** It goes on dry enough not to cockle the paper, gives enough working time to position a small patch over an aperture, does not bleed through and dull the tint, and leaves nothing glossy where light passes. It also releases if the paper needs replacing, which matters on a part where the paper is the thing most likely to be revised. `castle`'s spec already specified glue-stick and printer paper as the intended method; this is the print that establishes it works.

Two consequences worth knowing before using it:

- **Colouring attenuates.** A tinted aperture passes less light than a plain one, so tinting is also a *brightness* control and it competes with whatever the geometry was doing. Here the eyes are tinted and the beak is not, which pushes against this part's primary criterion — that the eyes are the brightest thing and the beak is subordinate. It came out fine by eye, but the margin is narrower than the model believes.
- **Marker on paper goes on unevenly.** At full resolution the green is visibly streaked, with thin and thick patches. Unlit that reads as texture and is arguably an asset. Backlit it is amplified, because a thin patch transmits more. If an even field is wanted, a second coat from the back or coloured tissue in place of marker both fix it.

### The puck was laid on its side, and the geometry survived by luck

The tea light was **mounted on its side, aimed at the back of the plate, held with small rolls of tape sticky side out.** That is the same field modification `mini_castle` made, down to the tape — see its `prints.md`, which established that puck orientation is a design variable nothing in the model knows about.

This part was designed around an **upright** puck:

```
shelf                    73.95
opaque base top          88.95
LED band          88.95 – 98.95
eye centre               93.95   ← dead centre of the band
```

Laid down, the flame stops being a 10 mm column standing on a 15 mm plinth and becomes a roughly point source on the cylinder axis, `dia / 2` above the shelf, radiating sideways:

```
flame axis    73.95 + 17.5 = 91.45   ← 2.5 mm below eye centre
```

**The eyes got away with it.** 91.45 still falls inside the 88.95–98.95 band the shelf was derived to hit, just low of centre.

**The beak did not, in principle.** The whole reason the beak was expected to stay subordinate is a 15 mm opaque base sitting *underneath* the flame and shadowing everything below it. On its side that base is beside the flame, not under it, and shadows nothing — exactly the mechanism that made `mini_castle`'s gate the brightest thing on the object. It was judged acceptable here by eye, so this is a note about a justification that no longer holds rather than a fault that appeared.

**So `shelf = eye_centre − (opaque_h + emit_top)/2` is now measuring the wrong axis.** The assertion still passes and the number it produces still works, but the theory behind it describes a puck in an orientation this print did not use. That is the dangerous kind of correct: right answer, wrong reason, and it will stop being the right answer the moment anything moves.

If the sideways orientation is ever designed in rather than improvised, two things follow and both are cheap:

- **The shelf wants `eye_z − dia/2` = 76.45**, 2.5 mm above where it sits, to put the flame axis on the eye centre instead of below it.
- **The tape rolls are describing the feature they want.** `mini_castle` already worked its shape out: two low ribs running front-to-back either side of the contact line, spaced a little under the puck diameter apart. Lateral stops at the tangent, not a saddle wrapping the cylinder — no overhang, no bridging, nothing that complicates the print. Right now the aim is set by hand every time and nothing holds the flame at the height that worked.

### The joint does not need glue

**The owl rests in the branch's slot under its own weight and stays put.** It was never glued, and nothing about the assembly asks for it.

The slot's clearance was chosen *as a glue gap* — the spec's reasoning is that a tight slot in PLA either will not assemble or splits the branch, so leave room for adhesive. That reasoning produced the right number for the wrong reason: the same clearance turns out to seat the plate well enough that gravity alone holds it, and the glue it was making room for is unnecessary.

Three things follow:

- **The criterion about whether the glued joint survives being carried by the owl is answered by deletion.** There is no glued joint to survive. It is replaced by a different and much less alarming question: lift the ornament by the owl and the branch stays on the table. That is a handling habit, not a failure mode, and it is obvious the first time anyone does it.
- **It disassembles**, which is a real gain nobody designed for. The plate stores and travels flat, and the two pieces pack smaller than the assembled ornament.
- **Do not tighten the slot to make it grip harder.** The seat works; a snugger one buys nothing and risks the split the clearance exists to prevent. The lantern set already paid for the general form of this mistake once, tightening `fit` to cure a rattle and ending up with a bore a puck would not enter.

## Iteration #7 — the sleeve got twice as tall, and that is what fixed the side leak

- **Settings:** as iteration #6 — black PLA, plate flat, branch upright. The new piece is a `tealight_sleeve` printed at **double length**, made by scaling the shipped 15 mm STL 200% in Z in the slicer. Z-only scaling leaves bore and wall untouched, so the printed object is 36.0 mm bore, 0.8 mm wall, 30.0 mm long — dimensionally identical to the sleeve now in `pieces()`.
- **Result:** the puck lies inside it on the shelf, and **the light that used to spill sideways off the shelf is gone.** Charles: "This allowed me to hide the light leaking from the side so it didn't distract the viewer." Light still escapes rearward, which nobody minds — you have to stand behind the ornament to see it, and at that point you are not looking at the owl anyway.
- **Verdict: good.** The sleeve is now a third piece of this part rather than a field modification.

### Why a sleeve that shrouds the flame is right here and wrong in `tealight_sleeve`

`tealight_sleeve` spends three paragraphs establishing that the sleeve **wraps the base, not the flame**, and asserts its length equals `PUCK.opaque_h` in both directions. This part asserts the opposite bound — `sleeve_len == PUCK.flame_top` — and both are correct, because the two parts are doing opposite jobs with the same shape.

The difference is the puck's orientation, which is the same fact `shared.py` warns about and `mini_castle` found by accident. Upright, the sleeve's walls stand **over** the flame, and everything they cover is light taken away from whatever the puck is meant to light. On its side, aimed forward at the owl's back, the walls stand **beside** the flame: they block the sideways light and pass all of the forward light unobstructed. Shrouding is the whole function rather than the failure mode.

So the rule to carry forward is not "sleeves stop at the base" but **a sleeve's length is decided by which way the puck points**. Upright, it is a chock and stops at the base. On its side it is a snoot and runs the whole length of the puck.

### "Double tall" and "the whole puck" are the same number by coincidence, and only one of them is a reason

`2 × opaque_h = 30.0` and `flame_top = 30.0`. The doubling is how the number was arrived at in the slicer; the puck's overall height is why it is the right number. `model.py` carries the second, because it is the one that survives the puck being re-measured — if a future puck has a taller flame, "double" stops shrouding it and `flame_top` does not.

### What the sleeve costs, and the two things now asserted because of it

- **It lifts the flame axis 1.3 mm.** A bare puck rests on its own cylinder, axis at `dia/2` above the shelf; sleeved, it rests on a 0.8 mm wall and sits centred in a 36 mm bore, so the axis is at `wall + bore/2` = 18.8 instead of 17.5. Measured against the shelf floor's **top face** the numbers are 95.15 mm sleeved against 93.85 bare, with the eyes spanning 88.5–99.4 and centred at 93.95. Both are comfortably inside the eyes; the sleeved one is 1.2 mm high of centre where the bare one was 0.1 mm low. Asserted, because it is the kind of small penalty that is fine at 140 mm and not fine at some other size.
- **It is 37.6 mm across, so lying down it stands 37.6 mm tall** — 14.6 mm above the top of the eyes and far above the 3 mm shelf rim. "The shelf is not visible from the front" therefore stopped being a statement about the shelf. The owl's silhouette is at least ±32.5 mm wide everywhere the sleeve occupies, so it hides it completely, but that is a property of the traced outline at this size rather than of anything designed. Asserted by walking the silhouette at 1 mm steps over the sleeve's full height.

### A 2.4 mm error in the LED-band derivation, found while positioning the sleeve and deliberately not fixed

`shelf_z` is where the shelf's floor slab **begins**; a puck on the shelf rests on the slab's **top**, `shelf_t` = 2.4 mm higher. `geometry()` derives `led_lo` and `led_hi` from `shelf_z`, so for an **upright** puck every one of those heights is 2.4 mm low, and the coverage assertion is checking a band the puck does not occupy.

It changes nothing about this object — the puck lies down, and the sideways case is measured from `floor_top`, which is now a named field precisely so nothing else picks up the wrong datum. It is left alone rather than corrected because correcting it would move `shelf_z` on a part that is printed, accepted and works, to improve a case this part does not use. Recorded here so that the next person to read that derivation does not spend the evening re-deriving it and concluding it is right.

**It also makes iteration #6's arithmetic above wrong, and by the same 2.4 mm.** That entry puts the bare sideways flame axis at 91.45 mm and calls it 2.5 mm below the eye centre; measured from the floor's top face it is 93.85, which is 0.1 mm below centre — the sideways puck was very nearly perfect and nobody knew. Its recommendation to raise the shelf to 76.45 would therefore have *broken* a correct alignment. Do not act on it.

## Template for an entry

### YYYY-MM-DD — iteration #N (`<params digest>`)

- **Settings:** material, layer height, supports, orientation on the plate.
- **Result:** what came out.
- **Measured vs. modeled:** the numbers that differed, and by how much. This is what turns a `nominal` constraint in spec.md into a `measured` one.
- **Verdict:** and then run `cad accept <part> good|bad|mixed "<why>"` so the iteration history carries it too.

### Photographed lit, and turned all the way round

`finished_owl_lit.jpg` plus a 360° turn (`videos/finished_owl.mov`, reduced to `finished_owl.gif`). The existing `finished_owl.jpg` is the daylight shot; both are in the README, because they answer different questions.

**Lit, the eyes read as green crescents — but the silhouette is carrying more of the load than expected.** The ear tufts, the feathered edge and the branch are all legible against the wall behind, so the object reads as an owl *and* as a face, not as three holes floating in the dark. That is worth stating precisely, because the reverse was written here first and the photograph does not support it: a backlit silhouette part still needs a room with something behind it. Against true black the outline would go and only the apertures would remain, which is a different and much weaker object. The place it sits is part of the design.

**The turn confirms the puck lies on its side on the shelf**, aimed forward, and that the entire rear of the plate is featureless black. Worth having on record: this part's shelf height was derived for an *upright* puck, and the photograph of the accepted object shows a sideways one. The number is right and its premise is dead — already noted above, now visible.
