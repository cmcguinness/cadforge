# cadforge — project conventions

Parametric CAD in Python, organised around a design process rather than a pile of scripts. Read this before writing or editing a part.

## The model this repo is built on

Designing a part here is a **search**, and the human is the **objective function**.

Generating a candidate is cheap. Evaluating one is not: only a person can say whether a shape is the shape they wanted, and every evaluation spends a judgment call that does not get cheaper with practice. Their attention is the scarce resource, and every component here exists to spend less of it:

| Component | What it is, in those terms |
|---|---|
| `spec.md` acceptance criteria | The objective function, written down. Editing them **moves the target**; the harness calls that a new *generation*. |
| Assertions in `check()` | The fraction of the objective that got compiled into code — evaluated forever after without spending a human. |
| `build/review/sheet.png` | Makes evaluation possible for a reviewer who cannot open a viewer. |
| `history.md` | A tabu list. Stops the search re-entering a basin it already left, which is the only way successive approximation degenerates into a random walk. |
| `cad next` | Removes the last tax: working out which move comes next. |
| `notes.md` | Knowledge that survives a regeneration. Geometry resets on a respec; hard-won physical facts must not. |

Three consequences worth internalising, because they contradict ordinary software instincts:

- **`model.py` is disposable and that is fine.** The deliverable is an STL. Once a mesh prints and works, how it was produced has no further claim on anyone. Regenerating from a revised spec costs minutes, not months — so nondeterminism between runs is not a defect, it is exploration.
- **Convergence is the only property that matters.** Not reproducibility. A search that reaches an acceptable object has succeeded regardless of the path. A search that circles has failed regardless of how reasonable each step was.
- **Detail in a spec is only useful when it constrains the outcome.** Detail that prescribes the *method* does not narrow the search, it replaces it — and over-prescribed specs measurably produce worse parts. The test: does this line change what counts as success, or just how to get there?

## The process

Every part moves through five declared stages. The stage lives in the part's `spec.md` front matter and is changed deliberately with `cad stage`, never inferred from which files happen to exist.

```
  spec  ──▶  model  ──▶  review  ──▶  print  ──▶  done
   ▲                        │           │
   └────────────────────────┴───────────┘
        refinement loops back, and the history remembers
```

| stage | what is happening | what ends it |
|-------|-------------------|--------------|
| `spec` | Intent is being written and refined. No geometry. | The acceptance criteria are settled and falsifiable. |
| `model` | `model.py` is being built to satisfy the spec. | It builds and its assertions pass. |
| `review` | Renders are read against the acceptance criteria. | The criteria a render *can* settle are settled. |
| `print` | STL exported; printing or printed, not yet judged. | The physical object has been handled. |
| `done` | Validated in the hand. | A new requirement. |

The two loops that matter are the ones that go *backwards*. Review sends you back to `model`; a bad print sends you back to `model` or, when the spec was wrong rather than the geometry, all the way to `spec`.

**Know which loop you are in.** Going back to `model` searches *within* the current target. Going back to `spec` *moves* the target — a new generation, with the history reset, because verdicts recorded against the old criteria were answers to a different question. If several iterations pass without a `good`, that is the signal to take the outer loop: `cad next` says so after five.

### Never make the human work out what comes next

Every command that changes state ends by printing the single next action, derived from what is actually on disk — criteria present, model newer than the render, latest verdict, print criteria still open. `cad next` shows it for one part; `cad status` shows the board.

The rules live in `cadkit/advise.py` and are ordered by what blocks what. If you add a stage or an artifact, add its rule there — an unhandled state that falls through to a vague suggestion is worse than no suggestion at all.

### Who does what

**The user works in conversation. You work the tools.** They describe a part, look at renders, and say what is wrong; everything between those is yours. Do not end a turn by telling them to run something you could have run — that is handing back the tax the harness exists to pay.

