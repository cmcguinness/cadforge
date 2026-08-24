# ghost_lantern — print log

One entry per physical print. This closes the outer loop: the renders and the checks can only judge geometry, and everything else is discovered here.

Record a print even when it succeeds. A design that works and nobody wrote down *why* it works is one refinement away from losing the property by accident.

## Template for an entry

### YYYY-MM-DD — iteration #N (`<params digest>`)

- **Settings:** material, layer height, supports, orientation on the plate.
- **Result:** what came out.
- **Measured vs. modeled:** the numbers that differed, and by how much. This is what turns a `nominal` constraint in spec.md into a `measured` one.
- **Verdict:** and then run `cad accept <part> good|bad|mixed "<why>"` so the iteration history carries it too.

---

### First print, four ghosts (`7310f730`)

Black PLA, upright, the set's profile (210 °C, scarf around entire wall, avoid-crossing-wall at 100%).

**Result: great.** Third of the set and the first that needed no rework at all.

Worth recording *why* it went cleanly, because three earlier attempts at a ghost did not:

- **Inverted polarity.** The ghost is the material and the window around it is the opening, so its eyes and mouth are **holes in material** — topologically free. Under the set's usual polarity they would have been chips of plastic floating inside a hole, which is the failure that destroyed `raven_lantern`'s lettering. A ghost cannot drop its face the way a raven or a witch-in-profile can: its recognition lives there.
- **The artwork was edited by hand to anchor it.** The generated version had the robe stopping inside the window; extending it to the window's bottom edge so it merges into the wall below took the part from **29 floating islands to zero**. Support propagates upward, so an anchor at the bottom is the one that actually matters — sides and top do not help.
- **Four, not five.** Judged at true scale: five left 41% of the motif width as solid between windows and read as a band of light; four leaves 77% and reads as a dark object with windows in it.

**Verdict:** `good`.

**Still worth noting for the record**, if anyone remembers: whether the slicer asked for supports (the zero-island result predicted not), and whether the flat ceilings at the top of each window — ~5–6 mm bridges, wider than anything the raven bridged — came out clean.

### Photographed lit, in the dark

`finished_ghost_lantern.jpg`. One tea light, paper liner rolled inside the bore, on a shelf at room distance.

**The polarity argument is settled by looking.** The ghost reads as a dark figure standing in a lit window — arms up, round eyes and open mouth burning through — rather than as a bright ghost-shaped blob, which is what the set's usual motif-as-opening polarity would have produced. The eyes and mouth are the brightest things in the frame despite being the smallest openings, because they sit inside the figure where nothing competes with them.

**The liner is doing its job.** The window is an even field rather than a bright bar with a visible flame in it, which is the whole reason the paper is there. Whether the ~5–6 mm window ceilings bridged cleanly is not something this photograph can answer — they are behind the ghost, unlit and out of the light path.

### Turned all the way round

A full 360° turn (`videos/finished_ghost_lantern.mov`, reduced to `finished_ghost_lantern.gif`). The still above is one ghost; the turn is all four, and it answers a question no single view could.

**The four-not-five decision holds up in motion.** The rib between adjacent windows is wide enough that as one ghost leaves the frame the next is only just arriving — there is always solid, unlit wall between them. That is the property the rib fraction was chosen for, and until now it rested on a judgement made at true scale on a flat drawing. Turning the object is the test that drawing could not be: at five the ribs would be passing through the eyeline continuously and the lantern would read as a band of light rather than as a dark object with windows in it.

**The liner reads evenly on every face.** No hot face, no dim face, and no visible flame at any angle — which is a stronger result than the single still gives it credit for, because a rolled paper tube is not a precision component and there was no reason to assume it would sit concentric.

### The animation is one period, not one turn

`finished_ghost_lantern.gif` covers **90° — one quarter of a rotation, 57 frames at 10 fps** — and loops without a visible seam. Four identical ghosts evenly spaced means a quarter is a full period of the object, so three quarters of the footage was redundant. 993 kB instead of 2.3 MB, and the loop reads as an endless procession rather than as a clip that restarts.

The period landed at exactly 228 ÷ 4 frames — the clip is one clean revolution and the turntable is motor-driven, so a quarter of the frames is a quarter of the turn. Seam after a six-frame crossfade is 2.11 against 3.84 for two consecutive frames, so the loop point is a smaller step than a normal frame advance.

Picking the loop by smallest raw frame difference is unreliable even here, where the period is exact: the room light is fixed while the object turns, so a ghost at one angle is never lit like the ghost 90° along and the minimum is shallow. `witch_lantern/prints.md` has the method that works and the wrong explanation that got published first.
