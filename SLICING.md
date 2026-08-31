# Slicing

Settings that are not in `printer.toml`, and why.

**Nothing in `cadkit` reads this file.** `printer.toml` holds the values the code consumes — bed, nozzle, layer height, overhang limit, density. What follows is the other half: settings a person types into the slicer, which the harness cannot see and cannot check. They are written down because otherwise they are rediscovered one failed print at a time.

Every entry carries the evidence that produced it. A setting with no reason attached gets "tidied away" by the next person.

## Organised by scope, because it matters

A finding that is really about the *machine* will be re-derived on every project if it is filed under one. Conversely a geometry-specific setting applied everywhere is cargo cult.

---

## Machine — the A1 mini, any part, any filament

- **Flow dynamics calibrates automatically at print start.** It is not a knob. Time spent tuning pressure advance here is wasted; the printer has already done it.

- **Monotonic top surface and "no ironing" are already the stock defaults.** Not a knob either, and worth knowing before hunting for it: `0.08mm Extra Fine @BBL A1M` resolves to `top_surface_pattern = monotonicline`, `bottom_surface_pattern = monotonic` and `ironing_type = no ironing`, all inherited from `fdm_process_common`. A lithophane recipe that lists them reads like three settings to change and is really zero.

  Read the resolved values rather than the profile you selected — the value is almost never in that file. Walk `inherits` in `~/Library/Application Support/BambuStudio/system/BBL/process/*.json`, child first, first definition wins. `0.08mm Extra Fine @BBL A1M` → `fdm_process_single_0.08` → `fdm_process_single_common` → `fdm_process_common`, and everything above was set in the last of those.

  To see it in the UI: **Process → Strength → "Top/bottom shells" → Top surface pattern** (Bambu Studio 02.07.01). Options are Concentric / Rectilinear / Monotonic / Monotonic line / Aligned Rectilinear / Hilbert Curve / Archimedean Chords / Octagram Spiral. The Strength page's groups run *Walls*, *Top/bottom shells*, *Infill*, *Advanced*.

  What that profile does NOT already give you: `sparse_infill_density` is 15% and a lithophane needs 100% — **Process → Strength → Infill**, one group below. Both settings are on the same screen.

- **To find where a setting lives, read the binary, not the forums.** On macOS the binary is inside `BambuStudio.app`, wherever it is installed. `strings -a Contents/MacOS/BambuStudio` contains two useful tables: the parameter definitions (key, label, tooltip, enum values, in `PrintConfig.cpp` order) and the wiki help-anchor list, which is emitted **in page and option-group order** and is what actually reveals which tab a setting is on. Searching for the group label alone is not enough — group names like "Shell" also exist as gizmo and icon names.

  The Process settings **search box** also works and searches print settings. It is the retraction travel threshold that it will not find, because that one is a *filament* override rather than a print setting.

## Material — PLA on this machine

- **Nozzle 210 °C, not 220.**

  The single change that settled stringing on `raven_lantern`, after travel routing and seam settings were already correct.

  **Try temperature first.** It costs one reslice. It had been ranked *fourth*, behind buying a filament dryer, on the reasoning that persistent stringing after retraction is configured usually means moisture. That reasoning was simply wrong for this machine, and acting on it would have cost $45 to find out. Moisture remains untested rather than disproven — a spool left open longer may still want drying.

## Geometry — parts with openings pierced through a vertical wall

Applies to any pierced wall, not only to lanterns. Both of these were diagnosed on `raven_lantern` and both are counter-intuitive.

- **`Scarf around entire wall` — ON.**

  The default `Smart scarf seam` only scarfs contours smoother than its 155° threshold, while `Seam position: Aligned` deliberately *seeks corners*. On a plain cylinder those agree. Through a band of openings the openings **create** corners, the seam snaps to them, the scarf is skipped there, and the stacked start/stop blobs become a visible bump partway up the wall — not at the bottom, not the full height, which is what makes it puzzling.

- **`Avoid crossing wall` — ON, max detour 100%.**

  Each opening splits the wall into separate perimeter islands, so the nozzle travels between them and the short path is straight across the open bore. That is where stringing comes from.

  **50% is not enough, and the arithmetic says why.** The detour is an arc where the crossing is a chord: for two points separated by angle θ the ratio is θ / (2·sin(θ/2)). Adjacent openings need +5%, two apart +21%, but a near-diametric travel needs **+57%**. At 50% the slicer routes around for short hops and gives up and crosses for exactly the long ones that string worst.