| The user | You |
|---|---|
| Says what they want, in prose | `cad new`, drafts `spec.md` with them |
| Looks at the render sheet, in their own viewer | `cad build` — it writes the sheet and prints its path, and does **not** open it |
| Says what is wrong, in prose | Translates that into a parameter or geometry change, rebuilds |
| Gives a verdict, in prose | `cad accept` with their words as the note |
| Slices and prints (Bambu Studio, by hand) | `cad build --stl`, hands over the path |
| Reports what came out | Records it in `prints.md`, ticks off the criteria it settled |

Three things genuinely need them and cannot be delegated: **judgment** (only they can say whether a shape is the shape they meant), **the printer** (Bambu Studio is a GUI and slicing stays manual — see Scope), and **editing `spec.md` directly** if they would rather write it than dictate it.

Everything else — running builds, reading the sheet, checking criteria, recording verdicts, chasing `cad next` — is yours. Relay what matters; do not paste raw command output at them and make them parse it.

### The commands

You run these. They are listed so you know what exists, not as instructions to pass along.

```bash
./cad status                  # every part, grouped by project: stage, history
./cad project [<name>]        # the sets, or one set and who belongs to it
./cad new <name> [--project <p>]   # scaffold at the spec stage
./cad build <name>            # build → assert → check → render
./cad build <name> --stl      # …and export the mesh, in the print pose
./cad watch <name>            # rebuild on save
./cad accept <name> good|bad|mixed|printed "why"
./cad history <name>          # what was tried, and what was ruled out
./cad sweep <name> wall=2,2.4,3    # variants rendered side by side
./cad stage <name> review
./cad promote <name>          # publish a private part (dry-run without --yes)
```

`build` does the whole inner loop in one shot, because a review that takes three commands is a review that gets skipped.

## Refinement must not oscillate

This is the failure the repo is built to prevent. Wall thickness goes 2.0 → 3.0 because a print felt flimsy, then 3.0 → 2.4 because it looked chunky, then back toward 3.0 for the same reason as the first time. Each step is locally reasonable. The information that would stop it is never written down, because at the time it feels too obvious to write.

So it is not written down by hand:

- Every `cad build` compares the parameters against `history.jsonl` and appends an entry when they differ, with the **diff computed rather than remembered**.
- Returning to a parameter set that already carries a verdict prints a loud warning naming the iteration and its outcome.
- `history.md` is regenerated from the record and carries a ledger of values that were in play on rejected iterations.

**Before proposing any parameter change, read the part's `history.md`.** An iteration marked `bad` is a direction already ruled out; going back needs a reason that did not exist the first time.

After a build that you have judged — from renders or from a print — record it: `cad accept <part> good|bad|mixed "why"`. The entry already exists; you are filling in the outcome. An iteration left `untested` forever is how the ledger rots.

## Where parts live

Two collections, treated identically by the harness:

- **`examples/`** — public, committed to this repo, written to be read by strangers.
- **`parts/`** — private, git-ignored here, version-controlled separately. This is where real work happens. `cad new` scaffolds here by default.

`cad status` labels each, marking a private part with `*` when a snapshot of it is published.

Publishing is `cad promote <name>`, which is a **publishing decision, not a file move**. It lists what would become public and does nothing without `--yes`, because `notes.md` and `prints.md` carry measurements, dead ends and whatever was written right after a failed print. It refuses outright to publish a part importing a still-private assembly, or belonging to a still-private project. Read `PRIVACY.md` before promoting anything.

Three things about it that are easy to get wrong:

