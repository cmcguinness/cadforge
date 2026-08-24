# examples

Eight printed parts, all carrying their real record rather than a tidied one. They come in five sizes of lesson:

- **[`castle`](castle/)** — one large, complicated object. 136 × 92 × 178 mm, eleven hours, internal chambers, traced artwork and coursed stonework. Read this one for how the process holds up when a part is too big to hold in your head, and for a print that failed for a reason that was never in the model.
- **[`mini_castle`](mini_castle/)** — the same castle at half size, as a **variant rather than a fork**: its `model.py` loads the castle's by path and subtracts two boxes, so it holds no geometry of its own and cannot drift. Read it for what happens when a scaled part meets a component that does not scale with it.
- **the Halloween lantern set** — four small ones that are deliberately *one body with four motifs*, so the thing that differs between them is the thing you would change to make your own.
- **[`castle_base`](castle_base/)** — ground for the castle to stand on, and the first part here that must **fit** another: moat, forecourt, a drawbridge on a printed pin hinge, and a sign you can put your own name on. Read it for the `assemblies/castle_ground.py` contract — the numbers along the cut between two parts that are really one object — and for a peg-in-socket fit recorded from both edges of its window rather than as a number that merely worked.
- **[`owl`](owl/)** — a standalone, and the only part here that is not a hollow object with a light inside it. A flat silhouette plate glued into a branch, lit from behind by a puck on a shelf. Read it for what happens *after* the print: the paper behind an opening turns out to be a finishing surface, and the light source turns out to have an orientation nobody modelled.

Everything here builds from a clean clone. You do not need a printer configured to try it:

```bash
./cad build ghost_lantern      # writes build/review/sheet.png, prints its path
```

Without `printer.toml` the harness runs on generic defaults and says so on every command — bed fit and mass will be answering for a machine nobody owns. That is fine for looking. Run `./cad setup` before trusting a number.

## castle — the big one

A haunted castle facade lit from behind by tea lights: four tiers on a declared 1:120 scale, a face whose gate is a seven-toothed iron portcullis, a bat traced from supplied artwork in a great arched window, megalithic coursed stonework and tiled roofs. It is the part to read if you want to see the process carry something substantial rather than something neat.

Three things it teaches that the lanterns cannot:

- **An eleven-hour print failed, and the model was never at fault.** A tree support headed for the second floor collapsed partway up the *first*. The cause was a slicer setting — `support on build plate only`, which sounds conservative and on a hollow part is the opposite, because chamber floors are model material and the setting forbids a support from standing on one. Same mesh, four settings changed, perfect print. `prints.md` has the column-height arithmetic; `../SLICING.md` has the general form.
- **Geometry sized from one constraint and never checked against its surroundings** is a single recurring bug wearing six costumes — crenellations cut full depth, a platform punched through a side wall, masonry grooves sawing through walls they did not belong to. `notes.md` names the pattern and the assertions that now catch it. That section is worth reading even if you never build anything remotely like a castle.
- **A render cannot show surface texture at whole-part zoom.** The review sheet showed smooth walls while the mortar was being cut correctly, because the renderer's depth-jump threshold scales with the view. Detail needs detail crops, and believing an undated or unzoomed render is its own failure mode.

It also shows the rule that an import is not membership: it reads the lantern project's measured `PUCK` without joining the set, because it does not share the set's envelope or standards.

**It is done, and one criterion was abandoned rather than met.** The turret shafts were never lined and their windows stay dark; the spec says so explicitly instead of leaving the box unticked, because an unmet criterion and an abandoned one are different things and only one of them is a defect. A published part that records what it gave up on is more honest than a tidied one.

## mini_castle — the same object, half size

The castle at 50%, with its two internal floors removed so the three chambers become one tall cavity that a single tea light stands in. 68 × 46 × 89 mm, 23 g, two hours against eleven.

**Its `model.py` contains no geometry.** It loads `castle/model.py` by path and subtracts two boxes — that is the entire part. Worth reading if you want a variant that cannot drift from its parent: there is no copy of the castle's 1858 lines to keep in sync, and a fix to the castle lands here for free. The cost is that it can only ever be the castle plus a difference; wanting proportions of its own would make it a separate part.

Three things it teaches that the castle does not:

