# Creepy owl — silhouette for a flat standee

For `parts/owl`: a flat plate cut to the owl's outline, printed **lying flat on the bed**, slotted and glued into a separate branch-shaped stand. A tea light sits on a shelf behind the head, level with the eyes.

## Why this prompt departs from TEMPLATE.md

`TEMPLATE.md` is written for a motif cut **into** a panel that stands vertical while it prints. Almost none of it applies here, and pasting it unchanged would over-constrain the artwork badly:

- **The polarity is inverted.** There, black is the hole and the panel is white. Here **black is the object** — the plate itself — and white is simply removed. The eyes are white holes inside black, which is topologically free: a hole in material is just a hole.
- **Every layer-support rule is void.** No downward spikes, no stalactites, ceilings not beginning in mid-air, prefer a single peak — all of that exists because a lantern motif's plane is *vertical* during printing. This plate lies flat on the bed, so its plane is horizontal and none of those failures are possible. Ear tufts, deep notches and a ragged feathered outline are all free.
- **The minimum feature is negligible.** At 140 mm tall, three extrusion widths is 1.2 mm — about **1%** of the height, against 7% for the 19 mm lantern motifs. Detail is affordable here in a way it has never been before in this repo.
- **No pupils in the artwork.** The eyes become apertures, and a printed paper insert behind them carries the colour and the pupil. Asking the generator for pupils would only mean cutting them back out.

What *does* still matter: one connected piece, and nothing black floating detached from the body.

## The prompt

> Create a **creepy owl, seen head-on, staring directly at the viewer**, as a single-piece silhouette design.
>
> It should read as **a hunched, wide-eyed owl with prominent ear tufts, glaring straight out** — unsettling rather than cute. Bold, clean, instantly recognizable as an owl.
>
> ### What the image means
>
> This becomes a **flat plate cut to this outline** and stood upright, like a theatre standee:
>
> - **BLACK = the object.** It is solid material. - **WHITE = removed.** It is air.
>
> ### Rules that matter
>
> **1. The black must be ONE connected piece.** Every black area must join every other black area. Nothing black may float detached — a detached piece is simply not part of the object and would fall on the floor.
>
> **2. The two eyes must be white holes fully enclosed by black.** Large, round, forward-facing, side by side, symmetrical about the centre line, and each one completely surrounded by black on all sides. They must not open out to the edge of the head or connect to the background.
>
> **3. Do not draw pupils, irises, highlights or any detail inside the eyes.** Leave each eye a clean, empty white shape. Colour and pupil are added separately afterwards.
>
> **4. The bottom edge should be broadly flat and horizontal** — the owl sits on a perch, so end it at the feet with a stable, roughly level base rather than a point or a curve.
>
> **5. It must be taller than it is wide.**
>
> ### What makes it creepy
>
> Favour: an oversized head relative to the body; eyes set wide and staring dead ahead; sharp ear tufts; hunched, compressed shoulders; a heavy brow; an outline with a few bold irregular feather lobes.
>
> Avoid: a friendly rounded cartoon owl; a tilted or three-quarter head; anything whimsical; a smile.
>
> ### Style
>
> - Bold vector graphic silhouette. Pure black on pure white, no greys. - Crisp hard edges. No shading, gradients, textures, lighting or perspective. - No background elements, no border, no frame, no perch or branch — the owl only. - The owl fills the image with a small even margin.
>
> ### Check before you answer, and state your answer to each
>
> 1. Is all the black one single connected piece? Name anything that is not. 2. Is each eye a white shape completely enclosed by black, with no path to the background? 3. Are the eyes empty — no pupils, no highlights, no detail? 4. Is the bottom edge broadly flat and horizontal? 5. Is it taller than it is wide? 6. Would someone shown only this, at a glance, say "creepy owl"?
>
> If any check fails, fix it and check again.

## When the image comes back

Validate before modelling — `ARTWORK.md` has the pipeline. Specifically:

- Confirm one connected black region, and exactly two enclosed white regions.
- Watch for stray specks. The cat artwork came back with a 3-pixel enclosed white region that would have become a pinhole.
- Simulate the nozzle and look at the result. At this size it should survive essentially untouched, and if it does not, something is wrong with the artwork rather than with the size.
- The eye apertures are ours to move. Trace them for position and shape, then treat their spacing as a parameter — spacing is what makes a face read as calm or startled, and it is worth a sweep.