- **It copies. The private original stays and remains authoritative.** The published copy is a *snapshot*; refinement continues in `parts/`, and re-running `cad promote` refreshes the snapshot. `find()` resolves a name to the private copy wherever both exist, so `cad build <name>` always edits the working copy rather than the thing that gets overwritten.
- **`history.jsonl` and `history.md` are never published.** One dated row per build reconstructs which evenings were spent how, and that is nobody's business. The ledger stays in the working copy, where it does its real job of stopping the search circling.
- **Dates are stripped from everything that does go out** — print-log headings, `ACCEPTED.md`'s date field, the accepted mesh's timestamped filename, and dates in prose. Withholding the ledger alone achieves nothing while `prints.md` is dated and the mesh is named to the minute. Any date form the scrubber does not recognise becomes a loud `[date removed]` rather than slipping through quietly; if you see one in `examples/`, teach `_scrub` the form rather than editing the published file.
- **Image metadata is stripped too, and it was the bigger leak.** A photo's EXIF carries the second it was taken and the camera's serial number; images were copied through untouched for a long time. `cadkit/imgmeta.py` rewrites every published JPEG, PNG and GIF without it, losslessly (the compressed data is copied byte for byte), keeping only orientation and colour profiles. An image format it cannot strip is refused before anything is copied — convert it, do not work around the refusal.

## Never hard-wrap a paragraph in Markdown

**Every paragraph in every `.md` file is ONE line, however long.** Do not wrap prose at 80 columns, or at any width. This applies to files you write by hand, files a command generates, and edits to files that are already correct.

Typora — and any renderer with breaks-on-newline — treats a single newline inside a paragraph as a hard line break, so source-wrapped text renders as ragged, broken lines instead of flowing prose. The whole repo was reflowed once to fix this; do not undo it one edit at a time.

What still gets its own line: headings, list items, table rows, blockquote paragraphs, and anything inside a fenced code block. A list item that runs long stays on one line too. ASCII diagrams live in fences, where wrapping is content rather than formatting.

Editors that soft-wrap make long lines perfectly readable. The 80-column habit is for code.

## The files a part carries

```
<collection>/<name>/
    spec.md        intent + acceptance criteria. THE DURABLE ARTIFACT.
    model.py       geometry. Disposable — expect to rewrite it.
    notes.md       why the numbers are what they are.
    history.md     what was tried (generated; edit history.jsonl never by hand).
    prints.md      what happened when it met the physical world.
    inspiration/   the source imagery this part was made from.
    build/         generated, git-ignored.
```

**`inspiration/` is not optional decoration for a traced part.** Put the reference image there *before* tracing, and have the trace script read `Path(__file__).parent / "inspiration" / "<name>.png"`. A source that lives outside the part stops existing: `raven_lantern`'s artwork pointed into a per-session chat image cache and is gone, so that outline can now only be edited as coordinates, never re-traced against what it was meant to look like. A part traced from a picture is not described without the picture — the outline data is a list of numbers, and whether it still *reads* as the subject is a question only the original can settle.

The division of labour matters and is easy to blur:

- **`spec.md`** is what the part is *for*. When a design goes wrong it is almost always because the spec was thin, not because the geometry was hard.
- **`notes.md`** is *why the numbers are what they are* — the reasoning that is invisible in the source. Never restate a dimension value here; duplicated numbers drift. Name the symbol and explain the why. The material for this file is anything a render and a check cannot say: a decision that had two valid-looking options, a value that turned out to be spoken for by something outside the model, a belief that was wrong and what replaced it.
- **`history.md`** is *what was tried*. Generated. Do not hand-edit it.
- **`prints.md`** is *what the physical world said*. Record successes too — a design that works and nobody wrote down why is one refinement from losing the property by accident.

## Writing a part

`model.py` must define `PARAMS` (a frozen `Params` dataclass instance) and `build(p) -> Part`. It may define `check(part, p)`, `pieces(p)`, `SECTION` and `PRINT_ROTATION`.

**Nothing runs on import.** No `show()`, no file writes, no prints. Everything that acts on a part calls `build()`. The old repo called `show()` at module scope, which meant nothing could import a part without pushing it at a viewer, which is why every STL export sat commented out.

```python
@dataclass(frozen=True)
class P(Params):
    wall: float = 2.4

PARAMS = P()
SECTION = "x"              # which way to cut the cutaway render
PRINT_ROTATION = (0, 0, 0) # modeled pose → print pose

def build(p: P) -> Part: ...
def check(part, p) -> None: ...      # assertions
def pieces(p) -> dict: ...           # multi-piece prints only
```