- **Derive the quantity that matters, not the inputs.** "Is it big enough at half size?" has no answer. "Is any single dimension short?" does — and the answer was not the obvious one. The ground floor accepts a 35 mm puck comfortably; its clear *height* is 22.6 mm against a puck 30 mm tall. Footprint was never the problem.
- **A scaled part does not scale its contents.** Everything halves except the tea light. That asymmetry drives the whole design and is invisible while you are working.
- **The finished object is not the one that was designed.** It was built around an upright puck whose opaque base was expected to swallow the gate. At the bench the puck was laid on its side, aimed at the face, because it lit better — and the gate became the brightest thing on the object. `prints.md` records a prediction that was wrong in both directions and why, which is more useful than the part.

## The lantern set — the one idea each is here for

Read one README, then that part's `prints.md`. The print log is where the process earns its keep; the rest is scaffolding around it.

| | the idea worth taking |
|---|---|
| [`raven_lantern`](raven_lantern/) | **A feature and the thing that killed it were the same feature.** Lost a *Nevermore* inscription: letter counters need webs, webs are single-extrusion, and single extrusions do not survive support removal. |
| [`witch_lantern`](witch_lantern/) | **Supports are judged by what they touch.** The set's blanket no-supports rule came from the raven, and was wrong — this printed *with* supports and they came off clean. Over-generalising from one failure is itself a failure. |
| [`ghost_lantern`](ghost_lantern/) | **Inverted polarity.** A motif that reads from its outer contour can be the hole; one whose recognition lives in its interior cannot. A ghost is a blob without its face, so the ghost is the material and the face is the holes. |
| [`pumpkin_lantern`](pumpkin_lantern/) | **Wall thickness as an optical parameter.** This one *glows* rather than silhouettes, which makes the wall a filter rather than a boundary — a different job for the same number. |

Every part here — castle included — is the same seven files, and the reading order inside one is:

| file | what it is |
|---|---|
| `spec.md` | what it is for, and the acceptance criteria — **the durable artifact** |
| `notes.md` | why the numbers are what they are |
| `prints.md` | what happened when it met the physical world |
| `model.py` | the geometry. Disposable by design |
| `inspiration/` | the artwork the part was traced from |
| `accepted/` | the frozen deliverable: the mesh that was actually printed, its parameters, and the exact generator that made it |
| `trace_*.py` | for the traced motifs: turns `inspiration/<name>.png` into outline data. Re-runnable |

One file is missing from that list on purpose. A part also keeps a `history.md` — every iteration, every parameter changed, every verdict — and it is arguably the most useful thing in a working part. It is **not published**, because one dated row per build describes the author's calendar rather than the design. Dates are stripped from what does go out, too. See [`../PRIVACY.md`](../PRIVACY.md); if you are running your own fork, the same applies to yours.

`accepted/` is the one directory here that a spec revision cannot regenerate. If you only want to print a lantern, take the STL from there and stop reading.

## What the lanterns share

The set is a **project**, not an assembly — the lanterns do not fit each other, they merely have to look like siblings on a shelf. What they share lives in [`../projects/halloween_lantern/`](../projects/halloween_lantern/):

- **`project.md`** — what is settled for the whole set, and why.
- **`shared.py`** — the numbers every member reads: the puck, the envelope, and the derived datums.

Read `shared.py` before writing a fifth lantern. It is short, and its docstring carries the fact the whole set turns on:

> A flame-style LED tea light is not a glowing disc. It is an **opaque base** with a narrow **translucent flame** standing on top, and the LED sits inside the lower part of that flame.

That gives the motif band a lower bound *and* an upper bound. An opening below the opaque base is a dark hole with grey plastic behind it; an opening far above the flame has nothing in line of sight. Both fail the same way — silently, and only once printed and lit. `lit_window()` is that band, and it is the scarce dimension in every part here.

Two more consequences worth knowing before you design against it:

- **Height is an input, not an output.** It used to be motif height plus margins, so a lantern with a bigger motif came out taller and a shelf of them stepped up and down for reasons about the artwork rather than about the set. Now the rim is the datum, the motif hangs from it, and a motif that will not fit the lit space is a **build failure** instead of a silently taller lantern.
- **The paper liner is a design element, not an accessory.** A 10 mm flame is nearly a line source; the rolled paper intercepts it and re-emits over its whole surface, turning it into a lit column. That is what makes a motif band taller than the LED viable at all. It also takes up the slack in the bore — so do not tighten `fit` to cure a rattle. A rattle is much cheaper than a puck that will not go in, which is a mistake this set has already paid for once.

