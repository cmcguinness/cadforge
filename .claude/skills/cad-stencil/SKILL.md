---
name: cad-stencil
description: Get artwork for a motif that will be cut through a part, by writing a manufacturability-constrained prompt for an image generator and then validating what comes back. Use whenever a part needs a silhouette, stencil, or cutout shape. Triggers on "stencil", "silhouette", "cutout", "motif", "make a ghost/bat/pumpkin design", "prompt for ChatGPT".
---

# Getting artwork that can actually be made

The user generates motif artwork with ChatGPT. Your job is the two ends of that: **write the prompt**, and **validate what comes back**. The image generator is good at pictures and blind to manufacture, so every constraint has to be stated, and stated concretely.

## Recognise the moment

Reach for this when a part needs a shape cut through it — a lantern motif, a stencil, a pierced panel — and the shape is going to come from an image rather than from construction geometry. Also when the user is *already* iterating on a prompt: they will paste a draft, and the useful contribution is a rewrite plus the reason for each change.

## Do this

1. **Read `ARTWORK.md` at the repo root**, which carries the pipeline and the rules. Read `chatgpt-prompts/TEMPLATE.md`, which is the prompt itself.
2. **Establish the numbers before writing anything**: the motif's finished height in mm, and the nozzle. `{{MIN_PCT}}` is derived — `100 × 3 × nozzle ÷ height`, rounded up — not guessed. For a part in a project, the height usually falls out of the project's envelope.
3. **Settle polarity explicitly.** Black-as-hole is the default and has printed twice. Subject-as-retained-material needs anchoring to the panel at three or four points and was abandoned once; do not choose it casually.
4. **Ask whether the subject needs a face.** A face is interior detail, and interior detail is what fails at small size. If the silhouette carries the recognition alone, dropping the face removes the hardest constraint.
5. **Fill the template and save it** to `chatgpt-prompts/<subject>-cutout.md`, so the prompt and its failures are on the record like everything else. Hand the user the text to paste.
6. **When the image comes back, validate it before modelling.** Do not skip to geometry — this is where a wasted afternoon gets caught for the price of a minute:
   - alpha-composite onto white, threshold, largest component;
   - **connectivity** — any white region enclosed by black is a loose chip;
   - **nozzle simulation** — morphological opening at the nozzle radius, then *look at the result at true size*, not enlarged;
   - **islands** — rasterise at layer resolution and check that no row has material with nothing beneath it and no path sideways to an anchor.
7. **Show the user a true-scale two-tone flat.** Never a magnified view and never the grey render sheet: a shaded solid gives motif and wall the same tone, so a figure/ground design dissolves in it. A motif approved at 5× has already failed here once.

## The failure to check first

**White floating inside black.** It is the most likely single defect, because the generator's prior for a face — two eyes and a mouth inside a head — is exactly the forbidden shape, and an abstract prohibition loses to that prior.

Naming the failure in the prompt, giving a concrete alternative, and ending with a checklist is what makes it stick. Stating the rule once, politely, does not.

## Do not

- **Do not fix a bad motif by growing the part.** Part size is set by what it holds. Artwork adapts; the part does not.
- **Do not accept "it will be fine at print size".** Simulate it and look.
- **Do not treat the slicer's warning as noise.** It is ground truth, and it has been right against this repo's own analysis more than once. `cad build`'s islands check is an early warning, not a substitute.
- **Do not iterate on the artwork more than about twice.** If a subject keeps failing, the subject is wrong, not the prompt. A shape whose recognition lives in its interior cannot be rescued — see `ARTWORK.md`.
