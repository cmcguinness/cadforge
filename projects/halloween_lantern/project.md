# Halloween lanterns

A set of black-and-orange tea light lanterns for October: one cylinder body, one motif each, cut through the wall so the LED puck lights the shape.

Members declare themselves in `spec.md` front matter with `project: halloween_lantern`. The numbers they share live in `shared.py`.

## What is settled for the whole set

These are not per-part decisions. Changing one here changes every lantern, which is the point — and is why they are here rather than rediscovered in each part.

| | |
|---|---|
| **Height** | Fixed for every lantern. The rim is the datum. |
| **Motif datum** | The top of the cutouts sits a fixed distance below the rim, so motifs line up across a shelf however tall the artwork is. |
| **Bore** | Shared, so any puck fits any lantern. |
| **Material** | PLA, printed upright on the base, no supports. |
| **Diffuser** | A rolled paper liner is part of the design, not an accessory. |

### The paper is a finishing surface, not just a diffuser

Established on `owl` (see its `prints.md`) and applicable to anything here that puts paper behind an opening: **the paper can be glued and coloured, which gives a single-colour print a multi-colour face.** Glue stick affixes it without cockling, without bleeding through, and releases if the paper needs replacing; an art marker tints it. The aperture sets the shape, the paper sets the brightness, the marker sets the hue.

Two cautions. Tinting **attenuates**, so a coloured opening is dimmer than a plain one and colour is therefore also a brightness control competing with whatever the geometry intended. And marker on paper goes on unevenly — invisible unlit, amplified backlit, because a thin patch transmits more. Coloured tissue is the even alternative.

### The fact the whole set turns on

A flame-style LED tea light is **opaque for its whole lower half** — an opaque base with a narrow translucent flame standing on top and the LED inside the lower part of that flame. An opening below the top of that base is not a lit motif; it is a dark hole with grey plastic behind it.

That is a hard floor. The ceiling is soft, because the paper liner intercepts a near-line source and re-emits over its whole surface, turning it into a lit column. Height above the flame costs little; height below the base buys nothing.

The consequence is that **the lit canvas is short** — roughly the flame's own height — and it is the scarce dimension in every design here.

### Size is fixed by the candle, not by the artwork

The puck is not negotiable, so the canvas is what it is. Any conflict between what a motif wants and what fits is resolved by **changing the motif** — see `ARTWORK.md` at the repo root for how.

A larger LED candle would be a larger canvas, and that is a change to this file rather than to any part.

### Supports: allowed, and judged per motif

**Revised 2026-08-05, after printing `witch_lantern` with supports and having them come off cleanly with no damage.**

The rule here previously said "if a motif needs supports, reconsider the motif", generalised from one failure. That was too strong, and the generalisation was wrong in an instructive way.

`raven_lantern` lost its lettering to support removal — but the cause was not supports. It was **0.5 mm single-extrusion webs** holding glyph counters, sitting exactly where support material had to be pried out. The feature and the thing that killed it were the same feature. Supports were the occasion, not the cause.

Where the features a support touches are **robust** — millimetre-scale, anchored at both ends — removal is uneventful. The witch head proved that on a motif that `cad build` flagged with fifteen floating islands.

So the actual rule:

| the support touches | verdict |
|---|---|
| features of a millimetre or more | fine — use supports, they come off clean |
| thin webs, single-extrusion ribs, anything holding a counter | do not — reshape instead |

`cad build`'s **islands** check reports WARN rather than FAIL for exactly this reason: it surfaces the decision while the shape is still cheap to change. It does not make it.

Two things still worth checking on any supported print here, because they are specific to lanterns rather than general:

- **The inner wall is backlit** through the openings by the paper liner, so residue there is silhouetted rather than hidden. Inspect the bore before fitting the liner.
- Supports inside a motif have to come out **through** the motif.

## Slicing

The settings live in **`SLICING.md`** at the repo root, organised by scope — machine, material, and geometry — because almost none of what was learned here is actually about lanterns. "Avoid crossing wall at 100%" applies to any pierced vertical wall; "210 °C" applies to any part in this filament.

What IS specific to this set:

- **Interior finish is not free.** The paper liner rolls up *inside* any stray material on the bore and backlights it, so strings and support residue there are silhouetted rather than hidden. This is the opposite of the usual assumption and it decides the supports question for every lantern.
- **Opening count** is bounded below by how solid the lantern should read and above by stringing. Four to six.

## Open across the set

- **Why the bore printed undersize.** `fit` went 0.6 → 1.6 mm after a puck would not go in. Three candidates, undistinguished: an unmeasured lip on the puck, bores printing undersize on this machine, or 0.6 simply being optimistic. The middle one would be a fact about the machine and would belong somewhere more general than this project.
- **Paper liner thickness** is an upper bound ("under 0.2 mm"), never measured. It is consumed out of `fit`.
- **How far above the flame the liner keeps things usefully lit.** Established only by "the old one worked".
- **Rib strength with this much wall removed.** Carried as a print-only *criterion* on three lanterns for a while, which was a mistake: all three are printed and done and none of them was ever squeezed, so it sat unticked forever and made finished parts look unfinished. It is a question about the set — same wall, same material, same open-area fraction — and nothing will answer it until one of them is dropped or gripped hard. Moved here so it stops being a false debt against parts that are finished.

## The working slicer profile, as a file

`slicer-profile-raven_lantern.3mf` is a saved Bambu Studio project for the raven, carrying the settings above as an artifact rather than as prose — scarf seam, avoid-crossing-wall, temperature and all. Open it and slice a different lantern in it rather than re-deriving the profile from the list.

It was rescued from a `build/` directory during promotion, where it would have been deleted as generated output. It is not generated: a saved slicer project is a hand-made thing, and this is the only copy.
