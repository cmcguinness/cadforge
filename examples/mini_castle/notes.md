# mini_castle — notes

Why the numbers are what they are. Never restate a dimension here; name the symbol and explain the reasoning that is invisible in the source.

## Why this part exists at all

The full-size castle gives each storey its own puck. At half size none of them can take one, and the reason is worth stating precisely because it is not the one you would guess: **the binding constraint is height, not footprint.**

The ground floor halves to a 61.6 × 41.0 mm floor, which accepts a 35 mm puck with 6 mm to spare in the tighter direction. Its clear height halves to 22.6 mm against a puck 30 mm tall to the flame tip. Width and depth were never the problem. Merging the three chambers into one column gives 59.6 mm of height and the puck simply drops in.

This is the general lesson the repo keeps relearning in different clothes: **derive the quantity that actually matters and check that, not the inputs.** "Is it big enough at 50%?" has no answer; "is any single dimension short?" does.

## The puck does not scale, and that is the whole design tension

Everything else here halves. The tea light does not: 35 mm across, **15 mm of opaque base**, LED to 25, flame tip at 30, whatever size the castle is.

So the fraction of the lit storey that is blocked by the puck's own body doubles when the castle halves — from 33% at full size to **66% here**. The emitting band lands opposite the *top* of the face storey and the *bottom* of the bat window.

The predicted consequence was: eyes light well, the bat window does better than it has any right to because it sits directly opposite the LED, the mouth darkens from its threshold upward, and the top turret is ambient rather than lit.

**The object answered a better question instead.** The design intent was an upright puck on the floor, as above. At the bench it was laid **on its side**, flame horizontal and aimed at the openings, because that lit the castle better. See `prints.md`. Lying down it is a directional source at roughly z 18 mm — mid-face-storey — and its opaque base is beside the flame rather than under it, so the 66% figure describes a configuration the winning version does not use.

The 66% reasoning is not wrong; it is simply about a configuration that turned out not to be the good one. Keep it, because it still governs the upright case and the upright case is still what a future scaled variant would reach for first.

## Puck orientation is a design variable, and the set never noticed

This is the finding worth keeping, and it is not specific to this part.

`projects/halloween_lantern/shared.py` documents its heights as "measured from the surface the puck stands on", and every part in this repo inherits that assumption without ever stating it as a choice. A puck has two usable orientations and they behave completely differently:

| | upright | on its side |
|---|---|---|
| emitter | vertical column, floor + 15 to floor + 30 | point at ~z 18, on the cylinder axis |
| directionality | roughly omnidirectional | **aimed** — a cone at the wall it faces |
| the opaque base | a plinth blocking everything below it | beside the flame, blocking almost nothing |
| suits | a lantern about as tall as its puck | one opening, or one storey, wanted bright |

For the lantern set the upright assumption is right: those bodies are barely taller than the puck and want light all round. For a tall object with a face on one side, laying the puck down is *better* — it spends all the light on the thing that matters instead of spreading it over storeys nobody looks at.

Neither is the answer here yet. What is settled is that the question exists, that it is free to test, and that any future part which is much taller than its light source should decide it deliberately rather than inheriting it.

If the mouth turns out to be fatal, the fixes in rough order of cost are: raise `scale` until the gate clears 15 mm; shorten the gate so it stops running to the floor; or abandon the flame puck for a flat-bodied LED. The last one breaks the set's shared `PUCK` and should stay a last resort.

## Removing the floors is a printability win, not just a lighting one

Planar overhang faces fell from **137 to 3**. The slabs *were* the large flat ceilings, and those ceilings are what needed the tree supports whose collapse killed the first full-size print. Taking them out removes the problem rather than solving it.

The remaining large face (344 mm²) is the footing ring left under the walls where the slab used to be. It is internal and invisible, so support scars there cost nothing.

## `y0` is a tier line, not an inside face

**The bug this part shipped and then fixed within the hour.** The slab cutters were built from each `Chamber`, and `Chamber.x0`/`x1` are the chamber *interior* while `Chamber.y0` is the **tier line** — the outside of the storey's front wall. Taking `y0` as a starting point therefore cut a horizontal slot clean through that wall over the slab's whole z band: 6.4 mm tall at the second storey, 4.4 mm at the turret, both at exactly the wall-walk level. Lit, light escaped forward onto the walkway from behind the battlements. It was spotted on a render.

Two things worth carrying:

- **The asymmetry is invisible at the call site.** `s.x0` and `s.y0` read like the same kind of thing and are not. That is now stated in `_slab_cutter`'s docstring, because a comment at the definition is the only place it can be seen.
- **Every generic check passed.** The part was one solid, watertight, the bounding box was exactly the castle's at half scale, no islands. A slot through an internal wall changes none of those. It is the repo's signature failure — geometry sized from one constraint and never checked against its surroundings — and the only thing that catches it is an assertion that probes the *specific* surface that should still be there. `check()` now does.

## Why this is a transformation and not a redesign

`model.py` loads the castle's module and subtracts two boxes. It is deliberately not a copy: the castle is still being refined, and a fork would have to be re-merged by hand every time. `model.py` is disposable here in the strongest sense the repo means it — the geometry lives next door and this file is only the difference.

The cost is that this part inherits the castle's bugs and its fixes without asking. That is the right trade while it stays a scaled variant. The moment it wants proportions of its own — a taller ground floor to lift the face out of the puck's shadow, say — it has stopped being a variant and should become its own part with its own model.

## The paper templates live next door

Cutting outlines for both diffusers are on one page at `castle/templates/paper-diffuser-templates.pdf`, which carries this part's at 0.5x alongside the full-size ones. Generated by `castle/paper_templates.py` from `castle`'s openings, for the same reason this file's geometry comes from there: this part is that part scaled, and a second copy of the outlines would be a second thing to keep in step.

**"First floor" and "second floor" name the elevation here, not structure.** This part has no internal slabs — the storeys are inferred from the facade — so the two sheets are simply the two groups of openings, the same two as full size.
