---
stage: done
---

# mini_castle

The castle at half size, hollowed into a single tall cavity so that one tea light can light the whole thing.

## What it is for

A small version of `castle` that **works as a lantern**, for a shelf, a mantel or a table where the full 178 mm object is too big. It sits beside the `halloween_lantern` set rather than replacing anything, and takes the same tea light every other lit part here takes.

The full-size castle gives each of its three storeys its own puck. This one cannot: at half size no chamber is tall enough. Removing the two internal slabs merges them into one column, and a single puck stands at the bottom of it.

## Constraints

- **The tea light does not scale.** `measured`, in `projects/halloween_lantern/shared.py`: 35.0 mm across, 15.0 mm of **opaque base**, LED to 25.0, flame tip at 30.0. Every clearance here is against those numbers and not against a fraction of them. This is the constraint that drives the whole part.
- **The binding dimension is height, not footprint.** At half size the ground floor is 61.6 × 41.0 mm, which accepts a 35 mm puck comfortably; its clear height is 22.6 mm against a puck 30 mm tall. That is the only reason the slabs come out.
- **Fixed by the process:** fits the configured bed; printed upright as modelled; supports allowed. The interior is invisible in use, so support scars inside cost nothing.
- **Fixed by taste:** it must still read as the same castle. This is `castle` scaled with two boxes subtracted, not a redesign — if it starts wanting bespoke proportions it has become a different part and should be one.

## Acceptance criteria

### Does it do its job?

- [x] **One tea light lights it.** A single puck, standing on the ground floor, inserted and removed through the open back by hand.
- [x] **The face still reads as a face** — eyes and mouth — lit, at room distance, to someone who was not told.
- [x] **The gate reads lit.** It does, brilliantly — it is the brightest thing on the object. The opaque-base worry this part was designed around assumed an upright puck; **the puck lies on its side by design**, so its base sits beside the flame rather than under the gate and never blocks it. See notes.md.
- [x] **The bat window lights.** It sits directly opposite the emitting band, so it should do better here than it has any right to.
- [x] **The top turret is deliberately dark.** The puck is aimed at the face, which is where this object's whole design lives, and spending light on a turret nobody looks at would cost the thing that works. An unlit window high on a haunted castle reads correctly. Same decision as the full-size castle's corner turrets.
- [x] **A clear column runs from the ground floor to the top turret ceiling**, wide enough and deep enough for the puck, with nothing left of either slab. Asserted.
- [x] **Removing the floors did not open the castle to the outside.** The exterior is the castle's, exactly, at half scale. Asserted on the bounding box.
- [x] **It is one connected solid.** A slab cutter that severed a wall would leave a plausible-looking castle in two pieces. Asserted.

### Is it built correctly?

- [x] Fits the configured bed in the pose it is exported in.
- [x] `PRINT_ROTATION` is stated, and the overhang check runs in that pose.
- [x] **Nothing is thinner than the nozzle can draw.** Halving puts the wall at 1.2 mm — three extrusion widths — and the gate's bars at 0.7 mm, which is under two. The bars are the risk and they are the reason this is a print criterion rather than an assertion.
- [x] **The exterior is `castle`'s**, unmodified apart from scale. Any divergence is a bug in the transformation, not a design choice.

### Only a print can settle these

- [x] **Whether the mouth reads lit.** The one that decides if this part is worth having.
- [x] **1.2 mm walls are stiff enough** with no internal floors. Settled by use rather than by measurement: the object has been handled repeatedly — puck fitted, chocks placed, paper glued behind two openings — and stands on a shelf without complaint.
- [x] **Whether the 0.7 mm gate bars survive printing** at all, or merge, or come out ragged.
- [x] **The interior prints cleanly.** Removing the slabs removed the large flat ceilings with them: 3 planar overhang faces against the full castle's 137. It came off the plate with no interior rework.

## Open questions

- **Should the puck lie on its side, by design?** The first lit print had it laid down at the bench because that distributed the light better, and it produced a brilliant face. Nothing in the model knows a puck can be turned over, so this arrived as a field modification.

  It needed a second one to stay put: rolls of electrical tape, sticky side out, either side of where the puck's rounded edge meets the floor. **That is the specification for the feature** — the constraint wanted is lateral, at the tangent line, not a socket the puck has to be threaded into. Two low ribs front-to-back, spaced a little under the puck's diameter, would hold it, fix its aim (a cylinder that cannot roll cannot turn its flame away), and keep insertion a matter of dropping it in through the open back.

  **Low priority.** The tape works, its positions are pencilled on the floor, and replacing a strip is barely harder than eyeballing it. Worth doing only if this part is opened up for some other reason.

- **Does the mouth survive the opaque base?** Predicted to darken from the threshold up through roughly two thirds of the face storey. If it is fatal, the fixes in rough order of cost are: raise the scale until the gate clears 15 mm; shorten the gate so it no longer runs to the floor; or use a flat-bodied LED instead of a flame puck — which would break the set's shared `PUCK` and should be the last resort.
- **Is 50% the right scale**, or is there a larger fraction that keeps the part small while lifting the face into the light? Nothing here is invested in 0.5 specifically; it is a parameter.
