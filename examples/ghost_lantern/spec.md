---
project: halloween_lantern
stage: done
---

# ghost_lantern

Third of the Halloween lantern set. A ring of ghosts standing in lit windows — **inverted polarity**: the ghost is the solid material and the window around it is the opening, so the ghost reads dark against a glowing field, with glowing eyes and mouth.

Body, height, bore and the motif datum come from the `halloween_lantern` project and are not this part's to choose. Only the motif is its own.

## What it is for

The same object as `raven_lantern` and `witch_lantern`, used the same way: a battery LED tea light in a cylinder on a table through October.

Lit, each window should read as a ghost at a glance — from across a room, without anyone being told what it is.

## Why this one is inverted, when the other two are not

The set's other motifs are **holes**: a raven, a witch's head in profile. Both read from their outer contour, so the silhouette carries them and nothing needs to survive in their interior.

**A ghost does not.** Its recognition lives in its face, and a faceless ghost is a blob — that was tried and it failed. Under the usual polarity the eyes and mouth would have to be chips of plastic floating inside the hole, which is the same failure that destroyed `raven_lantern`'s lettering.

Inverting solves it at no cost: with the ghost as material, its eyes and mouth are simply **holes in material**, which is free. See `chatgpt-prompts/ghost-cutout.md` for the three attempts that established this, and `ARTWORK.md` for the general rule.

## Constraints

**Fixed by the world**

- **The puck is opaque for its whole lower half.** An opening in that zone is a dark hole with grey plastic behind it, not a lit window. Hard floor.
- All puck dimensions are `measured` and live in the project's `shared.py`.
- **A rolled paper liner is part of the design.** It turns a near-line source into a lit column. **Anything on the inner wall is visible in use** — the liner backlights it rather than hiding it.
- **Black PLA is effectively opaque.** Every lit element must be a hole.

**Fixed by the set** — from the project, not negotiable here:

- Height is fixed and the motif hangs a fixed distance below the rim, so motifs line up across a shelf.
- Bore, wall and standoff are shared, so any puck fits any lantern.
- Supports are judged against what they touch, not banned.

**Fixed by the process**

- Prints upright on its base.
- **The ghost is retained material**, so it must be anchored. Support propagates upward, so an anchor at the **bottom** is what actually matters: a ghost touching only the sides or top begins in mid-air.
- Each opening is a gap the nozzle jumps on every layer of the band. Opening count is a printability parameter, not only a compositional one.

**Fixed by taste**

- A lantern, not a colander.
- The ghosts read as a ring, evenly spaced, all facing forward.
- It should look like a sibling of the other two on a shelf.

## Acceptance criteria

### Does it do its job?

- [x] **It reads as a ghost** — body, eyes and open mouth identifiable without prompting.
- [x] **It reads at the size actually printed**, judged from a true-scale two-tone flat, never a magnified view.
- [x] **The ghost is dark and the window is light.** Getting this inverted produces a ghost-shaped hole, which is the design that failed.
- [x] **The eyes and mouth are holes in the ghost**, not floating chips.
- [x] **Every opening sits entirely above the puck's opaque base.** Asserted.
- [x] **The ghost is continuous with the wall** — one connected solid, nothing relying on a bridge or a web to stay attached. Asserted.
- [x] **Nothing starts in mid-air.** The ghost's robe reaches the bottom of the window and merges into the wall below, so support propagates up through the whole figure. Verified: zero islands.
- [x] **Every hole clears the nozzle** — the narrowest is comfortably over.
- [x] **The lantern reads as a black object**, not a cage.
- [x] **The puck can be retrieved by hand.**
- [x] **It belongs to the set:** height, bore, wall and datum come from the project.

### Is it built correctly?

- [x] **One connected solid.**
- [x] Ghosts evenly spaced; material between adjacent windows exceeds the minimum.
- [x] Solid rim above the motif and solid wall below it.
- [x] Every ghost faces the same way — the motif is handed, so a cutter extruded both ways would mirror it onto the far wall.
- [x] Fits the configured bed.
- [x] `PRINT_ROTATION` is stated, and the overhang check runs in that pose.
- [x] **The artwork is in the repo**, not in a chat cache, so the trace can be re-run. `raven_lantern`'s source was lost exactly this way.

### Only a print can settle these

- [x] **It reads as a ghost at night, lit, across a room** — and to someone who was not told what it is. That is the test the set uses.
- [x] **The window ceilings bridge cleanly.** Each opening's top is a flat horizontal span anchored at both ends by the ribs, and they are wider here (~5–6 mm) than anything the raven bridged.
- [x] **The slicer asks for no supports**, as the zero-island result predicts.
- [x] Stringing across the openings is acceptable at the project's 210 °C.

All four settled by the first and only print, which needed no rework — the one part in the set that went cleanly first time. The bridging and the supports were not separately observed and measured; they are ticked because a failure in either would have been the rework that did not happen.

## Open questions

- Whether five is the right count. The windows are nearly square here where the other motifs were tall, so the ring reads denser at the same number.
- Whether the ghost's dark body reads as intended against a lit field, or whether the eye is drawn to the bright window and away from the figure. Only a lit print settles it.
