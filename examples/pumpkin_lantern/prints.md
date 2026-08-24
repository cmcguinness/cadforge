# pumpkin_lantern — print log

One entry per physical print. This closes the outer loop: the renders and the checks can only judge geometry, and everything else is discovered here.

Record a print even when it succeeds. A design that works and nobody wrote down *why* it works is one refinement away from losing the property by accident.

## Template for an entry

### YYYY-MM-DD — iteration #N (`<params digest>`)

- **Settings:** material, layer height, supports, orientation on the plate.
- **Result:** what came out.
- **Measured vs. modeled:** the numbers that differed, and by how much. This is what turns a `nominal` constraint in spec.md into a `measured` one.
- **Verdict:** and then run `cad accept <part> good|bad|mixed "<why>"` so the iteration history carries it too.

---

### Partial print, aborted deliberately (`9778a915`)

Base and lid together on one plate, orange PLA, no supports. **Killed part-way through on purpose**, once a defect was spotted in the sliced preview rather than in anything the harness had reported.

**What it settled, which is the point of running it at all:**

- **The ribbing reads.** Ten lobes at 1.3 mm of amplitude on a 70 mm pumpkin is the right amount at this size — present, not corrugated. This was an open question and it is now closed.
- **The teeth print.** The two rows of triangles were mid-way and coming out clean, which exercises the arrangement that matters: apex-down holes bridging onto their lands, apex-up holes needing no ceiling at all, and the 1.4 mm waist between the rows surviving as a real feature.
- **1.1 mm walls print** as walls. Whether they *glow* is still unknown — the print never got far enough to light.

**Why it was killed: a disconnected ring near the top of the lid.**

The shoulder collapsed into the stem too fast — 16 mm of radius over 2.4 mm of height. For a hollow shell that means each printed ring shifts inward 1.36 mm per 0.2 mm layer against a wall only 1.1 mm thick, so consecutive rings do not overlap at all. Not a rough surface: a stack of loose hoops.

**Nothing in the model complained**, and that is the interesting part. The surface was smooth, both pieces were valid solids, and the `islands` check passed — its grid is 0.4 mm where the real tolerance here is 0.168 mm, coarse enough to conclude the rings touched when they did not. It was caught by a person looking at the slicer preview.

Fixed by a slope clamp on the profile plus an assertion that states the rule directly: **|dr/dz| × layer height must be less than the wall thickness**, or the rings cannot reach each other. That constraint is peculiar to hollow lofted shells and does not exist for a solid part, which is why no general check has it.

**Verdict:** `mixed` — the shape and the ribbing are right, the shoulder was not.

---

### Iteration #17, two-row grin (`753a1622` geometry, `tooth_row_h` 7.2)

First complete print of the one-piece design. Orange PLA, 210 °C, 0.2 mm, no supports, upright on its own skirt.

**What it settled — the four questions the renders could not answer:**

- **1.1 mm is strong enough as a closed shell.** The partial print felt marginal in the hand; the finished one does not. The dome and the floor ring stiffen it far out of proportion to their thickness, which is why the earlier sample was misleading.
- **The shoulder welds.** Tightening the ring-overlap factor from 0.7 to 0.45 fixed it directly — no loose hoops, no disconnected ring. It still shows faint concentric terracing on the shallow dome, which is cosmetic and lives at the top where nothing is looked at.
- **The annular ring centres it.** 0.9 mm per side is right: the pumpkin drops over the puck without being forced and does not wander.
- **The stem survives being picked up by.** It is the natural handle and it takes it.

**And the thing the whole part is for:** lit, the face is the brightest thing and the body glows orange behind it. Both halves, which is what separates this from the other three lanterns.

**The one defect:** the mouth read wrong. Two rows of four aligned triangles, apex-to-apex, fuse visually into **three diamonds in a slot** rather than a set of teeth. The geometry was exactly as modelled; the failure was in what the eye does with it, which no assertion could have caught.

**Verdict:** `mixed` — everything structural and optical passed; the grin needed redrawing.

---

### Iteration #18, interleaved grin (`a328657f`) — **accepted**

Same settings. The only change since #17 is the mouth: **4 apex-up triangles on the bottom row, 3 apex-down on top, interleaved on a shared period**, with the rows deliberately overlapping 3.4 mm so the material between them is one continuous zigzag rather than two rows either side of a waist. Mouth widened 30 → 36 mm so the triangles come out roughly equilateral (7.6 × 7.2 mm) instead of tall and narrow.

**Result:** it reads as teeth. The diamond illusion is gone — the offset breaks the apex-to-apex pairing that caused it, and the overlap means there is no horizontal band across the mouth for the eye to latch onto. The wider triangles bridge cleanly at 7.6 mm.

**The lesson worth keeping:** *a hole is not the shape you see.* Two rows of identical holes at the same pitch produce a third figure between them, and that figure is what gets recognised. Interleaving is what stops it. This is a figure/ground problem of exactly the kind that killed the flying witch, arriving in a part where nobody was watching for it.

**Verdict:** `good`. Fourth lantern in the set, and the only one that glows rather than silhouettes.

### Photographed lit, and turned all the way round

`finished_pumpkin_lantern.jpg` plus a full 360° turn on a turntable (`videos/finished_pumpkin_lantern.mov`, reduced to `finished_pumpkin_lantern.gif`).

**The turn is what a still could not show: the back is plain glowing ribs.** With the face away from the camera the object is still unmistakably a lit pumpkin — the ribbing reads, the stem reads, the whole body is orange light. That is the wall-as-filter claim holding up from an angle nobody designed for, and it is the reason this part gets away with a face on one side only. Every other lantern in the set would be a black cylinder from behind.

**The face is the brightest thing from the front and the body is bright everywhere**, which was the criterion, and both halves of it survive being photographed rather than reasoned about.
