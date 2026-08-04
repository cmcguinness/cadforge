# cadforge — project conventions

Parametric CAD in Python, organised around a design process rather than a pile
of scripts. Read this before writing or editing a part.

## The process

Every part moves through five declared stages. The stage lives in the part's
`spec.md` front matter and is changed deliberately with `cad stage`, never
inferred from which files happen to exist.

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

The two loops that matter are the ones that go *backwards*. Review sends you
back to `model`; a bad print sends you back to `model` or, when the spec was
wrong rather than the geometry, all the way to `spec`.

### The commands

```bash
./cad status                  # every part, its collection, stage, history
./cad new <name>              # scaffold at the spec stage
./cad build <name>            # build → assert → check → render
./cad build <name> --stl      # …and export the mesh, in the print pose
./cad watch <name>            # rebuild on save
./cad accept <name> good|bad|mixed|printed "why"
./cad history <name>          # what was tried, and what was ruled out
./cad sweep <name> wall=2,2.4,3    # variants rendered side by side
./cad stage <name> review
./cad promote <name>          # publish a private part (dry-run without --yes)
```

`build` does the whole inner loop in one shot, because a review that takes three
commands is a review that gets skipped.

## Refinement must not oscillate

This is the failure the repo is built to prevent. Wall thickness goes 2.0 → 3.0
because a print felt flimsy, then 3.0 → 2.4 because it looked chunky, then back
toward 3.0 for the same reason as the first time. Each step is locally
reasonable. The information that would stop it is never written down, because at
the time it feels too obvious to write.

So it is not written down by hand:

- Every `cad build` compares the parameters against `history.jsonl` and appends
  an entry when they differ, with the **diff computed rather than remembered**.
- Returning to a parameter set that already carries a verdict prints a loud
  warning naming the iteration and its outcome.
- `history.md` is regenerated from the record and carries a ledger of values
  that were in play on rejected iterations.

**Before proposing any parameter change, read the part's `history.md`.** An
iteration marked `bad` is a direction already ruled out; going back needs a
reason that did not exist the first time.

After a build that you have judged — from renders or from a print — record it:
`cad accept <part> good|bad|mixed "why"`. The entry already exists; you are
filling in the outcome. An iteration left `untested` forever is how the ledger
rots.

## Where parts live

Two collections, treated identically by the harness:

- **`examples/`** — public, committed to this repo, written to be read by
  strangers.
- **`parts/`** — private, git-ignored here, version-controlled separately. This
  is where real work happens. `cad new` scaffolds here by default.

`cad status` labels each. Publishing is `cad promote <name>`, which is a
**publishing decision, not a file move**: it lists what would become public and
does nothing without `--yes`, because `notes.md` and `history.md` carry
measurements, dead ends and whatever was written right after a failed print.
It refuses outright to publish a part importing a still-private assembly. Read
`PRIVACY.md` before promoting anything.

## The files a part carries

```
<collection>/<name>/
    spec.md      intent + acceptance criteria. THE DURABLE ARTIFACT.
    model.py     geometry. Disposable — expect to rewrite it.
    notes.md     why the numbers are what they are.
    history.md   what was tried (generated; edit history.jsonl never by hand).
    prints.md    what happened when it met the physical world.
    build/       generated, git-ignored.
```

The division of labour matters and is easy to blur:

- **`spec.md`** is what the part is *for*. When a design goes wrong it is almost
  always because the spec was thin, not because the geometry was hard.
- **`notes.md`** is *why the numbers are what they are* — the reasoning that is
  invisible in the source. Never restate a dimension value here; duplicated
  numbers drift. Name the symbol and explain the why.
  `examples/desk_edge_hook/notes.md` is the worked example: the clip prints
  cleanly in two orientations and delaminates in one of them, and nothing in the
  geometry can tell you which — so the decision is written down and encoded in
  `PRINT_ROTATION`.
- **`history.md`** is *what was tried*. Generated. Do not hand-edit it.
- **`prints.md`** is *what the physical world said*. Record successes too — a
  design that works and nobody wrote down why is one refinement from losing the
  property by accident.

## Writing a part

`model.py` must define `PARAMS` (a frozen `Params` dataclass instance) and
`build(p) -> Part`. It may define `check(part, p)`, `pieces(p)`, `SECTION` and
`PRINT_ROTATION`.