- **Opening count is a printability parameter.** No travel setting removes the need to jump a gap — at any layer through the motif band the wall is genuinely discontinuous at each opening. Six openings ≈ 17.6 mm wide meant twelve long jumps per layer. Fewer openings is less stringing, and that belongs in the design conversation rather than the slicer one.

## Geometry — parts with surface texture

- **`Remove small overhangs` — ON**, for anything with moulded texture. Mortar courses, tile courses and any shallow relief leave horizontal ledges a fraction of a millimetre wide, and a slicer's overhang test is angle-based, so a 90-degree face qualifies however small it is. Without this, a textured wall grows a support under every course, and they land on the SHOW SIDE.

- **It filters by AREA, not by span, and that catches people out.** A mortar bed and a tile course on a cone leave the same third-of-a-millimetre ledge, but the bed's face is a flat strip and the tile's is a ring — and a ring round a 15 mm turret is some 50 mm2 of face. The setting removed the walls' supports and left every roof course propped.

  The durable answer is in the model, not the slicer: **taper each groove shut at its head** so there is no horizontal face to find. See `castle/notes.md`.

## Geometry — parts whose first layer is one large solid face

`castle_base` is 158 × 159 mm and its underside is a **single flat 251 cm² face**. That is a different kind of first layer from anything else here — every other part is mostly perimeter with a bit of infill, and this one is a slab. Two consequences, both learned by aborting a print.

- **Tearing on a slab first layer means ADHESION, not squish.** The lines split and the nozzle drags through what it just laid, which looks exactly like a nozzle set too low — and reading it that way sends you to Z-offset and flow ratio, which is the wrong end of the machine. What is actually happening is that unstuck line gets picked up on the next pass. **Wash the plate first and re-run before touching anything else.** A freshly washed plate fixed it outright.

  The reason a slab exposes this when smaller parts do not: on a small footprint the perimeters and a bit of area are enough to hold even a marginal plate, and the failure mode when it is not enough is *lifting*, which is obvious. At 251 cm² of solid, every square millimetre is bearing surface and one contaminated patch anywhere in the middle tears rather than lifts. A slab has no tolerance for a plate that a small part would print on happily.

- **`Initial layer infill` is the speed that matters, not `Initial layer`.** For this footprint the first layer is roughly 0.6 m of perimeter against 60 m of infill — 97% of the path length. Slowing the wall speed changes nothing you can see. Set **Bottom surface pattern → Monotonic** while you are there; it is the most even option on a large flat bottom.

- **The part also reaches into the plate's outer band** — 158 mm on a 180 mm plate is 11 mm of margin, where the bed mesh is sparsest. Force a full mesh rather than letting it reuse the cached one.

## Supports

Not a prohibition. `cad build`'s **islands** check reports WARN, because the question is a decision and the harness should not make it:

| the support touches | verdict |
|---|---|
| features of a millimetre or more | fine — they come off clean |
| thin webs, single-extrusion ribs, anything holding a counter | reshape instead |

`raven_lantern` lost its lettering to support removal, and the cause was **not** supports: it was 0.5 mm single-extrusion webs sitting exactly where support material had to be pried out. The feature and the thing that killed it were the same feature. `witch_lantern` printed with supports on a hat brim and they came off with no damage.

The other half of the decision is **what surface the support touches**. On a lantern the inner wall is backlit through its own openings by the paper liner, so residue there is silhouetted rather than hidden. On a bracket nobody looks at it. Judge per part.

## Geometry — walls wide enough to hold sparse infill

**A wall wider than the perimeters can fill gets sparse infill inside it, and the nozzle will drag across that infill.** Heard on `moon_lightbox` as a buzzing on every travel, worsening with height. It is not a Z-offset problem and not a printer problem; it is geometry.

Two perimeters at a 0.42 line width fill 1.68 mm of wall. Anything past that becomes a sparse-infill channel between the perimeter skins. At 15% density in a narrow channel the lines are short and badly anchored — `infill_anchor` degrades to a one-sided anchor when it cannot find a suitable perimeter segment — so they curl above the nominal layer height. The nozzle then hits them.

**The slicer will not save you, and it is worth knowing exactly why**, because the protections look like they should apply:

