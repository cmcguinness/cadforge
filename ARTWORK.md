# Adapting artwork to a printed part

How a supplied silhouette becomes a motif that prints. Learned on `raven_lantern` and `witch_lantern`, both of which cost several laps to get right, and every lap taught the same lesson from a different angle.

Read this before tracing anything.

**Getting the artwork in the first place** is `chatgpt-prompts/TEMPLATE.md` — a manufacturability-constrained prompt for an image generator, with the derivation for its one computed number. The `cad-stencil` skill drives both ends: writing the prompt, and validating what comes back before any modelling happens.

## The rule everything else follows from

**Adapt the artwork to the part. Never the part to the artwork.**

A part's size is usually set by something outside the design's control — the object it holds, the space it fits, the machine that makes it. The canvas is therefore what it is, and any conflict between "what the artwork wants" and "what fits" is resolved by changing the artwork. Growing the part to preserve a detail is the wrong trade, and a seductive one, because it feels like respecting the design.

Two corollaries:

- **A generated reference image has no intent to preserve.** Wispy hair, feathered bristles, tapering claws — nobody chose those, and nothing depends on them. Simplify freely.
- **If a detail genuinely cannot survive**, say so and ask for the image to be regenerated chunkier. That is cheaper than redesigning the part around it.

The one case where the *part* legitimately grows is when the constraint that fixed its size changes — a larger object to hold, a different machine. That is a change to the world the parts live in, so it belongs wherever that world is described, and it moves every affected part at once. It is never a per-motif decision.

## The pipeline

1. **Trace it; do not draw it.** A hand-authored polygon looks hand-authored. The first raven was 17 points of guesswork and was visibly worse than a trace of the reference.
2. **Alpha-composite onto white before thresholding.** A silhouette PNG is usually RGBA with a transparent background. Converting straight to greyscale makes every transparent pixel *black*, so the trace returns the image border and nothing announces the error. Symptom: ink covers ~100% of the frame.
3. **Largest connected component, then fill holes.** Generated art carries stray specks; keeping the largest component drops them without judgement calls.
4. **Moore-neighbour boundary walk, then Douglas–Peucker.** A few thousand boundary pixels reduce to 100–200 points with no visible loss at print size. Keep an explicit backtrack direction in the walk or it terminates instantly.
5. **Normalise before storing.** Unit height, centred — or, when the motif has to sit inside a circle, translated to the centre of its **minimum enclosing circle** and scaled to radius 1. This is what keeps *one* size parameter meaningful, so editing a point changes the shape and never the size.
6. **Measure the narrowest features and store the figures next to the outline.** As a fraction of the motif's size, so they scale with it. These are what the printability assertions multiply.

## Judging printability

**Simulate the nozzle. Do not reason about it.** A morphological *opening* at the nozzle radius approximates what the machine can resolve, and rendering the result answers the question directly — no proxy metric required.

This is worth doing before any modelling, because it changes decisions. On the witch it showed the broom handle disappearing completely at the intended size, and the pose collapsing into "hunched figure holding nothing". No amount of staring at the source image would have revealed that.

**Beware area-based metrics.** "What fraction of the shape is thinner than the nozzle" sounds rigorous and misleads badly: every tapered tip and sharp corner contributes thin area, so the number never approaches zero and barely responds to scale. The witch went from 31% to 21% while growing 60% — because tapers taper, and no size fixes a taper.

**Watch the piece count.** Opening that splits a motif into two components means something detached. On the witch this caught the broom handle surviving as a *floating stick*, which is worse than losing it.

## The three operations

Applied in this order, and each for a different reason:

| operation | fixes | cost |
|---|---|---|
| **closing** | gaps *between* fine features — merges a fringe into a mass | detail becomes silhouette |
| **dilation** | features *too thin* to print | everything gets fatter |
| **cropping** | detail that cannot be rescued at any usable size | the feature is gone |

Three things learned the hard way about applying them:

