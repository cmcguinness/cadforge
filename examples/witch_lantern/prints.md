# witch_lantern — print log

One entry per physical print. This closes the outer loop: the renders and the checks can only judge geometry, and everything else is discovered here.

Record a print even when it succeeds. A design that works and nobody wrote down *why* it works is one refinement away from losing the property by accident.

## Template for an entry

### YYYY-MM-DD — iteration #N (`<params digest>`)

- **Settings:** material, layer height, supports, orientation on the plate.
- **Result:** what came out.
- **Measured vs. modeled:** the numbers that differed, and by how much. This is what turns a `nominal` constraint in spec.md into a `measured` one.
- **Verdict:** and then run `cad accept <part> good|bad|mixed "<why>"` so the iteration history carries it too.

---

### First print, witch head, WITH supports

Five heads, 19 mm, black PLA, printed upright with support generation enabled. `cad build` had flagged 15 floating islands on this geometry — the notch between the hat's curled tip and its crown, where a wedge of wall pokes down into the opening and starts in mid-air.

- **The supports came off cleanly, with no damage.**

That settles the question the islands check exists to raise, and it settles it the *other* way from the project's previous rule. Supports are fine here. The lettering did not die because supports are dangerous; it died because 0.5 mm webs cannot survive anything being pried off them. A witch's hat brim can.

The project's stance is revised accordingly: supports are judged against the robustness of what they touch, not banned. See project.md.

**Result: good. It passes.**

The acceptance criterion was that it be identifiable **without prompting**, and that was tested the only way it can be: someone who had not been told what it was looked at it and said "witch". That is worth more than any amount of squinting by the people who designed it, and it is the method to repeat on every motif in this set — recognition by a person with no context is the whole point of a silhouette, and the designers are the last people able to judge it.

The hat point and hair tendrils survived; stringing at 210 °C was acceptable.

### Photographed lit, and turned all the way round

`finished_witch_lantern.jpg` plus a full 360° turn (`videos/finished_witch_lantern.mov`, reduced to `finished_witch_lantern.gif`). One tea light, paper liner rolled into the bore.

**The profile survives at true scale, which is the whole bet this part made.** Hat brim, hooked nose, chin and streaming hair all read as a silhouette from across a room — no interior detail, nothing that had to be held on by a web. That is the claim `notes.md` makes about outer-contour motifs, and it has now been tested against a photograph rather than a two-tone flat.

**Five motifs is fine here, and the turn shows why it was not fine on the ghost.** Two witches are visible at once with solid wall between them, because a profile is narrow. The rib rule is a fraction of *motif width*, and a narrow motif spends less of the circumference — so the same fraction that forced `ghost_lantern` down to four leaves this one comfortable at five. Worth recording, because the number five looks like a set-wide constant in the shared body and is not one.

**No hot face and no visible flame at any angle**, same as the ghost. Two lanterns now say the rolled paper tube sits well enough without being a precision part.

### The animation is one period, not one turn

`finished_witch_lantern.gif` covers **72° — one fifth of a rotation, 40 frames at 10 fps** — and loops without a visible seam. Five identical heads evenly spaced means a fifth is a full period of the object, so a whole revolution of footage carries the same information five times over. 687 kB instead of 2.3 MB. The technique and the reasoning live in `raven_lantern/prints.md`.

**Choosing the loop point by smallest raw frame difference is not reliable, and this clip is where that showed.** The obvious method — find the pair of frames one period apart that look most alike — picked a spurious match at the edge of the search range. The minimum is *shallow*: because the room light is fixed while the object turns, a witch at one angle is never lit quite like the witch 72° along, so no two frames a period apart ever match well and the search is choosing between near-equal bad options. Asking which candidate has the lowest best-matching period at each start gives answers scattered from 38 to 53 frames around a true value near 42.

The fix is to stop optimising the wrong quantity. Shortlist by raw match, then choose on **the seam that survives the crossfade, measured against an ordinary frame step inside the same window** — which is what actually decides whether a viewer sees a jump. That found 40 frames starting at 2.1 s, seam 2.03 against 3.52 for two consecutive frames.

**A correction, kept because the mistake is more instructive than the result.** This section first claimed the turntable was hand-spun and decelerating, inferred from a frame-to-frame motion figure that fell from 7.8 to 1.4 and rose again. The turntable is motor-driven and turns at a constant rate. Checking the background separately — which a wobbling camera would move and a rotating object would not — showed it nearly static throughout, so that was not the cause either. A derived statistic was handed a physical mechanism it could not support, and the mechanism was written into a durable file. **Measure the thing you are claiming, not something correlated with it**, and if the claim is about the rig, look at the rig.
