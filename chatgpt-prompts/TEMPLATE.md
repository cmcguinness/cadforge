# Stencil-prompt template

A reusable prompt for asking an image generator for artwork that will become a **cutout in a 3D-printed panel**. Fill the placeholders, paste the result into ChatGPT, then run the returned image through the pipeline in `ARTWORK.md`.

Every rule below was paid for by a failed or cancelled print. Do not trim them on the grounds that the model "should know" — it demonstrably does not.

## How to fill it in

| placeholder | what to put | example |
|---|---|---|
| `{{SUBJECT}}` | the thing, in a few words | `a terrifying Halloween ghost` |
| `{{CHARACTER}}` | what makes it read, one sentence | `flowing spectral form with raised arms and trailing robes` |
| `{{HEIGHT_MM}}` | finished height of the motif | `19` |
| `{{MIN_PCT}}` | min feature as % of height — `100 × 3 × nozzle ÷ height`, rounded up | `7` |

**Derive `{{MIN_PCT}}`, do not guess it.** Three extrusion widths is the floor for something that has to survive handling. At a 0.4 mm nozzle and a 19 mm motif: 3 × 0.4 ÷ 19 = 6.3% → state 7%.

## Two things to decide before sending

**1. Polarity.** Two options, and the choice is decided by **where the subject's recognition lives**.

**Polarity A — subject is the hole.** Black = removed. The subject glows; the panel stays dark. `raven_lantern` and `witch_lantern` use this and it has printed twice. The template below is written for it.

Correct when the subject **reads from its outer contour**: a bird, a bat, a gravestone, a face in profile — where nose, chin and brow are all outline.

**Polarity B — subject is the material.** A black *window* is removed, and the subject stands inside it as retained material. It reads as a dark shape against light. Any hole *inside* the subject — an eye, a mouth — is then topologically free, because a hole in material is just a hole.

Correct when the subject's recognition **lives in its interior**. A ghost is the example: a faceless ghost is a blob, and under polarity A its eyes must be floating chips. Under B they are simply holes, and it reads better — a dark ghost with *glowing* eyes.

The cost of B is **anchoring**. The subject must touch the window's edge, and critically **at the bottom**, because support propagates upward: a subject touching only the sides or top begins in mid-air. Drapery, robes and trailing forms make this natural; a compact figure does not.

B was abandoned once on a flying witch — but for a reason that was about *her*, not about B: her pose needed thin interior gaps at 0.4–0.8 mm. Judge it on whether the subject has large interior features and something that reaches down.

See `ghost-cutout.md` for a worked polarity-B prompt.

**2. Whether it must print support-free.** A **valley in the top profile** is a downward-hanging wedge of panel, and every valley is an island. One upward extremity (a hat, a humped back) gives none; two or more (raised arms, ears, horns) give one per gap, unavoidably. If support-free matters, ask for a pose with a **single continuous rising outline** — and do not also ask for raised arms, because the two requirements contradict each other. If supports are acceptable, ignore this and let the pose be what it wants to be.

**3. Whether the subject can carry a face.** A face is interior detail, and interior detail is the thing that does not survive being made small. If the silhouette can carry the whole recognition on its own, say so and drop the face entirely — it removes the hardest constraint in the prompt.

---

## The template

> Create {{SUBJECT}} as a **single-piece stencil design**, not an illustration.
>
> It should read as {{CHARACTER}}. Bold, clean, and instantly recognizable.
>
> ### What the image means
>
> This becomes a **cutout in a flat panel**, so the two colours are not decoration:
>
> - **BLACK = the hole.** It is removed. The subject is the empty space, and light shines through it. - **WHITE = the panel.** It is solid material that must physically hold together and must survive being built up in horizontal layers from the bottom.
>
> ### The size it will actually be
>
> The finished design will be about **{{HEIGHT_MM}} mm tall — smaller than a thumbnail.**
>
> - It must be recognizable **at that size, by someone who has not been told what it is.** - **Recognition must come from the outer silhouette alone.** No interior detail may be doing the work. - Proportions: about as wide as tall, **or taller than wide. Never wider than tall.** - **No feature — black or white — may be narrower than {{MIN_PCT}}% of the overall height.**
>
> ### The failure to avoid above all others
>
> **Do not draw any white shape floating inside the black.** The most common version of this is a face: two white eyes and a white mouth sitting inside a black head. Those are not features, they are **loose chips that fall out of the panel**, and a design containing them is scrap.
>
> This is the single most likely way to get this wrong. Check it explicitly before you answer.
>
> ### Manufacturing rules — these outrank the artwork
>
> **1. Every white shape must be connected to the white background.** Trace a path from any white pixel to the edge of the image without crossing black. If you cannot, that white is a loose chip.
>
> **2. White must never hang downward.** The panel builds up in layers from the bottom, so white always needs white beneath it. - Where white reaches into the black, it must **rise from below**, run sideways, or come in from the side. - **Never descend from above like a stalactite.** - **No downward-pointing white point, spike, wedge or V-notch anywhere.** Upward-pointing ones are fine. - So: notches in the subject's outline may open **upward**, never **downward**.
>
> **3. If the design has a face, build it from bridged shapes.** Each eye or mouth must be joined to the white outside the subject by a **broad white bar that runs inward and slightly UPWARD from the edge**, so the feature sits at the top of its own bridge and everything beneath it is solid. Make the bars obvious and at least as wide as the minimum feature size — they should look like a deliberate part of a stencil.
>
> **If you cannot do this convincingly, omit the face entirely** and let the silhouette carry the design. That is a better answer than floating eyes.
>
> **4. Ceilings must not begin in mid-air.** A span of white anchored at both ends is fine, however wide — that is a bridge and it prints well. What fails is white that *starts* over open space with nothing on either side.
>
> **5. Prefer a single peak.** The top of the design should rise to **one** high point, not two or more. Every dip between two high points becomes a weakness in the panel. (Skip this if supports are acceptable.)
>
> **6. Favour vertical edges, steep slopes, sweeping curves and tapered forms.** Avoid long shallow near-horizontal edges on the undersides of white shapes.
>
> **7. Blunt, not ragged.** Suggest irregularity with **a few large, rounded lobes** — never fine tatters, wisps, tendrils, spikes or delicate fingers.
>
> ### Style
>
> - Professional stencil; bold vector graphic. - Pure black on pure white. No greys. - Crisp hard edges. No shading, gradients, textures, lighting, perspective. - No background elements, no border, no frame. - The subject fills the image with a small even margin.
>
> ### Check before you answer
>
> Go through these one at a time and state your answer to each:
>
> 1. Is every white area connected to the white background? Name any that is not. 2. Are there any downward-pointing white spikes, wedges or notches? 3. Is every feature at least {{MIN_PCT}}% of the height in width? 4. Is it taller than it is wide, or square? 5. Would someone shown only this, at thumbnail size, say what it is?
>
> If any check fails, fix it and check again. **When appearance conflicts with manufacturability, always favour manufacturability** — a simpler design that can be made beats a beautiful one that cannot.
