# raven_lantern — print log

One entry per physical print. This closes the outer loop: the renders and the checks can only judge geometry, and everything else is discovered here.

Record a print even when it succeeds. A design that works and nobody wrote down *why* it works is one refinement away from losing the property by accident.

## Template for an entry

### YYYY-MM-DD — iteration #N (`<params digest>`)

- **Settings:** material, layer height, supports, orientation on the plate.
- **Result:** what came out.
- **Measured vs. modeled:** the numbers that differed, and by how much. This is what turns a `nominal` constraint in spec.md into a `measured` one.
- **Verdict:** and then run `cad accept <part> good|bad|mixed "<why>"` so the iteration history carries it too.

---

### Iteration #6 (`b4a8ec93`)

First physical print. Black PLA, upright on the base as exported, supports on.

- **Result: mixed.** The ravens came out well and settle the motif entirely — silhouette, feet, size and placement are all right and none of them need another lap. The two failures are unrelated to each other.

- **The bore is 2 mm too small. The puck does not fit.** Modelled bore was 36.2 mm for a puck measured at 35.0 mm, i.e. 0.6 mm radial clearance. In the hand that is not enough. Corrected by taking the shared `fit` from 0.6 to 1.6 mm, which is a **2 mm increase in diameter** as asked.

  What has *not* been established is which of three causes it was, and they have different consequences for the rest of the set:
    1. the puck is wider than 35.0 mm at some point that was not measured — many have a lip or a moulded seam above the widest caliper point;
    2. printed bores come out undersize — normal on FDM, and it would apply to every lantern and every other part on this machine;
    3. 0.6 mm was simply optimistic for a part you drop something into by feel.

  Worth ten seconds with a caliper on the printed bore next time one is in reach: if it measures under 36.2 mm, it is (2) and it is a machine fact worth knowing everywhere, not a lantern fact.

- **The lettering tore apart on support removal.** The retaining webs did not survive. They were 0.5 mm wide by 0.8 mm deep, a single extrusion, spanning the counters of `R` and `O` on the inside face — and the slicer put support material in the letter openings, so removing it pulled directly on them.

  The design error was not the web dimensions. It was **putting a fragile feature where a support has to be removed from**. The webs were sized against the nozzle — can the machine lay this down — and never against the forces of post-processing, which is where they actually died. A feature can be perfectly printable and still not survive being made.

  Dropping the lettering rather than thickening the webs, on request. Thicker webs would have to grow a lot to take a thumbnail's worth of prying, and by then they are visible from outside and the letters read badly again — which is where this started.

- **Verdict:** `mixed` — ravens settled, bore and lettering both wrong.

### Iteration #7, lettering-free, 40 mm fixed height

Black PLA, upright, **no supports** — the slicer asked for none once the lettering was gone. Sliced with `Scarf around entire wall` ON and `Avoid crossing wall` ON at 100% max detour.

- **The ravens are good.** Silhouette, feet, size and placement all settle. The motif is done; nothing about the bird needs another lap.
- **The bore fits now.** `fit` 0.6 → 1.6 mm was the right correction.
- **Seam bump: fixed.** `Scarf around entire wall` did it. The diagnosis holds — the default `Smart scarf` skipped the seam exactly where the raven openings created corners, which is where `Seam position: Aligned` was putting it.
- **Stringing: improved but NOT fixed**, and worse than expected in one specific way.

#### The liner does not hide interior strings — it backlights them

Recorded because the opposite was asserted here and it was wrong.

The reasoning was that the paper liner covers the inside wall, so strings there are invisible in use. In fact the liner rolls up **inside** the strings, so they end up trapped between the paper and the wall. Lit, they are silhouetted against a glowing white surface — which makes them *more* visible than bare strings on a black wall, not less.

So interior finish is not cosmetically free on this design, and any future "it's on the inside, it doesn't matter" reasoning about this set is wrong for the same reason.

Removed with a needle file. That works and is not a fix — it is a per-lantern manual step on a set meant to be printed several at a time.

#### Why they persist

Travel across the openings, not across the bore. `Avoid crossing wall` can route travel *within* solid material, but at any layer through the motif band the wall is genuinely discontinuous at each opening — there is no path around, only a jump across. With six ravens roughly 17.6 mm wide, that is twelve long jumps per layer over the whole band, and no travel setting removes the need for them.

