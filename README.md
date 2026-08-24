# CadForge

There you are with your Claude code Max plan, and you've got a billion dollar AI system at your beck and call.  What do you do with it?

Create plastic tchotchkes, of course!

But wait, you say that's not something an LLM can do? Au contraire, mon ami!

Because (stay with me here) Claude code can write python programs.  Python programs can create 3D models and export .stl files.  .stl files can be 3D printed.  By the transitive property of hacking stuff together, this means that Claude Code can 3D print stuff.  QED.

Of course it's not as simple as hey presto and it's done.  It takes time and effort and trial and error.  But it works amazingly well.

This repository has two purposes.  The first, the trivial one, is to grab the examples I've generated myself and 3D print them: the .stl files are here.  The second is to use all the assets I've built up to create your own AI-driven plastic tchotchkes.  I hope you give it a whirl.

That second purpose is most of what's here, and it takes some explaining — because the interesting problem turned out not to be the CAD.  It was everything around it.  So the rest of this README is the careful version: what the repo is, why it's shaped the way it is, and how to drive it.

## What it is

**A workshop for designing 3D-printed parts with [Claude Code](https://claude.com/claude-code).** You describe what you want, Claude writes the [build123d](https://github.com/gumyr/build123d) model, you look at the renders and say what's wrong, and it converges on an STL you print.

This is not a CAD library that happens to tolerate an AI. Every component here exists to compensate for something a language model cannot do — and if you are not driving it with one, you want maybe a quarter of what is in this repo.

## The problem it solves

Ask an LLM to design a physical object and four things go wrong, reliably:

**It can't see.** It will write geometry, assert the geometry is correct, and have no way to check. → `cad build` renders a contact sheet — four orthographic views plus a cutaway — to a **PNG on disk**, headless via numpy and Pillow. No VTK, no OpenGL, no viewer window that has to be open at the right moment. ~0.1 s per view. A live viewer can only be read by a person watching it; a file can be read by the model that produced it.

**It doesn't remember.** Every session starts from nothing. It will re-derive a clearance you already paid a failed print to learn. → `notes.md` holds the reasoning that isn't visible in the source, `history.md` holds what was already tried. Both are plain markdown, read at the start of the work.

**It agrees with itself.** Shown a render, it will confirm the shape matches the shape it drew and call that a review. → `spec.md` carries acceptance criteria that `cad build` prints beneath the renders, so the review answers questions someone else wrote. Criteria are split by axis — *does it do its job* vs *is it built correctly* — because an unstated axis stays unconstrained however precise the others get. That is not hypothetical: this repo's first example had seven criteria, all about construction, and produced a part that was built perfectly and could hold nothing.

**It is confidently, plausibly wrong.** A shape built from bad maths is still a shape, and no render will tell you. → Parts assert derived facts against the theory that produced them, so editing the theory fails loudly instead of quietly producing something subtly wrong.

And one that's about the loop rather than the model: **refinement circles.** Wall thickness goes 2.0 → 3.0 → 2.4 → back toward 3.0, each step locally reasonable. → Every build diffs the parameters against the history — the diff *computed*, not remembered — and returning to a judged parameter set says so:

```
!! these exact parameters were used before:
     iteration #3 (2026-07-14) → bad — still too flimsy at the rib
   check history.md before spending more effort here.
```

## Install

Once:

```bash
git clone <this repo> && cd cadforge
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
./cad setup                       # choose your printer and material
```

`requirements.txt` pins a large, version-sensitive OCP binary wheel — expect it to take a while.

That is everything the design loop needs. The optional `ocp_vscode` viewer, for when you want to grab a part and spin it rather than read a contact sheet, is a separate two-line install and `requirements-viewer.txt` explains why:

```bash
.venv/bin/pip install -r requirements-viewer.txt
.venv/bin/pip install --no-deps --upgrade 'pillow==12.3.0'
```

The second line matters. The viewer's dependency chain caps Pillow below the version that patches its current advisories, so installing it silently downgrades Pillow; that line puts the patched one back.

`cad setup` writes `printer.toml` — git-ignored, because it describes your bench rather than the project. Profiles ship for the common Bambu, Prusa and Creality machines plus a generic FDM fallback; `./cad setup --list` shows them, and any value can be overridden in the file. Materials cover PLA, PETG, ABS, ASA and TPU, which set density for the mass estimate, default clearances, and a tighter overhang limit where the material droops earlier.

Until it runs, every bed-fit check, mass estimate and minimum-wall assertion is answering for a machine nobody owns — so the harness refuses to talk about anything else:

```
 !! puck_base — Configure your printer and material.
      Running on generic defaults: every bed-fit check, mass estimate and
      minimum-wall assertion is currently answering for a machine nobody owns.
```

The bundled figures are **nominal** — manufacturer numbers, not measurements. This repo is fussy about that distinction everywhere else and it applies to itself. Measure your own bed before trusting a part that lands near its edge.

## The loop

Start a session with `claude` in the repo, and say what you want:

> *"I need a holder for a battery tea light, about 45mm across, with hearts cut through the wall so the light shows through."*

Claude reads `CLAUDE.md` and the skills in `.claude/skills/`, drafts a `spec.md` with you, and the cycle starts:

```
   .───────────────────────────.
  (            Start            )
   `───────────────────────────'
                 │
                 │
                 │
                 ▼
 ┌──────────────────────────────┐
 │  You describe what you want  │
 └──────────────────────────────┘
                 │
                 │
                 ▼
                .─.
               (   )◀────────────────────────────────┐
                `─'                                  │
                 │                                   │
                 │                                   │
                 ▼                                   │
 ┌──────────────────────────────┐                    │
 │    Claude Creates/Updates    │                    │
 │     spec and/or model.py     │                    │
 └──────────────────────────────┘                    │
                 │                                   │
                 │                                   │
                 ▼                                   │
 ┌──────────────────────────────┐      ┌──────────────────────────┐
 │  model.py builds, asserts,   │      │      User Feedback       │
 │     checks, and renders      │      │                          │
 └──────────────────────────────┘      └──────────────────────────┘
                │                                    ▲
                │                                    │
                ▼                                    │
┌──────────────────────────────┐                     │
│     User reviews render      │                     │
└──────────────────────────────┘                     │
                │                                    │
                │                                    │
                │                                    │
                ▼                                    │
                Λ                                    │
               ╱ ╲                                   │
              ╱   ╲                                  │
             ╱     ╲                                 │
            ╱  Good ╲   No                           │
           ▕ Enough? ▏───────────────────────────────┤
            ╲       ╱                                │
             ╲     ╱                                 │
              ╲   ╱                                  │
               ╲ ╱                                   │
                V                                    │
                │                                    │
                │ Yes                                │
                │                                    │
                ▼                                    │
┌──────────────────────────────┐                     │
│          Make Print          │                     │
└──────────────────────────────┘                     │
                │                                    │
                │                                    │
                │                                    │
┌───────────────▼──────────────┐                     │
│      User reviews print      │                     │
└──────────────────────────────┘                     │
                │                                    │
                │                                    │
                │                                    │
                ▼                                    │
                Λ                                    │
               ╱ ╲                                   │
              ╱   ╲                                  │
             ╱     ╲                                 │
            ╱  Good ╲  No                            │
           ▕ Enough? ▏───────────────────────────────┘
            ╲       ╱
             ╲     ╱
              ╲   ╱
               ╲ ╱
                V
                │
                │ Yes
                │
                ▼
    .───────────────────────.
   (          Done           )
    `───────────────────────'
```

**You stay in the conversation.** You do not type commands. Claude runs the builds, reads the checks, tracks the criteria and records the verdicts. The render sheet is written to a file and its path printed; you open it, because looking at it is the one step nothing can do for you. Keep it open in an editor that reloads on change and it updates in place as the design moves.

Your side of it is three things, and only three:

- **Judgment.** Is this the shape you meant? Nothing else can answer that.
- **The printer.** Slicing is manual in Bambu Studio, by design.
- **Words.** *"The hearts are too low."* *"That wall looks fragile."* *"It came out fine but the puck is a pain to get back out."*

Editing `spec.md` yourself is optional — dictate it if you prefer, though the first one is often easier to type than to describe.

**Each lap costs you one judgment call.** That is the expensive step and the only one nothing else can do — which is why the criteria, the renders, the assertions and the history all exist. They make the lap cheap, keep it honest, and stop you doing the same lap twice.

The outer loop matters most. A print teaches you something the geometry could not, and that usually revises the *spec* rather than the parameters.

**Nobody has to work out what comes next.** Every command that changes state ends by printing the one next move, derived from what is on disk — criteria missing, model newer than the render, verdict outstanding, print criteria still open. Claude reads it and acts on it:

```
 !! puck_base — Add criteria under '### Does it do its job?' in spec.md.
      Every criterion here is about construction. A list of geometric
      invariants will certify a part that is built perfectly and does nothing.
    tealight_holder — Record the print in prints.md and tick off what it settled.
      2 print-only criteria are still open.
```

Parts with nothing outstanding are left off it. A board is a list of things to do, and finished work listed as "nothing to do" crowds out the one part that needs something — which is exactly what a fresh clone used to get, four times over, about four lanterns somebody else finished. `./cad` on its own says where you are and what the one next move is.

## Why it's shaped this way

Designing a part is a **search**, and **you are the objective function**. Generating a candidate is cheap and getting cheaper; evaluating one costs a human judgment call and never gets cheaper at all. Your attention is the scarce resource, and every piece here spends less of it:

| | |
|---|---|
| acceptance criteria | The objective function, written down. Editing them *moves the target* — a new **generation**, which resets the history, because old verdicts answered a different question. |
| assertions in `check()` | The share of the objective compiled into code, evaluated forever after without spending you. |
| the render sheet | Makes evaluation possible for a reviewer who can't open a viewer. |
| `history.md` | A tabu list. Stops the search re-entering a basin it already left — the only way successive approximation degenerates into a random walk. |
| `cad next` | Removes the last tax: deciding what to do next. |
| `accepted/` | The frozen deliverable. |

Three consequences that cut against ordinary software instincts:

- **`model.py` is disposable, and that's fine.** The deliverable is an STL. Once a mesh prints and works, how it was produced has no further claim on anyone, and regenerating from a revised spec costs minutes. Nondeterminism between runs is exploration, not a defect.
- **Convergence is the only property that matters** — not reproducibility. A search that reaches an acceptable object has succeeded regardless of path.
- **Spec detail helps only when it constrains the *outcome*.** Detail that prescribes the *method* doesn't narrow the search, it replaces it, and over-prescribed specs measurably produce worse parts. The test for any line: does it change what counts as success, or only how to get there?

That last one is why the spec template tells you to **start vague**. A meticulous spec written before you've seen anything narrows the search to whatever you first imagined, and you never find out what else was available.

## A part

```
parts/<name>/
    spec.md        what it's for, and criteria a render can settle
    model.py       build(p) -> Part.  Nothing runs on import.
    notes.md       why the numbers are what they are
    history.md     what was tried, what was ruled out    (generated, PRIVATE)
    prints.md      what happened when it met the real world
    inspiration/   the source imagery it was made from
    build/         renders, meshes, params.json          (generated, ignored)
    accepted/      the frozen deliverable                (generated, TRACKED)
```

`spec.md` and `notes.md` are durable. `model.py` gets rewritten. `accepted/` exists because the STL is the real deliverable and the one artifact a respec *cannot* reproduce — a good verdict freezes the mesh, its params, the render sheet, and the exact generator that made it.

`history.md` is the one file that **never leaves the private tree**. One dated row per build reconstructs which evenings were spent how, so `cad promote` withholds it and strips dates from everything it does publish. See [PRIVACY.md](PRIVACY.md).

```python
@dataclass(frozen=True)
class P(Params):
    tealight_h: float = 16.0   # NOMINAL — never measured
    rim_clearance: float = 7.0 # the height knob; see notes.md

PARAMS = P()
PRINT_ROTATION = (0, 0, 0)     # modeled pose → print pose

def build(p: P) -> Part: ...

def check(part, p) -> None:
    g = geometry(p)   # derived values, shared by build() and check()
    # An LED puck emits from its top face and is opaque below, so a heart cut
    # level with the body is a dark hole no wall thickness can fix.
    assert g.heart_bottom >= g.puck_top, "the puck body would black out every heart"
```

Parameters are a frozen dataclass, so every mesh is written beside the exact values that produced it. Meshes are named by export time (`<part>-YYYYmmdd-HHMM.stl`) and `build/exports.jsonl` maps each one back to its parameters — a digest names the parameters, not the mesh, and a part reading a shared assembly can change shape without its digest moving. A dimension you can't trace to its inputs is one you'll re-derive by measuring a print.

`PRINT_ROTATION` separates the modeled pose from the printed one — the overhang check is meaningless in the wrong orientation, and an STL exported in the modeled pose lands on the plate needing a manual rotation nobody records. Leaving it undeclared makes every build say so.

## Commands

You should not need these — Claude runs them. They are documented because nothing is hidden behind the agent, and because you may want to drive a step by hand.

| | |
|---|---|
| `cad` | where you are and the one next move |
| `cad next [<name>]` | the single next action |
| `cad status` | every part, its stage, its history, the board |
| `cad new <name>` | scaffold at the spec stage |
| `cad build <name> [--stl]` | build → assert → check → render → export |
| `cad watch <name>` | rebuild on save |
| `cad accept <name> good\|bad\|mixed "why"` | record a verdict; freeze on good |
| `cad history <name>` | what was tried, what was ruled out |
| `cad sweep <name> wall=2,2.4,3` | variants rendered side by side |
| `cad stage <name> review` | move through the process |
| `cad promote <name>` | publish a scrubbed snapshot into `examples/`; re-run to refresh |

`cad build` writes the render sheet and prints its path; it does **not** open it. Pass `--open` if you want it launched. The default is the other way round because a viewer that seizes the desktop on every rebuild is intolerable in a loop that rebuilds constantly — and because a sheet held open in an editor that watches the file reloads quietly on its own, which is strictly better.

## Public and private

`examples/` is public and lives here. `parts/` is where real work happens — git-ignored, version-controlled separately, so your own designs stay private without leaving the working directory. Same commands drive both; which tree a part is in states whether it's *published*, not how it's built. See [PRIVACY.md](PRIVACY.md) — and if you have just cloned this and want to design something, put it in `parts/`; it is already ignored and `cad new` goes there by default.

`examples/` holds seven printed parts, all carrying their real record rather than a tidied one — one large object, a half-size variant of it, a set of four small ones, and a standalone:

| | |
|---|---|
| [`castle`](examples/castle/) | a haunted castle facade, 178 mm and eleven hours. **A print that failed for a reason that was never in the model**, and one recurring bug — geometry sized from one constraint and never checked against its surroundings — wearing six different costumes. |
| [`mini_castle`](examples/mini_castle/) | the castle at half size, as a **variant rather than a fork** — its `model.py` holds no geometry, it loads the castle's and subtracts two boxes. What happens when a scaled part meets a component that does not scale. |
| [`raven_lantern`](examples/raven_lantern/) | six ravens. Lost a *Nevermore* inscription on the way, and the README explains why the feature and the thing that killed it were the same feature. |
| [`witch_lantern`](examples/witch_lantern/) | five heads in profile. Printed *with* supports, which settled a rule the set had over-generalised. |
| [`ghost_lantern`](examples/ghost_lantern/) | four ghosts in lit windows — **inverted polarity**, the motif as material rather than as hole. |
| [`pumpkin_lantern`](examples/pumpkin_lantern/) | a jack-o'-lantern that **glows** rather than silhouettes, so wall thickness is an optical parameter. |
| [`owl`](examples/owl/) | a backlit silhouette on a branch, in two glued pieces. **The paper behind an opening is a finishing surface** — glued and tinted, one aperture gives a single-colour print a multi-colour face. |

Start with any one's `README.md`, then its `prints.md` — that is where the process earns its keep. [`examples/README.md`](examples/) orients the set, records what it has already ruled out, and walks through **adding a fifth lantern**: the four share one body, so a new one is a motif and its constraints and not much else.

## Scope and limits

`printer.py` holds every machine and material assumption in one place, read from your `printer.toml` — no part hardcodes a bed size or a nozzle. Slicing is manual, and the no-CLI-slicing boundary documented in `CLAUDE.md` is specific to Bambu hardware; other machines have their own slicers and their own answer.

Minimum wall thickness is not checked and there's no cheap reliable way to do it; thickness invariants belong in each part's `check()`. The overhang check reports planar faces only.

**`CLAUDE.md` is the real documentation** — it's what Claude reads on entering the repo, and it states the conventions and the process model in full. `.claude/skills/` holds three skills, one per stage where judgment is needed: `cad-spec` (draft and refine a spec through questioning), `cad-review` (read renders against criteria without rubber-stamping), `cad-print` (export, and record what the physical object taught you). If you change how the process works, change those — they shape the behaviour far more than any CLI flag.

If you want to change how the *harness* works — add a check, add a stage, teach it a new artifact — [`cadkit/README.md`](cadkit/README.md) is the tour: what each module buys you, which order to read them in, and the traps that have already cost real bugs.

## License

MIT. All of it — the harness, the parts, the notes, the pictures. Take any of it and do whatever you want, including selling things you make with it. Keep the copyright line somewhere and we're square.

One small ask, and it genuinely isn't a licence condition — just a nicety. Print one and keep it, or hand it to someone with a note saying *look what I made*, and you owe me nothing at all; that's what these are for. But if it goes out with real documentation attached — a shop listing, an instruction sheet, a class handout, a write-up — I'd appreciate a line saying where the design came from. A name and a link is plenty. Gift tags and love notes don't count.

And if you build something out of this, I'd love to see it. That one's pure nosiness.

Two things I should be honest about rather than let the licence quietly cover them. The reference pictures in `inspiration/` are AI-generated, so they're probably not copyrightable and definitely not mine to hand you — they're in the repo because you can't judge a traced outline without seeing what it was traced from. And the `.3mf` files are saved Bambu Studio projects: the settings are mine and you're welcome to them, but the format and whatever Bambu's own profiles put in there aren't mine to give away.

Nothing third-party is bundled in here, and every dependency — build123d, bd_warehouse, watchdog, numpy, Pillow — is permissive.
