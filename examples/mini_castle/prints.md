# mini_castle — print log

One entry per physical print. This closes the outer loop: the renders and the checks can only judge geometry, and everything else is discovered here.

---

### Iteration #2, first print, lit

- **Settings:** PLA (purple), 0.2 mm layers, upright as exported.
- **Result: it prints and it lights.** 68 × 46 × 89 mm. The gate bars survived at 0.7 mm, the tiled turret roof came out crisp at half scale, and the bat is cleanly formed.

**The lighting prediction was wrong in both directions, which is worth being precise about because the reasoning behind it was plausible and still failed.**

`notes.md` predicted the mouth would darken from its threshold upward, because the puck's 15 mm opaque base covers 66% of the face storey at this scale. It predicted the bat window would do well because it sits opposite the emitting band. Neither happened:

| opening | predicted | actual |
|---|---|---|
| mouth | darkens from the threshold | **the brightest thing on the object** |
| eyes | lit | lit, pupils read clearly |
| bat window | lights well | **dim** — reads as a silhouette against low ambient, not a glowing window |
| top turret | ambient at worst | **a black hole** |

**Why. THE PUCK WAS ON ITS SIDE** — laid down with the flame horizontal and aimed at the openings, not standing upright as every part in this repo has assumed.

That single fact explains the whole result and invalidates the prediction's premises rather than merely its conclusions:

- Lying down, the puck is 35 mm tall (its diameter) and the flame sits on the cylinder axis at roughly **z 18 mm**, pointing horizontally at the front wall — square in the middle of the face storey, which spans z 1.2–23.8.
- So the face is brilliant because **the light was aimed at it**, not because of bounce or proximity.
- The bat window (z 26–43.8) and the top turret (z 45–60.8) are simply *above the beam*. They are not suffering falloff up a chimney; they are outside the cone.
- **The 15 mm opaque base never entered into it.** On its side that base is behind and beside the flame, not a plinth under it. The entire "the base covers 66% of the face storey" constraint — which this part was designed around and which `spec.md` calls the central open question — describes an upright puck and does not apply to this print.

**The real finding is that puck orientation is a design variable, and nobody had noticed.** `projects/halloween_lantern/shared.py` states its heights are "measured from the surface the puck stands on" and every part here inherits that assumption silently. A puck on its side is a *directional* source at mid-height instead of a vertical column at floor level, and it changes which openings light more than any geometry change considered so far.

**This was a field modification, and it is the best thing to come out of the print.** The design intent was a puck sitting flat on the floor, exactly as the spec describes; laying it on its side was done at the bench because it made the light better. That is the outer loop doing its job — the physical object teaching something no render, check or assertion could have raised, because nothing in the model knows the puck can be turned over.

Two consequences, and the second is the actionable one:

- The criterion this part was built around — whether an upright puck's opaque base swallows the gate — is **still open**, since the winning configuration sidesteps it. Turning the puck upright and looking would settle it, and costs nothing. Worth knowing, not worth much.
- **The sideways orientation should stop being a field modification and become part of the design.** Right now the puck is a cylinder resting loose on a flat floor: it can roll, its aim is set by hand every time, and nothing holds the flame at the height that worked.

**The second field modification tells us exactly what that feature should be.** The puck was stopped from rolling with **small rolls of electrical tape, sticky side out, placed either side of where its rounded edge meets the floor.**

That is a cradle, improvised, and its shape is informative: the constraint that was actually needed is **lateral, at the tangent line** — two small stops where the cylinder touches down — and *not* a deep saddle wrapping the puck. Which is the cheaper geometry by a distance:

- two low ribs running front-to-back either side of the contact line, spaced a little under the puck's diameter apart;
- no overhang, no bridging, nothing that complicates the print;
- the puck still drops in from the open back and settles between them rather than being threaded into a socket;
- and it fixes the *aim* as a side effect, because a cylinder that cannot roll cannot rotate its flame away from the face either.

**But the tape is a perfectly good answer, and that is the honest conclusion.** The chock positions are pencilled on the floor, and replacing a strip is close to eyeballing it anyway. This is a decoration that gets handled a few times a year, not a mechanism.

So the ribs are **optional polish, not a missing feature.** Recorded because the tangent-line insight is worth having if this part is ever revised for another reason — not because the lantern needs fixing. It works.


**Criteria this settles:**

- The face reads as a face, lit. The gate is emphatically not swallowed by the opaque base — the criterion that was expected to be the hard one passes outright.
- The 0.7 mm gate bars print. They are legible and separated, not merged.
- One tea light does light it, and goes in and out through the open back.

**Criteria this fails:**

- **The top turret is a black hole.** The criterion explicitly allowed lit-by-scatter and disallowed dark. It is dark.
- **The bat window is weak.** It reads, because the bat is a silhouette and a silhouette only needs contrast — but the window does not glow, and at full size it does.

**With paper behind the face and the bat: better again, and the part is good.**

The bat window was the weak opening on the bare-puck print — the bat read as a silhouette against a dim interior rather than a lit one. Paper behind it fixes that. Same story as the full-size castle, where the diffuser turned out to be an improvement to something that already worked rather than a dependency of it, except here it is carrying more of the load: this puck is *aimed*, so an opening outside the beam has only the paper to spread light into it.

Worth stating as the general form, since it now has two data points:

> **Paper does not add light, it redistributes it.** On the full-size castle, where each storey has its own source, it softened openings that were already lit. Here, with one aimed source, it is what reaches an opening the beam does not point at. The taller the object relative to its light, the more the diffuser is doing.

**Also observed: stringing.** Fine wisps across the front and between the turrets. `SLICING.md` already carries the answer under material scope — 210 °C rather than 220, try temperature first — learned on `raven_lantern` and not applied here. Cosmetic at worst on a Halloween ornament, where it reads as cobweb.

### Photographed lit, and turned all the way round

`finished_mini_castle.jpg` plus a 360° turn (`videos/finished_mini_castle.mov`, reduced to `finished_mini_castle.gif`). The turn shows the open back with the puck lying on its side, which is the configuration this file's prediction-that-was-wrong is about — it is now on record as a photograph rather than only as prose.

Two things the photograph adds:

- **The corner-turret windows read dark**, checked on a full-resolution crop rather than from the whole-part view. Same result as the full-size `castle`, and for the same reason: the turret shafts are not in the light path and nothing lines them. The turret *walls* glow, because purple transmits — but a glowing wall with a black arch in it is not a lit window.
- **Purple at this wall thickness transmits**, so the whole facade glows and the object reads as lit stone rather than as a dark box with holes in it. That inverts the polarity the model was drawn to, exactly as recorded for the full-size part, and it is a filament-colour effect rather than a geometry one.
