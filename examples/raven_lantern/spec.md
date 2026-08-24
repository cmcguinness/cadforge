---
project: halloween_lantern
stage: done
---

# raven_lantern

First of the Halloween lantern set. Black filament, ravens cut through the wall, the word *Nevermore* beneath them. Shares its body with the rest of the set via the `halloween_lantern` project; only the motif is its own.

## What it is for

A battery LED tea light in a black cylinder, standing on a table through October as ambient decoration. Picked up occasionally to swap the puck or the paper liner. Lit, it should read as a raven — a bird, recognisably, from across the room — with a word under it that a person can actually read. Unlit, in daylight, it should still read as a deliberate object rather than a cylinder full of holes.

It is one of a small set. The others carry different motifs on the same body, so a shelf of them looks like a collection and any puck fits any lantern.

## Constraints

**Fixed by the world**

- **The puck is opaque for its whole lower half.** It is a flame-style LED tea light: an opaque base of battery and electronics, with a narrow translucent flame standing on top, the LED inside the lower part of that flame. So the light comes from a short thin column partway up, not from the puck's top face and not from the puck at all below the flame. **An opening in the opaque zone is not a lit raven, it is a dark hole with grey plastic behind it.** This is the single fact the design turns on, and it is a hard floor: no other choice recovers it.
- All puck dimensions are `measured` (calipers) — base diameter and height, LED height, full flame height, flame diameter. They live in the `halloween_lantern` project and are shared by the whole set. This replaces the never-measured nominal figures `tealight_holder` was built on, which were also the wrong *shape* of fact: that part assumed a flat emitting top face.
- **A rolled paper liner is part of the design, not an accessory**, and it does more than soften a hot spot. The flame is close to a line source; the paper intercepts it and re-emits over its whole surface, turning it into a lit column. **That is what evens out height variation**, and it is why the ceiling on the motif band is soft where the floor is hard — confirmed in the hand on `tealight_holder`. It shares the puck's fit clearance, so that clearance is spoken for.
- **Black PLA is effectively opaque.** Light escapes through openings or not at all; there is no thin-wall glow to fall back on. Every lit element must be a hole.
- A cylinder is a developable surface but a **letter is not left–right symmetric**. The `tealight_holder` trick of extruding one cutter both ways to pierce near and far wall at once is safe for a heart and *wrong* for text — it would mirror the word onto the back.

**Fixed by the process**

- Prints upright on its base, in the configured material, no supports.
- Openings must self-support: the top of every hole bridges, the bottom converges or is shallow enough to hold.
- Fits the configured bed with room for several on one plate — this is a set, and printing them one at a time is a real cost.

**Fixed by taste**

- A lantern, not a colander. Solid black material is what makes the lit shapes read; if too much wall is removed the object stops having a silhouette.
- A solid rim top and bottom, so it does not read as a row of broken arches.
- Ravens read as ravens head-on and foreshorten naturally as they wrap. That is the accepted behaviour of a cylinder, not a defect.
- The word is the punchline. It should sit where a person looking at the front of the lantern finds it without turning the object.

## Acceptance criteria

### Does it do its job?

- [x] **The raven reads as a bird**, not an ambiguous blob — recognisable silhouette with a distinguishable head, beak and tail. Read this off the front elevation of the render sheet.
- [x] **The word reads as *Nevermore*** from the front, in one view, without rotating the lantern. Not merely present — legible.
- [x] **Every opening — bird and letter alike — sits entirely above the puck's opaque base.** Nothing is backed by opaque plastic. This is the hard floor; assertable, and must be asserted.
- [x] **The motif is centred on the lit window rather than merely clearing it.** Reaching well above the flame is acceptable — the paper liner re-emits and evens out the falloff — but the design should not spend its canvas drifting upward for no reason.
- [x] **No text appears mirrored anywhere on the part.** If the word is visible on more than one face of the wall, every instance reads left-to-right.
- [x] **The pierced fraction of the motif band stays within bounds** — enough removed that it lights, enough left that it still reads as a black object. Derive the open-area fraction and assert it.
- [x] **The puck can be retrieved by hand** without tipping the lantern over. `tealight_holder` lost this by raising its band and nothing in the model complained; do not repeat that silently.
- [x] **A rolled paper liner can be fitted and removed** — the well is reachable and the clearance admits puck plus paper together. Settled by the second print, and it settled something else at the same time: the liner rolls up *inside* the interior strings and backlights them. See prints.md.
- [x] **It belongs to the set:** footprint, height and standoff come from the shared envelope, not from local numbers.

### Is it built correctly?

- [x] **One connected solid.** No loose glyph counters, no detached ravens.
- [x] **Every letter counter is bridged to the surrounding wall** — the middles of O, E, A, R survive as part of the body. Assert the expected count of pierced regions; a stencil font that silently lost a bridge still builds.
- [x] **Material between adjacent openings exceeds the minimum**, both between ravens and between letters, which is the tighter case.
- [x] Solid rim above the motif band and solid wall below it; the band clears both the floor and the top.
- [x] Fits the configured bed; no unsupported planar overhangs in the print pose.
- [x] `PRINT_ROTATION` is stated, and the overhang check is run in that pose.

### Only a print can settle these

- [x] **It reads as a raven at night, lit, across a room.** The render can show the silhouette; it cannot show what the eye does with a small bright shape in a dark room.
- [x] Whether the paper liner actually stays put behind a band of small openings, or shows through them as visible paper.

## Open questions

- **How far above the flame the liner keeps things usefully lit.** The floor is hard and measured; the ceiling is soft and has only ever been established by "the old one worked". If a lantern is ever built noticeably taller than this set, that is the number that stops being free.
- Paper liner thickness is still `nominal` — it eats into the same clearance as the puck, so it is worth a caliper before that clearance is ever tightened.
- Which stencil typeface, and whether its bridges survive at the size the word has to be. A stencil face solves the counter problem by construction; the alternative is adding bridges by hand, which is fiddly and font-specific.
- How ravens and word compose: a ring of ravens with the word below them, one large raven on the front with the word beneath, or the word wrapped as a band. Undecided on purpose — this is what the first renders are for.
- ~~Whether the word wrapped on a cylinder is legible enough at all.~~ **Settled, as a preference rather than a compromise:** the word runs far enough round that no single viewpoint holds all of it, and that is wanted — it invites picking the lantern up and turning it. Do not "fix" this by shrinking the text.
- Whether the set should share a print orientation and plate layout, given several will be printed together.
