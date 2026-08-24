# witch_lantern — notes

**Read before editing the model. Update when you learn something.**

## ABANDONED — the witch does not survive down-resing

Kept rather than deleted, because the reason is worth more than the part was.

She reads only if her **arm is separated from her body** and her **hand from the broom**. At a 19 mm moon those gaps measure 0.79 mm and 0.40 mm — one marginal, one exactly one nozzle wide. Close them and she is a dark mass in a hat; keep them and they are at or under what the machine can resolve.

That is not a tracing problem and no pipeline step fixes it. Merging, dilating and re-tracing all operate on the boundary, and **her legibility lives in her interior**. Two rounds of regenerated artwork and a rewritten opening filter got the geometry exactly right — the final trace matches the reference at 0.93 IoU, with the remaining difference being precisely those two gaps — and it still did not read.

The general rule is now in `ARTWORK.md`: **choose motifs that read from their outer contour alone.** The raven did; the witch never could.

What is worth keeping from this part if a moon-and-figure design is ever revisited at a larger size:

- The **openings-as-artwork** technique below. It is sound and it removed the retaining-web failure mode entirely.
- `trace_moon.py`, including the width-based opening filter.
- The observation about the render sheet, immediately below, which cost real confusion.

## The render sheet cannot review this part

`build/review/sheet.png` shows the witch as abstract shapes and **that is not a bug in the geometry**. The renderer produces a shaded grey solid, so the witch and the wall she stands in are the same tone and the silhouette has nothing to separate against. The design depends entirely on contrast between a lit opening and dark material, which a shaded exterior cannot show by construction.

This misled both of us once — it reads as though the wrong artwork was traced.

**Review this part from `design-approval.png` instead**, which is regenerated from the built geometry (not from the source image) as a two-tone unrolled wall at true scale, plus a nozzle-resolution simulation. The command that makes it is in the session log; it reads `moon_openings.py` and `geometry()`, so it always shows what the STL will actually do.

Generalises: **for any motif whose whole point is figure/ground contrast, a shaded render answers a different question than the one being asked.**

## The witch is not modelled

The artwork is composed the way the part is built — black is plastic, white is hole — so `trace_moon.py` extracts the **openings**, and the witch is whatever material they leave behind.

This is the load-bearing idea and it is worth not undoing:

- **Anchoring is a property of the reference image.** Her hat, broom and skirt run out through the moon's rim into the wall because the artwork draws them that way. The model arranges nothing.
- **There is therefore nothing to retain.** `raven_lantern` had to hold glyph counters on with thin webs added back in the innermost sliver of the wall, and those webs are exactly what tore apart during support removal. Here every piece of plastic is continuous with the wall by construction.
- `check()` asserts `len(part.solids()) == 1` rather than trusting it. A witch severed from the rim by a re-trace or a scale change is a separate solid, and counting solids catches that however it happens.

## Openings below the nozzle are dropped, not cut

`MIN_OPENING_MM2` in `trace_moon.py` discards openings under 1.5 mm². A sliver about a nozzle wide will not resolve as a hole — the slicer fills it with ragged gap-fill. Dropping it makes it solid material, which is a clean outcome; leaving it in is not. Two were dropped from this artwork (0.95 and 0.50 mm²).

This is the raven's toe problem in the other polarity: there, too-thin *material* became gap-fill; here, too-thin *opening* does.

## Why the moon is as large as the lit wall allows

`moon_dia = 0` means "take the whole lit wall", which is the sensible default rather than a lazy one: the moon **is** the lit area, so giving any of it back costs brightness and legibility for nothing. At the project's fixed height that comes out at 19 mm, which is also the ceiling — the assertion that the moon clears the puck's opaque base is what enforces it.

Four moons, not six. Compositionally 4 reads generously where 6 crowds, and independently, each opening is a hole the nozzle must jump on every layer of the band — `raven_lantern` strung badly with six. The two arguments happen to agree, which is why 4 was easy.

## Open threads

- **Nothing has been printed.** Every criterion about light, legibility and strength is still open.
- **The witch is a thin feature suspended in a hole**, and nothing has been prodded. She is well anchored in the model; whether she survives handling and the paper liner being fitted is unknown.
- **Whether four large round openings weaken the wall more than the raven band did.** Round holes pinch the wall to its minimum over a short height rather than tapering, which is why `min_rib` is higher here.