- **Parameters are a frozen dataclass**, so the numbers are named in one place, a build cannot mutate them halfway through, and every mesh is written next to the exact values that produced it. A dimension you cannot trace to its inputs is one you will re-derive by measuring a print.

  **Meshes are named by export time (`<part>-YYYYmmdd-HHMM.stl`), not by parameter digest**, and `build/exports.jsonl` is the append-only ledger mapping each file back to the parameters it came from. The digest names the *parameters*, which is not the same as naming the *mesh*: a part that reads a shared `assemblies/` module changes geometry when the assembly changes while its digest does not, so two different objects claimed one filename and the second overwrote the first. A timestamp cannot collide whatever caused the change. The same gap still applies to the oscillation guard — it compares `PARAMS` only, so a change made in an assembly is invisible to it.
- **Derived values go in one `geometry(p)` / `layout(p)` helper** that both `build` and `check` read, so an assertion can never be checking different arithmetic than the model used.
- **`PRINT_ROTATION` is not optional decoration.** The overhang check is meaningless in the wrong pose — a pocket floor is a ceiling when flipped — and an STL exported in the modeled pose lands on the plate needing a manual rotation nobody records. If the orientation is genuinely undecided, leave it unset: every build will then say so, which is the correct amount of nagging.

### Artwork becomes geometry through a pipeline, not a guess

A motif traced from a supplied image — a raven, a witch, a jack-o'-lantern face — goes through a specific process, and every step of it was paid for. **Read `ARTWORK.md` before tracing anything.**

The rule the rest follows from: **adapt the artwork to the part, never the part to the artwork.** Part size is set by the object it holds, so any conflict is resolved by changing the artwork. Supplied reference images are AI-generated and carry no intent to preserve — simplify freely, then show the result, because whether it still *reads* as the subject is a human judgement.

Judge printability by **simulating the nozzle** (a morphological opening at the nozzle radius) and looking at the result, not by reasoning about feature sizes.

### Overhangs and islands are different failures

`cad build` runs an **islands** check on every part, and it is worth knowing what it means because the distinction is easy to blur and expensive to miss:

- an **overhang** is material attached, on its own layer, to material that is supported. It leans out and droops. It usually survives.
- an **island** is a blob of material on a layer with *no path along that layer* to anything supported. It is extruded into open air and falls.

Measured as a fraction of material the two are indistinguishable — a part that printed clean scored 0.51% unsupported and one that had to be cancelled scored 0.47%. Counting islands separated them completely: zero against fifteen.

**An island is not a prohibition.** It is printable with supports, and the check is a WARN because the real question is a decision, surfaced while the shape can still be changed cheaply: enable supports and accept the cleanup and the marks removal leaves, or reshape so the feature is anchored. Which is right depends on the part — a bracket does not care about support scars, a lantern whose inner wall is backlit through its own openings very much does.

### Assertions carry the knowledge

Prefer a check that fails loudly over a comment that asks nicely. The best ones assert a *derived* fact against the theory that produced it — a shape built with wrong maths still renders as a plausible shape, and no generic check catches it. A good example of the pattern: an operation that selects features by position — say, filleting internal corners — should assert how many it selected. If the shape ever changes, that fires immediately instead of the operation silently landing on the wrong edges. `notes.md` explains the assertion, the assertion enforces it.

Assert the things that fail *silently*: a detached boss that prints as a loose cylinder inside a closed box, an unlit heart, two vent slots that merged into one unsupported span.

### Acceptance criteria must ask what the part is FOR

Write the criteria that establish the part does its job **before** the ones that check it is built correctly, because the second kind is much easier to write and will happily fill the whole list.

A criteria list made only of geometric invariants — wall thicknesses, fillet counts, one-solid, fits-the-bed — will certify a useless part with a clean bill of health. Every assertion passes, every check passes, the render matches the profile that was drawn, and nothing anywhere asked whether that profile was any use. Reviewing then confirms the shape is the shape you meant, which is not the same question as whether you meant the right shape.

