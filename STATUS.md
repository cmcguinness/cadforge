# cadforge — status

The public repo: the harness and the worked examples. Personal parts live in the private `parts/` collection and have their own STATUS.md there — see `PRIVACY.md` for the arrangement.

## Where things stand

2026-08-24.

| | |
|---|---|
| `cadkit/` | complete and exercised; carries projects and an islands check |
| `examples/` | **eight parts**, printed and done — four lanterns, castle, mini_castle, owl, castle_base |
| `projects/` | `halloween_lantern` — public, four published members, all done |
| `examples/assemblies/` | `castle_ground` — the castle / castle_base interface, the first shared assembly |
| docs | README, CLAUDE.md, PRIVACY.md, ARTWORK.md, SLICING.md, cadkit/README.md, four skills; MIT licence |

`./cad status` is the live view.

### The Halloween lantern set — four for four, all published

All four printed, accepted and promoted to `examples/`. Each carries a README telling how it actually went, with nothing tidied away: the ledgers, the failed features and the corrections are all present, because an example that hid its record would demonstrate a cylinder rather than a process. One body, one motif each, all hanging from the same rim datum so they line up on a shelf.

- **`raven_lantern`** (public) — six ravens. Lost a *Nevermore* inscription on the way; the lettering machinery is still in the model with `text` empty.
- **`witch_lantern`** (public) — five heads in profile. Passed UAT: someone who had not been told what it was said "witch".
- **`ghost_lantern`** (public) — four ghosts in lit windows, **inverted polarity**. The only one where the motif is the material rather than the hole, and the only one that needed no rework.
- **`pumpkin_lantern`** (public) — a jack-o'-lantern that drops over the puck. The odd one out: it **glows** rather than silhouettes, so wall thickness is an optical parameter and the ribs undulate the whole wall rather than being grooves cut into it. Three prints, one killed from the slicer preview.

### What the set actually taught

Most of it is not about lanterns, and has been filed accordingly:

- **`ARTWORK.md`** — turning a supplied image into a printable motif. Adapt the artwork to the part, never the reverse; simulate the nozzle rather than reasoning about it; prefer motifs that read from their outer contour; one peak or accept supports.
- **`SLICING.md`** — settings the harness cannot see, organised by scope (machine / material / geometry) so a machine fact is not re-derived per project.
- **`chatgpt-prompts/`** — a manufacturability-constrained prompt template for generating motif artwork, plus the `cad-stencil` skill that drives it.
- **`inspiration/` inside every part** — because the raven's source was lost to a per-session cache before anyone noticed, and its outline can now only be edited as coordinates.

The pumpkin added two constraints that only exist for a **hollow lofted shell** and are now assertions rather than prose: a shell cannot change radius faster than its wall is thick (`|dr/dz| × layer_height < wall`, or the rings arrive as loose hoops), and equal radius where two profile curves meet is not tangency — the equator is the widest point, so its slope must be zero or a crease runs right around the part. It also contributed the figure/ground finding in `ARTWORK.md`: **repeated openings generate a shape nobody drew**, and no check can see it because the geometry is correct.

### Harness changes, 2026-08-06 — all from driving it hard on one part

Five, and four of them are the same lesson: **this harness was calibrated for a human-paced loop and an agent runs it very differently.**

- **`cad build` no longer opens the render sheet.** It printed a path and then threw an image viewer over whatever the human was doing — on a cadence they do not control, dozens of times a session. That is not helping someone review, it is taking their attention by force. `--open` if you want it.
- **The stall counter counted builds, not evaluations.** `history.laps` treated `untested` as a lap, so a part being worked on quickly tripped "revise your criteria" having consumed no human attention at all — the advice fires hardest exactly where it least applies. It counts only judged-and-rejected iterations now, and `STALL_AFTER` went 5 → 15.
- **The islands check gave up on large parts** rather than coarsening. It went quiet mid-design on a part whose towers were being moved around every build, which is precisely when islands appear. It now widens the grid until it fits and reports the pitch it used.
- **Render size 520 → 900 px per view.** 520 was chosen when the sheet was glanced at. It is read closely; at that size a crenellation is four pixels and a mesh artefact is none.
- **Every view carries an A–H / 1–8 reference grid**, so a review can say "the face at C6" instead of describing where it is in prose.

### Open threads

- **Three near-identical `model.py` files**, now all public. The band-of-cutouts builder should be promoted into the project's `shared.py`; `ghost_lantern` differs only in cutting a list of openings where the other two cut one.
- **The rib rule is a guess with its evidence attached** — two thirds of the motif width, bracketed by one accept (0.77) and one reject (0.41). A metric measuring *actual closest approach* rather than bounding boxes would let one number cover all three motifs.
- **Why the bore printed undersize** is still unattributed: an unmeasured lip on the puck, bores printing undersize on this machine, or 0.6 mm simply being optimistic. The middle one would be a machine fact.
- ~~**`cad promote` copies files, not directories**, so `accepted/` had to be carried by hand.~~ **Fixed 2026-08-06** — it now carries `accepted/`, and only that: `build/` stays git-ignored. Publishing an example without its accepted mesh ships the recipe and not the dish, and `model.py` is disposable by design.
- **Two private parts still carry unticked criteria on a `done` stage** — `tealight_holder` (9) and `bench_tray` (5). Both predate the classified criteria sections and both work; the ledger is behind the world. `cad next` now says so instead of advising a reprint.