- **Prefer merging to deleting.** A bird with legs and no feet reads as a *mistake*; a bird with slightly chunky feet reads as a bird. Removing a feature is not neutral just because it is the easy operation.
- **Dilate to a target width, not by an amount.** Specifying millimetres over-fattens a small motif and under-fattens a large one, because the traced feature scales with the motif. Express the target in nozzle diameters so it survives a change of machine. The raven's toes came out *thicker than its legs* from a fixed 0.3 mm — a proportion nothing but the eye would catch.
- **Region-limit the operation when only one region is at fault.** A uniform offset fixes the toes by bloating the beak and rounding the tail notch. Dilate the foot zone; leave the bird alone.

Do not over-merge. At a closing radius of 0.035 of her height the witch stopped being a witch — the hat deformed and the hair became a blob. 0.013 kept her readable. There is a window, and the only way to find it is to look.

## Choose motifs that read from their OUTER contour alone

The most useful thing to know before picking artwork, and it decides whether a motif is viable long before any of the operations below matter.

A shape whose legibility depends on **internal separations** does not survive being made small. Those separations are gaps, gaps have a width, and the width scales with the motif — so past a certain size they fall under the nozzle and close up, and the shape collapses into a blob that is still technically the right silhouette.

Compare two motifs at the same 19 mm:

- **A perched raven reads from its outline.** Head, beak, back, tail and legs are all boundary. Nothing about recognising it requires a hole *inside* it. It scaled down fine.
- **A witch on a broomstick does not.** What makes the pose read is her arm separated from her body, her hand gripping the broom, the hat clear of the hair. Those gaps measured **0.79 mm and 0.40 mm** — one marginal, one at exactly the nozzle. Merge them and she stops reading as a figure riding something and becomes a dark mass with a hat.

The witch was abandoned for this reason, after the artwork had been regenerated twice and the pipeline had done everything it could. **No amount of merging, dilating or re-tracing fixes a motif whose meaning lives in its interior**, because those operations work on the boundary and the problem is not the boundary.

So, when choosing a subject for a small canvas:

- **Prefer silhouettes recognisable as a filled black shape** with no interior detail at all. Squint at the reference: if it survives, so will the print.
- **Interior openings are fine when they are large and few** — a jack-o'-lantern face is several big separate holes, not a network of thin gaps, and each one is legible on its own.
- **Count the load-bearing gaps before committing.** If more than one or two interior gaps are doing the recognition work, expect to abandon it.
- A figure *interacting with an object* (riding, holding, carrying) is the classic trap: the interaction is always read from the gaps between them.

## Cropping cuts with a rectangle, not a half-plane

A horizontal cut at the belly line also takes the tip off the tail, because the tail hangs *lower* than the belly. Limit the cut in x to the region you actually mean to remove.

And the inverse error, made immediately afterwards: an x-limited cut is right for removing *legs* and wrong for removing *toes*, because the foot spreads either side of the leg. Trimming over the leg's x-range takes the front of the foot and leaves the back claw. Check what else lives at the height you are cutting.

## Cutout or retained material?

Both fail below the nozzle; they fail differently.

- **Cutout** (raven): the motif is the hole. Thin features are thin *slots*, and a slot under one nozzle diameter is not omitted cleanly — the slicer fills it with ragged gap-fill. Blobby ankles are worse than no ankles.
- **Retained material** (witch in a moon): the motif is what is left standing. Thin features are thin *plastic*. This inverts the risk usefully, and adds a new requirement: the motif must be **held on at two or more points**. One is a hinge, not a fixing.

Sizing a retained motif to slightly *exceed* its opening is the clean way to anchor it — the overhang merges with the surrounding wall, so contact is structural and looks deliberate. Far better than adding tabs after the fact.

## Repeated openings generate a shape you did not draw

A motif traced from an image is one hole. A row of holes is not — and the thing that gets recognised may be the **material between them** rather than the holes themselves.

`pumpkin_lantern`'s grin cost a print to learn this. Two rows of four triangles, apex-to-apex, separated by a thin waist: modelled exactly as intended, printed cleanly, and read as **three diamonds in a slot**. Each opposed pair fused into a lozenge; the waist became the horizontal band holding them. Nobody drew a diamond anywhere.