Some functional criteria can be asserted, and should be. Derive the quantity that actually matters — the usable opening, the clearance that remains, the volume that is reachable — and assert *that*, not the raw parameters. Each input can look sensible while the space between them is nothing.

The ones that cannot be asserted go in the spec flagged for the reviewer to read off the render.

## Reviewing

**Every generated image carries the time it was made**, in a banner across the top. `cad build`'s render sheet does this automatically; anything else you generate — comparison sheets, true-scale flats, diagnostic overlays — must do the same.

An undated render is indistinguishable from a stale one, and that is not a theoretical worry: a sheet from before a change has already been read here as though it showed the change. Two lines of code against a whole wasted conversation.

### Crop before concluding a feature failed

**Resolution destroys small features, and it does so silently.** A whole-part view — rendered *or* photographed — averages fine detail away, and what comes back looks exactly like a feature that is not there. Both halves of that have now cost real time here:

- a render sheet showed smooth walls while the mortar was being cut correctly, because the renderer's depth-jump threshold scales with the view;
- a frame from a downscaled animation showed `castle`'s eyes as plain arches, so "the pupils are not reading" was written into `prints.md` along with a theory about the paper diffuser flattening them. A detail crop of a full-resolution still showed them immediately, exactly as designed.

So: **before reporting that a feature failed, crop to it at full resolution.** When the source is a photograph or a video the user has supplied, extract a frame and crop it — do not judge a millimetre-scale feature from a view of the whole object. Saying a hard-won detail did not survive, when it did, is worse than saying nothing.


`cad build` writes `build/review/sheet.png` — four orthographic views plus a cutaway — and prints the spec's acceptance criteria underneath. **Read the renders against the criteria.** Review without them degrades into "looks fine to me", which is how a part gets built with the right shape and the wrong purpose.

The renderer is a small software rasterizer (numpy + Pillow, no VTK, no GL). It produces shaded solids with silhouette and crease lines, not photographs. That is the right fidelity for "is this the shape I meant?".

`SECTION` matters more than it looks: internal geometry is exactly what a shaded exterior cannot show, and exactly where the expensive mistakes live.

## Shared numbers

- **`printer.py`** — machine and material facts only. Bed, nozzle, layer height, overhang limit, density, default clearances. Nothing part-specific, and **nothing hardcoded**: the values come from the user's `printer.toml`, written by `cad setup` and git-ignored. Never write a bed size or a nozzle diameter into a part; read it from `printer`. A part that assumes one machine is a part nobody else can print.
- **`assemblies/<name>.py`** — the contract between parts that must **fit** each other — where two parts are really one object cut into printable pieces, and the interface is the numbers along the cuts. It is **passed in**, not star-imported, so a part that does not participate cannot pick a name out of it by accident.
- **`projects/<name>/`** — parts that **belong** together. Independent objects sharing an envelope, a material, a set of standards and a slicer profile; nothing mates with anything. Holds `project.md` (what is settled for the whole set, and why) and optionally `shared.py` (the numbers every member reads). Membership is **declared** by the part, in `spec.md` front matter (`project: <name>`) — a part that imports a module has not thereby joined a set. `cad project` lists them; `cad status` groups by them.

  The distinction from an assembly is not pedantry and was learned by getting it wrong: a set of lanterns went into `assemblies/` because that was the only grouping that existed, but lanterns do not fit each other. The cost was that set-level decisions scattered through whichever part first discovered them.

  Both directories are namespace packages (no `__init__.py`), so they merge across collections and a private one needs no special handling to stay private. **`parts/projects/` is private; anything at the repo root is not** — a project carries measurements and workshop standards, so `cad promote` refuses to publish a part whose project is still private.
- **Everything else stays local to its part**, even if it looks general. Promote a value only when a second part genuinely needs it.

