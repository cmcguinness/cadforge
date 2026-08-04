# cadforge

Parametric CAD in Python ([build123d](https://github.com/gumyr/build123d)),
organised around a design process rather than a folder of scripts.

The premise: the hard part of designing a printed object is not writing the
geometry. It is knowing whether the geometry is right, remembering why a number
is what it is, and not going in circles when you refine it. So the repo is built
around those three problems.

```
spec  ──▶  model  ──▶  review  ──▶  print  ──▶  done
 ▲                        │           │
 └────────────────────────┴───────────┘
```

## What it gives you

**Review is an artifact, not a live viewer.** `cad build` writes a contact sheet
— four orthographic views plus a cutaway — as a PNG on disk. It renders headless
with numpy and Pillow: no VTK, no OpenGL, no browser tab that has to be open at
the right moment. About 0.1 s per view.

<!-- examples/desk_edge_hook/build/review/sheet.png is what this produces -->

**Refinement can't quietly oscillate.** Every build diffs the parameters against
the part's recorded history and appends an entry when they differ, with the diff
*computed rather than remembered*. Come back to a parameter set that already
carries a verdict and it says so, loudly:

```
!! these exact parameters were used before:
     iteration #3 (2026-07-14) → bad — still too flimsy at the rib
   check history.md before spending more effort here.
```

**Knowledge lives in assertions, not comments.** A shape built from wrong maths
still renders as a plausible shape. Parts assert derived facts against the theory
that produced them, so editing the theory fails immediately instead of producing
something subtly wrong that nobody notices until it is printed.

**Print pose is distinguished from modeled pose.** The overhang check is
meaningless in the wrong orientation, and an STL exported in the modeled pose
lands on the plate needing a manual rotation that nobody records. Parts declare
`PRINT_ROTATION`; leaving it undeclared makes every build say so.

## Try it

```bash
git clone <this repo> && cd cadforge
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

./cad status
./cad build desk_edge_hook          # writes examples/desk_edge_hook/build/review/sheet.png
./cad sweep desk_edge_hook throat=18,28,38
./cad new my_part
```

`requirements.txt` pins a large, version-sensitive OCP binary wheel. Expect the
install to take a while.

## A part

```
examples/desk_edge_hook/
    spec.md       what it is for, and acceptance criteria a render can settle
    model.py      build(p) -> Part.  Nothing runs on import.
    notes.md      why the numbers are what they are
    history.md    what was tried, and what was ruled out   (generated)
    prints.md     what happened when it met the physical world
```

`model.py` defines a frozen `Params` dataclass and `build(p)`. Optionally
`check(part, p)` for assertions, `pieces(p)` for multi-piece prints, `SECTION`
for the cutaway plane, and `PRINT_ROTATION`.

```python
@dataclass(frozen=True)
class P(Params):
    desk_t: float = 25.0    # MEASURED
    grip:   float = 0.8     # interference — this is what holds it on

PARAMS = P()
PRINT_ROTATION = (-90, 0, 0)

def build(p: P) -> Part: ...

def check(part, p) -> None:
    assert p.grip <= 0.08 * p.desk_t, "PLA will take a set rather than spring back"
```

Read `examples/desk_edge_hook/` end to end — it is written to be the tutorial.
Its `notes.md` is the point: the clip prints fine in two orientations and snaps
in one of them, and nothing in the geometry can tell you which.

## Commands

| | |
|---|---|
| `cad status` | every part, which collection, its stage, its history |
| `cad new <name>` | scaffold at the spec stage |
| `cad build <name> [--stl]` | build → assert → check → render → export |
| `cad watch <name>` | rebuild on save |
| `cad accept <name> good\|bad\|mixed "why"` | record a verdict |
| `cad history <name>` | what was tried, what was ruled out |
| `cad sweep <name> wall=2,2.4,3` | variants rendered side by side |
| `cad stage <name> review` | move through the process |
| `cad promote <name>` | publish a private part into `examples/` |

## Two collections

`examples/` is public and lives in this repo. `parts/` is where real work
happens; it is git-ignored here and version-controlled separately, so personal
designs stay private without leaving the working directory. See
[PRIVACY.md](PRIVACY.md).

## Scope

Built for a Bambu Lab A1 mini and PLA; `printer.py` holds every machine and
material assumption in one place. Slicing is manual in Bambu Studio — there is
deliberately no CLI slicing or print submission, and `CLAUDE.md` explains why
that is not an oversight.

`CLAUDE.md` documents the conventions in full, and `.claude/skills/` carries
three workflow skills (spec, review, print) if you drive this with an agent.