## What was built

- **Headless renderer** (`cadkit/render.py`) — tessellate → numpy z-buffer → PNG, with silhouette and crease edges; four orthographic views plus a cutaway on a contact sheet. No VTK, no GL, ~0.1 s per view. Review is an artifact anything can open, rather than a person watching a live viewer.
- **Part contract** (`cadkit/part.py`) — `build(p) -> Part`, nothing on import. Optional `check`, `pieces`, `SECTION`, `PRINT_ROTATION`. Two collections, public and private, treated identically.
- **Iteration history** (`cadkit/history.py`) — automatic parameter diffing and an oscillation guard that fires when a previously-judged parameter set comes back. Verified working.
- **Printability checks** (`cadkit/check.py`) — validity, bed fit, planar overhangs, mass. Explicit about what it does *not* check (true min wall).
- **`cad` CLI** — status / next / new / build / watch / accept / history / stage / sweep / promote.
- **Next-action engine** (`cadkit/advise.py`) — an ordered decision procedure over what is on disk. Every state-changing command ends by printing the one next move; `cad status` shows the board. The premise is that working out what to do next is itself a tax on the scarce resource (human attention), so the harness pays it.
- **Criteria classified by axis** — function / construction / print. An unstated axis stays unconstrained however precise the others get, so an empty function section is flagged as urgent rather than passing silently.
- **Generations** — the acceptance criteria are hashed. Editing them moves the target, which opens a new lineage: verdicts and the oscillation guard do not compare across the boundary. Enough rejected laps without a `good` (`STALL_AFTER`) and `cad next` says to revise the criteria rather than the parameters.
- **`accepted/`** — a good or printed verdict freezes the mesh, its params, the render sheet and the exact `model.py` that produced it, git-tracked. `model.py` is disposable and gets rewritten on a respec; without this the printed object is unreproducible.

## The model this is built on

Designing a part is a search; the human is the objective function. Generating candidates is cheap, evaluating them is not, and their attention is the scarce resource. Criteria make evaluation repeatable, assertions remove evaluations entirely, renders make evaluation possible for a reviewer with no viewer, history stops the search circling, and `cad next` removes the cost of deciding what to do next. `CLAUDE.md` states this in full — it is the thing to read before changing how the process works.

Consequences that contradict ordinary software instincts: `model.py` is disposable (the STL is the deliverable), convergence matters and reproducibility does not, and spec detail helps only when it constrains the *outcome* rather than the *method*.

## Open threads

- **Nobody has followed the README from a fresh clone and an empty venv.** The clone itself is verified; the `pip install` path is not.
- ~~**GitHub reports 13 Dependabot advisories** against the pinned wheels.~~ **Closed 2026-08-24** — Pillow 12.3.0 patched them all; the alert list is empty.
- **Minimum wall thickness is not checked** and there is no cheap, reliable way to do it. Thickness invariants belong in each part's `check()`.
- **The overhang check reports small planar faces** on many parts. They are warnings by design, but the threshold has never been tuned against a real print.
- **`STALL_AFTER = 15` is a guess.** It counts judged-and-rejected iterations only (see the 2026-08-06 harness notes above), but the number has never been calibrated against a real refinement run.
- **The ported specs predate the classified criteria sections.** Their criteria parse as `unclassified`, which suppresses the empty-function-axis warning. Any spec that gets revised should be split into the three axes.
- `cad sweep` only varies one parameter at a time. Two-parameter grids would be a natural extension and are not implemented.

## A failure worth keeping

The first attempt at a public example was a desk-edge clip with a hook to hang things from. The hook was a bare downward tab with no crook, so it could not hold anything at all. It was removed at Charles's request — but the way it got that far is the useful part, and the lesson is now in `CLAUDE.md`:

Every assertion passed. Every printability check passed. The render was reviewed and matched the drawn profile exactly. The spec had seven acceptance criteria and **not one asked whether the part could hold an object** — they were all geometric invariants. Review then confirmed the shape was the shape that had been meant, which is a different question from whether the right shape had been meant.

`CLAUDE.md` now requires functional criteria to come first, and to be asserted against *derived* quantities (the usable opening, the remaining clearance) rather than raw parameters, since each input can look sensible while the space between them is nothing.

## Next session

Read `CLAUDE.md` for the process, then `./cad status`.

The Halloween set is closed and four more parts have been published since (castle, mini_castle, owl, castle_base — the last two sharing the `castle_ground` assembly); the loop has now been round many times for real rather than backfilled. The repo is being readied to go public, and its history was squashed to a single commit first: the early examples were published before the date scrubber and the ledger withholding existed, so the record `PRIVACY.md` promises to keep private was reachable through `git show`. The highest-value moves left are the ones the set kept deferring:

- **Fold the band-of-cutouts builder into `projects/halloween_lantern/shared.py`.** Four near-identical `model.py` files are now public, and three of them differ only in which openings they cut. The pumpkin is genuinely different and should stay as it is.
- **Verify the README from a fresh clone and an empty venv** before pointing anyone at the repo.
- **Replace the rib rule's bounding-box metric** with actual closest approach, so one number covers all four motifs instead of a guess bracketed by one accept and one reject.