Which makes **raven count a printability parameter**, not only a compositional one. Six was chosen by eye.

### Stringing settled: 220 °C → 210 °C

**Dropping the nozzle temperature by 10 °C fixed it well enough.** Everything else was already in place — `Avoid crossing wall` at 100% detour, scarf seam, retraction at stock — and the residual stringing came off with the last 10 °C.

Worth recording as the *first* thing to try, not the fourth. It was ranked below drying the filament here on the reasoning that persistent stringing after retraction is configured usually means moisture. That inference was wrong on this machine, and it would have cost a $45 purchase to find out. **Temperature is free to test and takes one reslice; buy hardware only after it fails.**

No filament dryer was needed. The moisture hypothesis is untested rather than disproven — it may still matter for a spool that has sat open longer.

Raven judged **good enough**: motif, fit, seam and stringing all acceptable.

### Slicing the lettering-free version, before printing

**The lettering was the only thing asking for supports.** With `text` empty the slicer wanted none at all.

That closes the loop on the previous failure, and the shape of it is worth keeping: the letters needed supports, the supports had to be pulled out of the letter openings, and pulling them out destroyed the webs holding the letters together. **The feature and the thing that killed it were the same feature.** No amount of strengthening the webs addresses that, because the load only exists because the letters do.

It also confirms the ravens are self-supporting on their own, which had been an open print-only criterion: every opening is in a vertical wall and bridges across its own top the way a circular hole does. Any future motif in this set should be held to the same standard — **if a motif needs supports, that is a reason to reconsider the motif**, not a slicer setting to change. Support removal is a force nothing in the model can see.

### Photographed lit

`finished_raven_lantern.jpg`. One tea light, paper liner rolled into the bore, shot close so the motif fills the frame.

**The raven reads in full detail at true scale** — beak, breast, the separation between body and legs, and the feet. That is more than the design needed: the set's rule is that a motif must survive on its outer contour alone, and this one is carrying interior articulation as well.

**The empty band below the birds is the record of the failure**, and it photographs as exactly what it is: a plain stretch of wall where lettering used to be. Worth having, because a written description of a missing feature is easy to skim past and a picture of the gap is not.

**This photograph is now the only visual reference for the motif.** The source artwork lived in a per-session image cache and is gone, so the outline exists solely as coordinates and cannot be re-traced against the original. Nothing can regenerate it; the shape can only be edited numerically from here. Every traced part since keeps its reference in `inspiration/` for precisely this reason — the rule was written after this part paid for it.

**The turntable clip is half a rotation** — `videos/finished_raven_lantern.mov`, 8.7 seconds, three of the six ravens passing. The published GIF is not half a turn, though. It is **one sixth**, and it loops seamlessly.

**Six identical ravens on a ring means 60° is a full period of the object.** Rotate the lantern that far and it is, up to the room's lighting, the same object in the same pose — so a full revolution of footage is six copies of one piece of information. Searching the clip for the frame pair that minimises image difference found the period exactly: **31 frames at 10 fps, 3.10 s**, at a difference of 4.88 against 12.75 for two random frames. Sub-frame refinement at 20 fps did not improve it, which says the residual is not a timing error — it is that the room light is fixed while the object turns, so a raven at one angle is never lit quite like the next one.

**That residual was removed with a six-frame crossfade** at the loop point, blending the tail into footage from one period later. Seam difference fell from 6.15 to **2.60**, against 3.00 for two ordinary consecutive frames — the loop point is now a smaller step than a normal frame advance, so there is nothing left to see. The file is 616 kB for an endless turn, against 2.3 MB for a single revolution on the other lanterns.

**The general technique, since it applies to anything with rotational symmetry:** film a full turn, then publish one period of it. The saving scales with the symmetry order — six ravens, one sixth the file.

**How the rotation was measured, because the first attempt got it wrong.** Tracking the centroid of all lit pixels said the object barely moved, and "roughly a fifth of a turn" was written here on that basis. It is nonsense: ravens leave at the left as fast as they arrive at the right, so the *aggregate* centroid sits nearly still no matter how fast the cylinder spins. Charles simply counted the ravens going past and got the right answer without any of this.

The general form is one this repo keeps relearning in new costumes: **a global statistic will not measure a local event.** The same mistake as reading a whole-part render for a 0.6 mm mortar groove, or judging the castle's pupils from a downscaled frame. Measure the thing that actually changes, not the average of everything.