## Making a fifth

The body is done. A new lantern is a **motif and its constraints**, which is perhaps 200 lines — `witch_lantern/model.py` is the one to copy, at 218.

```bash
./cad new bat_lantern --project halloween_lantern
```

That scaffolds into `parts/`, which is git-ignored — your designs stay private without leaving the working directory. It is the right place; `examples/` is for things published deliberately.

**1. Get the artwork.** If the motif comes from an image rather than from construction geometry, read [`../ARTWORK.md`](../ARTWORK.md) first. The short version: settle **polarity** explicitly (black-as-hole is the default; `ghost_lantern` is the deliberate exception and its README says why), and ask whether the subject needs a **face** — a face is interior detail, and interior detail is what fails at this size. `chatgpt-prompts/TEMPLATE.md` is the prompt; save yours beside it so its failures are on the record too.

**2. Trace it to data, once.** Copy `witch_lantern/trace_head.py`. It walks the boundary, closes the finest features at a nozzle-derived radius, simplifies, and writes a `*_outline.py` module normalised to height 1.0 and centred in x. The model imports that module, never the image — so a build never depends on a file outside the repo.

**Put the source in the part's own `inspiration/` before you trace it**, and read it as `Path(__file__).parent / "inspiration" / "<name>.png"`. `raven_lantern`'s artwork pointed into a per-session chat cache and is gone, so that outline can now only be edited as coordinates, never re-traced against what it was meant to look like. A part traced from a picture is not described without the picture.

Judge printability by **simulating the nozzle** — a morphological opening at the nozzle radius — and looking at the result, not by reasoning about feature sizes. The witch keeps 98.4% of her area at 19 mm tall; the abandoned witch-on-a- broomstick did not, and the difference is entirely "does it read from its outer contour".

**3. Write the model.** It needs `PARAMS`, `build(p)`, and — read the existing ones for the shape of it:

```python
from projects.halloween_lantern import shared as body

def geometry(p):          # every derived value, in ONE place
    ...                   # build() and check() both read this, so an
                          # assertion can never check different arithmetic
```

Take `inner_r()`, `outer_r()`, `motif_top()` and `lit_window()` from `body`. Do not choose height, bore, wall or the motif datum — they are not a part's to choose, and a lantern that picks its own stops being a member of the set.

**4. Write the assertions that matter.** Every model here carries one load-bearing check, and it is the same one in different clothes: *the motif sits inside the lit window*. Copy its error message too — it tells you how much lit wall exists, how much the motif wants, and which of the two to change.

The generic checks (`cad build` runs validity, bed fit, overhangs, islands) will not catch a lantern that is built perfectly and lights nothing. Neither will a render. Assert the **derived** quantity — the lit band, the rib between openings, the open fraction of the wall — rather than the raw parameters. Each input can look sensible while the space between them is nothing.

**5. Then the loop.** `cad build`, look at `build/review/sheet.png` against your criteria, say what is wrong, and `cad accept` when it is right. `cad next` tells you what comes next at every point, so nobody has to work it out.

### Things the set has already ruled out

Read the four `prints.md` files before spending a print on any of these:

- **Lettering.** Counters need webs; webs are single extrusions; they tear off with the supports. `raven_lantern` lost *Nevermore* this way.
- **A blanket no-supports rule.** Generalised from that failure and wrong — `witch_lantern` printed with supports and they came off cleanly. Supports were the occasion, not the cause.
- **Interior-detail motifs at this size.** Gaps of 0.4–0.8 mm — arm from body, hand from broom — do not survive. Silhouettes that read from the outer contour do.
- **Tightening `fit` to cure a rattle.** 0.6 mm was modelled, printed, and the puck would not go in. It is 1.6 mm now and the liner takes the slack.
- **Too many openings.** Every opening is a gap the nozzle jumps on each layer of the band, and that is where the raven's stringing came from. Five heads is a ring; the geometry allows about seven before it becomes a colander.

One that was a *material* fact rather than a geometry fact, and so is filed in [`../SLICING.md`](../SLICING.md) instead: the residual stringing went away at 210 °C rather than 220. Try temperature first.