- Z-hop is configured and would apply here — the A1 mini resolves `z_hop = 0.4`, `z_hop_types = Auto Lift`, `retract_lift_above = 0`, `retract_lift_below = 179`.
- But **Z-hop is triggered by retraction, and retraction is gated by `retraction_minimum_travel = 1` mm.** Infill-to-infill hops in a narrow channel are mostly under a millimetre, so they get neither retraction nor lift. The protection is switched off for precisely the moves that are the problem.
- **"Auto Lift" narrows it further.** It is conditional, not "always lift", and travel that stays inside the object is the case it is designed *not* to lift for — because normally there is nothing there to hit.
- **No slicer models curl.** It plans travel against nominal geometry and believes the previous layer's top is exactly at Z. The clearance it calculated was real in the model and absent on the plate.

So the slicer behaved correctly on the information it had. **Fix it in the geometry: keep the wall at or below what the perimeters fill.** For a 3 mm wall that is 4 wall loops (4 × 0.42 × 2 sides = 3.36 mm) — the part becomes entirely perimeters, no infill anywhere, and stiffer than 15% infill would have made it.

Reaching for `retraction_minimum_travel = 0` and forcing Normal Lift instead does work and costs thousands of extra retractions and the ooze that comes with them. It is treating the symptom.

**The modelling trap that produces this:** a wall is usually constant and nobody checks it. This one drifted from 1.07 mm to 6.57 mm because the outer shell and the cavity were tapered independently and were not parallel. Cavity dimensions were asserted — they are what the optics depend on — and wall thickness was not, because nothing depends on it until the printer does. `moon_lightbox`'s `check()` now sections the built solid at four heights and fails if the wall varies at all.

## Geometry — hollow parts with an open back

A part with internal chambers, reachable from one open side, has a support failure mode that a solid part does not.

**Turn `support on build plate only` OFF.** It sounds conservative and on this kind of geometry it is the opposite. Chamber floors are model material, so that setting forbids a support from *starting* on one — the slicer's only remaining route is to originate outside the footprint and lean the branches in through the open back. That converts a short column into a tall unbraced one:

| support stands on | free column, `castle` |
|---|---|
| the chamber floor it holds up | 45 / 36 / 32 mm |
| the build plate | 48 / **88** / 122 mm |

An eleven-hour print of `castle` was killed partway up the **first** floor when a tree headed for the **second**-floor slab collapsed — it fell inside the first third of the 88 mm column, long before reaching anything it was there to hold. Tall leaning supports do not fail at the top; they fail early, while they are still a thin unbraced stick. The reprint, **same mesh, nothing changed in the model**, was perfect.

The open back is what makes the failure possible: it leaves the interior reachable, so the slicer routes through it rather than refusing.

Alongside it, for the same class of part:

- **Tree branch angle 30°, not 45°** — branches lean less far from vertical. This is *not* the threshold angle: threshold decides which model faces get support at all, branch angle governs the support's own geometry.
- **Bottom shell layers 3 → 5**, so a chamber ceiling has solid material to resist the peel when supports come away. Check the slab thickness first — `castle`'s second floor is 2.4 mm, twelve layers, so 5 bottom + 3 top leaves four layers of infill and the slab is effectively solid.
- **Leave top Z distance at one layer** unless removal has actually proved difficult. A bigger gap releases more easily but sags more, and on a wide ceiling sag can curl into the nozzle. Change it when you have the problem.

### Then the feet let go — and the fix for that has a bill attached

Moving supports onto the chamber floors solved the collapse and created the next failure. A support that stands on the plate stands on glass; one that stands on a chamber floor stands on **a 2.4 mm PLA slab spanning a cavity**, which flexes under the nozzle. A later `castle` print was aborted when supports starting from the *second floor* came loose at their feet.

| supports stand on | free column | foot sits on |
|---|---|---|
| the build plate | 48 / **88** / 122 mm — topples | glass |
| the chamber floor it holds up | 45 / 36 / 32 mm | **a springy 2.4 mm slab** |

There is no third option, so the answer is to keep the short columns and fix the foot. Three settings do that, and **they are not redundant — they are a pair plus a bonding fix, and maxing all of them is how you get the failure after this one**:

- **`Bottom Z distance` 0.2 → 0** decides *whether* the foot welds to the slab. At the stock 0.2 every support standing on model material begins one full layer of air above it and holds on by squish alone. This is the one that matters.
- **`Branch diameter angle` 5° → 8–12°** decides *how much area* welds. Its tooltip is a description of the problem: branches "gradually become thicker towards the bottom… can increase stability". **It compounds over the column's whole length**, which is what catches people out — at 12° on a 36 mm column a 4 mm tip becomes a **19 mm** foot, five times the original footprint area.
- **`Independent support layer height` → OFF** is a *candidate*, not part of the working recipe. On by default; it lets support layers sit at Z values that do not line up with the object's, so the first layer landing on the slab can be a sliver even with the gap at zero. **It was never actually applied** — the `.3mf` of the print that worked has it still on — so it is untested here and the other two settings were sufficient without it.