**Nothing runs on import.** No `show()`, no file writes, no prints. Everything
that acts on a part calls `build()`. The old repo called `show()` at module
scope, which meant nothing could import a part without pushing it at a viewer,
which is why every STL export sat commented out.

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

- **Parameters are a frozen dataclass**, so the numbers are named in one place,
  a build cannot mutate them halfway through, and every mesh is written next to
  the exact values that produced it (`build/params.json`, and the digest in the
  STL filename). A dimension you cannot trace to its inputs is one you will
  re-derive by measuring a print.
- **Derived values go in one `geometry(p)` / `layout(p)` helper** that both
  `build` and `check` read, so an assertion can never be checking different
  arithmetic than the model used.
- **`PRINT_ROTATION` is not optional decoration.** The overhang check is
  meaningless in the wrong pose — a pocket floor is a ceiling when flipped — and
  an STL exported in the modeled pose lands on the plate needing a manual
  rotation nobody records. If the orientation is genuinely undecided, leave it
  unset: every build will then say so, which is the correct amount of nagging.

### Assertions carry the knowledge

Prefer a check that fails loudly over a comment that asks nicely. The best ones
assert a *derived* fact against the theory that produced it — a shape built with
wrong maths still renders as a plausible shape, and no generic check catches it.
`desk_edge_hook` asserting that its fillet selection found exactly the three
internal corners it expects is the pattern: if the profile ever changes shape,
that fires instead of the fillet silently landing on the wrong edges. `notes.md`
explains the assertion, the assertion enforces it.

Assert the things that fail *silently*: a detached boss that prints as a loose
cylinder inside a closed box, an unlit heart, two vent slots that merged into
one unsupported span.

## Reviewing

`cad build` writes `build/review/sheet.png` — four orthographic views plus a
cutaway — and prints the spec's acceptance criteria underneath. **Read the
renders against the criteria.** Review without them degrades into "looks fine to
me", which is how a part gets built with the right shape and the wrong purpose.

The renderer is a small software rasterizer (numpy + Pillow, no VTK, no GL). It
produces shaded solids with silhouette and crease lines, not photographs. That
is the right fidelity for "is this the shape I meant?".

`SECTION` matters more than it looks: internal geometry is exactly what a shaded
exterior cannot show, and exactly where the expensive mistakes live.

## Shared numbers

- **`printer.py`** — machine and material facts only. Bed, nozzle, layer height,
  overhang limit, PLA density. Nothing part-specific.
- **`assemblies/<name>.py`** — the contract between parts that must fit each
  other — where two parts are really one object cut into printable pieces, and
  the interface is the numbers along the cuts. It is **passed in**,
  not star-imported, so a part that does not participate cannot pick a name out
  of it by accident. `assemblies/` is a namespace package (no `__init__.py`), so
  it merges across both collections and a private interface needs no special
  handling to stay private.
- **Everything else stays local to its part**, even if it looks general. Promote
  a value only when a second part genuinely needs it.

## Toolchain

- **build123d** is the modelling library. Not CadQuery, not OpenSCAD. Don't
  introduce another.
- **bd_warehouse** supplies stock parts — reach for it before modelling a
  standard component by hand (`thread`, `fastener`, `gear`, `bearing`,
  `sprocket`, `pipe`, `flange`, `open_builds`). Import the submodule; the
  top-level package is nearly empty.
- Run everything through `./cad`, which uses `.venv/bin/python`. A bare `python`
  lacks OCP.
- **Never `pip install` without asking first.** The OCP kernel is a large,
  version-sensitive binary wheel and the environment is easy to break. Pinned
  versions are in `requirements.txt`; update it when a dependency changes.
- `ocp_vscode` is installed but is **not** part of the loop. It pushes over a
  websocket to a browser tab and stores nothing, so a part run with no tab
  attached succeeds silently and displays nothing. Use it for interactive
  rotation if you like; never depend on it for review.

## Slicing and printing

Manual, in the Bambu Studio GUI. Don't build CLI slicing or automated print
submission for the A1 mini — that requires LAN-only + Developer Mode, which has
been ruled out, and Bambu Studio's CLI is a slicer front-end with no networking
flags at all.

If you reach for the CLI anyway, know that `--load-settings` does **not** resolve
a system profile's `inherits` chain. It silently falls back to generic defaults
— filament density 0, accelerations 20× low — then exits 0 and reports
`"Success."` Flatten the chain before passing profiles in.