The cure is to break the pairing, not to shrink the features:

- **Interleave.** Offset the rows by half a period and give them different counts (four up against three down), so no two openings are ever aligned.
- **Overlap the rows** rather than butting them, so there is no straight horizontal band across the middle for the eye to find. Overlapping *increases* the minimum material width, because the strut between staggered holes runs diagonally.

**No assertion catches this.** The geometry was correct on every attempt, so the checks that fire on thin material, islands and bed fit all passed. It is a figure/ground judgement, and it belongs to the same family as the flying witch — arriving in a part where nobody was looking for it, because that part had no traced artwork in it at all.

The check that *does* apply: **render the motif as a two-tone flat at true size and look at it** before printing. That is where the diamonds were visible in hindsight and where the second attempt was confirmed.

## Assert the proportions, because renders are the only other check

Three bugs on `raven_lantern` had **appearance as their only symptom**. None touched validity, wall thickness, overhangs or bed fit:

- retaining bars placed at the *edge* of the counters they crossed (`Wire.center()` is not the centroid — it returned the right-hand edge);
- the tail squared off by a full-width crop;
- toes finishing thicker than the legs they hang from.

Where a proportion can be named, assert it. And measure the assertion on the **raw outline**, not the derived shape — otherwise every deliberate crop or dilation trips it, and people widen the bounds until it means nothing.

## One peak, or accept supports

The most useful predictor of whether a cutout motif prints support-free, and the cheapest to check — you can see it in the reference image before anything else happens.

**A valley in the top profile is a downward-hanging wedge of material.** Where the motif has two upward extremities, the panel between them descends into the opening from above, and its lowest point begins in mid-air. That is an island.

So:

| top profile | support-free? |
|---|---|
| **one peak** — a hat, a humped back, a single dome | yes |
| **two or more peaks** — raised arms, ears, horns, twin spires | no, structurally |

`raven_lantern` (one humped back) and `witch_lantern` (one hat) print clean. A ghost with **raised arms** has a valley between each arm and its head, and no prompt wording can remove them: "raised arms" and "no downward-hanging material" are contradictory requirements. Asking for both produced 38 islands.

This is not a veto. Supports handle it and come off cleanly on robust features. It is a **choice to make deliberately at the artwork stage**, when it is free, rather than discovering it at the slicer.

If support-free matters, ask for the subject in a pose with a single continuous rising outline — arms down, wrapped, or trailing.

## Islands: the failure a silhouette can hide

An opening's shape decides whether the **wall around it** can be printed, and the fatal case is an *island* — a layer where some material has nothing beneath it and no path sideways to an anchor. A notch in a motif does this: a wedge of wall pokes down into the opening and its lowest point begins in mid-air.

This is invisible in every other check and it is not the same as an overhang. `cad build` now tests for it directly. Two rules follow for choosing artwork:

- **Prefer motifs whose openings converge upward.** If the opening is widest at the top and narrows downward, material closes over it progressively from both sides. `tealight_holder`'s hearts are point-down for exactly this reason.
- **Watch for notches and re-entrant tips.** A curled hat brim, a crescent, a hooked tail — anything that makes the wall reach down into the hole.

Islands can be removed automatically by merging them into the opening, which costs a little detail and is deterministic. Do it at layer resolution, since the question is about rows of layers — but apply the fill at full resolution, or the silhouette comes back blocky.

## Supports: a decision, not a default

For a part whose surfaces are seen — or backlit — support removal is a force nothing in the model can see, and the safest answer is a shape that does not need them. For a part nobody looks at, supports are simply cheap. Decide deliberately.

`raven_lantern` lost its lettering to support removal. The letters required supports; the supports had to be pulled out of the letter openings; pulling them out destroyed the webs holding the letters together. **The feature and the thing that killed it were the same feature.**

Strengthening the webs could not have helped, because the load only existed because the letters did.

So: if a motif needs supports, reconsider the motif. Every opening in a vertical wall bridges across its own top the way a circular hole does, and a motif that respects that needs no supports at all — which the lettering-free raven confirmed. Support removal is a force nothing in the model can see.