**`Branch diameter` barely moves the foot — and doubles the ceiling contact.** Over a 36 mm column the taper dominates the foot completely: 2 → 4 mm moves it by 2 mm where the angle moves it by 13. But the tooltip is precise about what the number actually is — "the initial diameter of support **nodes**" — and that is the *tip*, the end touching the ceiling. So raising it buys nothing at the bottom and doubles the weld at the top. **Leave it at 2**, or at the 3 Bambu's own `support_recommended_params.json` asks for.

#### The bill: 0 gap × large feet = demolition

Run at `Bottom Z distance` 0 **and** 12°, `castle` printed perfectly and the supports had to be destroyed to get them out. That is the trade stated plainly:

| | supports stay put | supports come out |
|---|---|---|
| gap 0.2, small feet | ✗ came loose mid-print | ✓ |
| gap 0, 19 mm feet | ✓ printed clean | ✗ demolition |

**Pick one of the two to max, not both.** Zero gap is the more valuable of the pair because it is what actually stops the foot letting go, so keep it and take the angle back to **8°** — still roughly double the original foot area, with far less of it fused. Reserve 12° for a support that has actually failed at 8.

**The tops need dialling back too, and `Branch diameter` is why.** Every top-end setting was left at stock for the print that would not release — top gap 0.2, two interface layers at 0.5 spacing — so nothing at that end was changed. What changed was the branch *tip*: 2 → 4 mm doubled the stub welded to each ceiling. The setting that does nothing useful at the bottom is the one doing the damage at the top.

**Reach for `Top interface spacing` before `Top Z distance`.** Both ease removal and only one of them is free:

| lever | what it costs |
|---|---|
| `Top interface spacing` 0.5 → **0.8** | fewer interface lines welded to the ceiling. Geometry unchanged, so **no extra sag** |
| `Top Z distance` 0.2 → more | a bigger gap the ceiling sags across — and on a wide chamber ceiling sag can curl into the nozzle |

So the starting point for the next `castle`: **branch diameter angle 12° → 8°** for the feet, **branch diameter 4 → 2** for the ceilings. One change at each end, both of them reversions rather than new territory, and neither risks a fresh failure mode. Hold `Top interface spacing` at 0.5 in reserve — reach for it only if the ceilings are still stubborn once the tips are back to normal size.

The scars land on chamber floors, which nobody sees and which get paper laid over them anyway, so **removal damage is not the cost being weighed here — removal *effort* is**, and on an enclosed chamber reachable only through the open back that effort is the real limit. Check the sliced preview for feet that have **merged into a continuous mass**: separate fat feet are fine, a fused slab inside a chamber is not.

**The general lesson**: when a print fails, ask what the slicer was *forbidden* to do before you change geometry. The model was never at fault here.

## The .3mf is a deliverable — keep it in `accepted/`

**Never leave a saved slicer project in `build/`.** That directory is declared disposable and git-ignored, and a `.3mf` is the single most irreplaceable file a part has: plate position, support configuration and per-object tweaks that nothing in this repo regenerates. The settings inside were paid for in failed prints.

This is not a precaution, it is a post-mortem. Three `.3mf` files were kept in `build/`; **two are gone** — `castle`'s, carrying the support configuration that took two failed eleven-hour attempts to find, and `pumpkin_lantern`'s. `raven_lantern`'s survives only because a copy happened to sit in `slicer-profiles/`.

So: once a print is judged, **Save As** into `<part>/accepted/<part>.3mf`, which is tracked and published with the part. `cad accept` freezes any `.3mf` it finds in `build/` for the same reason, and `cad next` will nag for one on a printed part that has none.

And write the settings into this file as prose anyway, at the right scope. A file can be lost; two paragraphs in `SLICING.md` reproduce the print by hand. That is exactly what saved the castle.

## Saved profiles

`slicer-profiles/` holds Bambu Studio projects carrying these settings as artifacts rather than as prose. Open one and slice a different part in it rather than re-deriving the list.

- `raven_lantern.3mf` — the profile as printed, with the scarf and avoid-crossing settings above.

These are hand-made files and are the only copy. One was nearly deleted as "generated output" because it happened to be sitting in a `build/` directory.