## Toolchain

- **build123d** is the modelling library. Not CadQuery, not OpenSCAD. Don't introduce another.

  Four of its behaviours have each cost a real bug here, and all four are silent — the part builds, is watertight, passes every check, and renders as something plausible:

  - **A primitive constructed inside an open builder joins it at construction time**, so a helper returning `Pos(...) * Box(...)` contributes twice. Build primitives before entering the builder, and pass `mode=Mode.PRIVATE`.
  - **`add()` places a shape relative to the builder's CURRENT WORKPLANE**, not at its own coordinates. Adding an absolutely-positioned solid while a `Plane.XZ` sketch is in context re-maps it — `owl` grew a 47 mm slab out of its feet this way. **Fuse absolutely-positioned solids with `+` outside the builder; use `add()` only for things you want placed *on* the workplane.**
  - **`.locate()` sets an ABSOLUTE location and discards any transform the shape already carried.** It will silently throw away a `.rotate()`. Use `.move()` for anything relative.
  - **`Plane.XZ`'s normal is −Y**, so a bare `extrude()` on it builds backwards. Pass `dir=` explicitly whenever the direction matters.

  All four live in the depth direction, which is exactly where a facade part hides its mistakes.
- **bd_warehouse** supplies stock parts — reach for it before modelling a standard component by hand (`thread`, `fastener`, `gear`, `bearing`, `sprocket`, `pipe`, `flange`, `open_builds`). Import the submodule; the top-level package is nearly empty.
- Run everything through `./cad`, which uses `.venv/bin/python`. A bare `python` lacks OCP.
- **Never `pip install` without asking first.** The OCP kernel is a large, version-sensitive binary wheel and the environment is easy to break. Pinned versions are in `requirements.txt`; update it when a dependency changes.
- `ocp_vscode` is installed but is **not** part of the loop. It pushes over a websocket to a browser tab and stores nothing, so a part run with no tab attached succeeds silently and displays nothing. Use it for interactive rotation if you like; never depend on it for review.

  It is pinned in `requirements-viewer.txt`, not `requirements.txt`, and that file explains the trap: its dependency chain caps Pillow *below* the version that patches Pillow's advisories, so installing the viewer silently downgrades Pillow. **If you ever run `pip install` in a way that touches ocp_vscode, check `pip list | grep -i pillow` afterwards** and re-force `pillow==12.3.0` with `--no-deps` if it moved. Putting both pins in one requirements file does not work — pip fails the whole install with ResolutionImpossible.

## Slicing and printing

**`SLICING.md` at the repo root** carries the settings that are not in `printer.toml` — the ones a person types into the slicer, which the harness cannot see and cannot check. It is organised by **scope**, because that is what decides where a finding belongs and whether it will be found again:

| scope | example |
|---|---|
| machine | flow dynamics auto-calibrates; not a knob |
| material | 210 °C not 220 for PLA here — try temperature FIRST when stringing |
| geometry | `avoid crossing wall` at 100% for any wall with openings pierced through it |

A finding filed under a project when it is really about the machine gets re-derived on every project. One applied everywhere when it is really about a geometry is cargo cult. Put it at the right level.

`slicer-profiles/` holds saved slicer projects as artifacts rather than prose. They are hand-made and there is one copy of each.



Manual, in the slicer. The rest of this section is specific to Bambu hardware — if `printer.toml` names another machine, its slicer has its own answer and the Developer Mode reasoning below does not apply.

For Bambu: manual, in the Bambu Studio GUI. Don't build CLI slicing or automated print submission for the A1 mini — that requires LAN-only + Developer Mode, which has been ruled out, and Bambu Studio's CLI is a slicer front-end with no networking flags at all.

If you reach for the CLI anyway, know that `--load-settings` does **not** resolve a system profile's `inherits` chain. It silently falls back to generic defaults — filament density 0, accelerations 20× low — then exits 0 and reports `"Success."` Flatten the chain before passing profiles in.
