---
project: halloween_lantern
stage: done
---

# witch_lantern

Second of the Halloween lantern set. Black filament. A ring of witch heads in profile — pointed hat, hooked nose, streaming hair — cut clean through the wall.

Body, height, bore and the motif datum come from the `halloween_lantern` project and are not this part's to choose. Only the motif is its own.

*(This spec replaced an earlier moon-and-flying-witch design, which was abandoned because its artwork could not survive being made this small. See notes.md — the reason is more useful than the design was.)*

## What it is for

The same object as `raven_lantern` and used the same way: a battery LED tea light in a black cylinder on a table through October, picked up occasionally to swap the puck or the paper liner.

Lit, the heads should read as witches at a glance — from across a room, without anyone being told what they are. Unlit, in daylight, the lantern should read as a deliberate object rather than a cylinder full of holes.

## Constraints

**Fixed by the world**

- **The puck is opaque for its whole lower half.** A flame-style LED tea light: an opaque base with a narrow translucent flame on top and the LED inside the lower part of that flame. An opening in the opaque zone is not a lit witch, it is a dark hole with grey plastic behind it. Hard floor; no design choice recovers it.
- All puck dimensions are `measured` and live in the project's `shared.py`.
- **A rolled paper liner is part of the design, not an accessory.** It turns a near-line source into a lit column. It shares the bore clearance, so that clearance is spoken for. **Anything on the inner wall is visible in use** — the liner rolls up *inside* stray material and backlights it rather than hiding it, which `raven_lantern` established the hard way.
- **Black PLA is effectively opaque.** Every lit element must be a hole.

**Fixed by the set** — from the project, not negotiable here:

- Overall height is fixed, and the top of the motif hangs a fixed distance below the rim so motifs line up across a shelf. A motif that will not fit in the lit wall below that datum is a build failure, not a taller lantern.
- Bore, wall and standoff are shared, so any puck fits any lantern.
- **No supports.** A hard requirement of the set; see the project's project.md for what it cost to learn.

**Fixed by the process**

- Prints upright on its base. Every opening is in a vertical wall and must bridge across its own top the way a circular hole does.
- The motif is a **cutout**, so its thin features are thin *slots*. A slot under one nozzle diameter is not omitted cleanly — the slicer fills it with ragged gap-fill.
- **Each opening is a gap the nozzle must jump on every layer of the band**, and that is where `raven_lantern`'s stringing came from. Opening count is a printability parameter, not only a compositional one.

**Fixed by taste**

- A lantern, not a colander.
- The heads read as a ring, evenly spaced, all facing the same way.
- It should look like a sibling of `raven_lantern` on a shelf.

## Acceptance criteria

### Does it do its job?

- [x] **It reads as a witch's head** — pointed hat, brim, hooked nose and chin all identifiable in the silhouette, without prompting.
- [x] **It reads at the size it is actually printed**, not when enlarged. Judge this from a true-scale two-tone flat, never from a magnified view: the previous motif was approved at 5× and failed at 1×.
- [x] **The motif reads from its outer contour alone.** No interior gap does the recognition work. This is what makes it viable at this size at all, and giving it up would repeat the mistake this part has already made once.
- [x] **Every opening sits entirely above the puck's opaque base.** Hard floor; assertable, and must be asserted.
- [x] **Nothing in the motif is narrower than the nozzle** at the size in use. Judged by simulating the nozzle against the artwork, not by a percentile of feature widths — tapered points make that number meaningless.
- [x] **The lantern reads as a black object**, not a cage: the pierced fraction of the outer wall stays within bounds at both ends.
- [x] **The puck can be retrieved by hand** — reach in, pinch the flame, pull.
- [x] **It belongs to the set:** height, bore, wall and motif datum all come from the project.

### Is it built correctly?

- [x] **One connected solid.**
- [x] Heads are evenly spaced, and the material between adjacent ones exceeds the minimum.
- [x] Solid rim above the motif and solid wall below it.
- [x] Every head faces the same way — the motif is handed, so a cutter extruded both ways would mirror it onto the far wall.
- [x] Fits the configured bed; no unsupported planar overhangs in the print pose.
- [x] `PRINT_ROTATION` is stated, and the overhang check is run in that pose.

### Only a print can settle these

- [x] **Supports, if used, come off without damaging the motif.** Revised from "the slicer asks for no supports" — that was over-generalised from the lettering failure. Settled: printed with supports, removed clean.
- [x] **It reads as a witch at night, lit, across a room.**
- [x] Stringing across the openings is acceptable at the project's 210 °C.
- [x] The hair tendrils and the hat point survive as openings rather than filling in.

## Open questions

- ~~How many heads.~~ **Settled: five**, judged from a true-scale flat rather than a magnified one. 10.4 mm ribs, comfortably over the minimum, and fewer nozzle jumps per layer than six.
- Whether the hair tendrils read as hair or as noise once lit.
