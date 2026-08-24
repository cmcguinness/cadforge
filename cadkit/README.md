# cadkit

The harness. About 3,100 lines of Python that turn "design a part" from a scripting exercise into a process with a memory.

**You do not need to read this to use cadforge.** Start at the repo root [`README.md`](../README.md) for what the thing is, and [`CLAUDE.md`](../CLAUDE.md) for the conventions a part must follow. This file is for when you want to change how the harness *works* — add a check, add a stage, teach it a new kind of artifact.

## The one idea

Designing a part is a **search**, and the human is the **objective function**. Generating a candidate is cheap; evaluating one costs a person's judgement and never gets cheaper. Every module here exists to spend less of that:

| module | what it buys you |
|---|---|
| [`part.py`](part.py) | The contract. What a `model.py` must provide, and how a spec's criteria are parsed. |
| [`check.py`](check.py) | The fraction of the objective function that got compiled into code. |
| [`render.py`](render.py) | Makes evaluation possible for a reviewer who cannot open a viewer. |
| [`history.py`](history.py) | A tabu list. Stops the search re-entering a basin it already left. |
| [`advise.py`](advise.py) | Removes the last tax: working out which move comes next. |
| [`project.py`](project.py) | Parts that *belong* together, as distinct from parts that *fit*. |
| [`printers.py`](printers.py) | Machine and material facts, so no part hardcodes a bed size. |
| [`cli.py`](cli.py) | The `cad` command. Wiring, and the only module that prints. |

## Reading order

If you are here to change something, read in this order — each one assumes the one before it.

**1. [`part.py`](part.py) — the contract.** Everything else is downstream of this. A part is a directory; `load()` imports its `model.py` and wraps it in a `LoadedPart` that knows how to `build()`, `check()`, orient for the plate, and split into `pieces()`. It also parses `spec.md`: the stage from front matter, the acceptance criteria from the three `###` headings, and `generation()` — a hash of the criteria *text* that scopes the iteration history.

Two subtleties worth knowing before you touch it. `find()` resolves a name to the **private** copy when a part exists in both trees, because promotion copies rather than moves and the published one is a snapshot that gets overwritten. And `generation()` **normalises whitespace** before hashing, because re-wrapping a criterion is not retargeting — learning that cost every part in the repo its history for about an hour.

**2. [`check.py`](check.py) — what runs on every build.** Six checks, each returning a `Result` with a severity: validity, volume and mass, bed fit, overhangs, a thickness *proxy*, and islands.

The one to understand is **islands versus overhangs**, because the distinction is easy to blur and expensive to miss. An overhang is material attached, on its own layer, to material that is supported: it leans out and droops, and usually survives. An island is a blob on a layer with *no path along that layer* to anything supported: it is extruded into open air and falls. Measured as a fraction of material the two are indistinguishable — a part that printed clean scored 0.51% unsupported and one that had to be cancelled scored 0.47%. Counting islands separated them completely: zero against fifteen.

An island is a **WARN**, not an error, because it is a decision — supports and their scars, or reshape so the feature is anchored — and which is right depends on the part.

**3. [`render.py`](render.py) — a software rasteriser.** Tessellate, project, z-buffer, edges, PNG. No VTK, no OpenGL, no viewer window that has to be open at the right moment; about 0.1 s a view. Four orthographic views plus a cutaway, with a reference grid and **a timestamp banner**, because an undated render is indistinguishable from a stale one and that has already been read here as though it showed a change it did not.

It is not a photograph and should not become one. The fidelity it has is the right fidelity for "is this the shape I meant?".

**4. [`history.py`](history.py) — the ledger.** `history.jsonl` is the record; `history.md` is generated from it and should never be hand-edited. Every build appends an entry when the parameters differ from the last, **with the diff computed rather than remembered**, and returning to a parameter set that already carries a verdict prints a loud warning. Everything is scoped by generation, so verdicts do not leak across a change in what "good" means.

**5. [`advise.py`](advise.py) — the decision procedure.** Ordered rules; the first that matches wins, because the earlier ones block the later ones. There is always exactly one next action, it is derivable from what is on disk, and it should be printed without being asked for.

**If you add a stage or an artifact, add its rule here.** An unhandled state that falls through to a vague suggestion is worse than no suggestion at all.

**6. [`cli.py`](cli.py) — the wiring.** One function per subcommand, and the only module that writes to the terminal. Keep it that way: everything else should be importable and testable without capturing stdout.

## Things that will bite you

**`cli.py` is 1070 lines and over the repo's own thousand-line guideline.** It has grown a command at a time.

**The decision (Charles, 2026-08-09) is to split it opportunistically, not now.** The next time it needs major surgery, that is the moment — do the split as part of the change rather than as a separate tidy-up. A refactor with no functional work attached is a change nobody can review against anything, and it would have to be rebuilt against every part in the repo to prove it changed nothing.

The natural seams, when the time comes: `cmd_build` and `cmd_promote` are the two heavy ones. `promote` in particular is nearly a self-contained subsystem — the scrubber, the artwork rules and the private/public policy — and answers to `PRIVACY.md` rather than to the design loop. `_freeze` belongs with `accept`. What should stay here is the argument parsing and the printing, because keeping every terminal write in one module is what lets the rest be imported and tested without capturing stdout.

Until then it is watched, not urgent: the guideline calls a thousand lines a minor problem and two thousand a pressing one.

**build123d has four silent traps**, all documented in [`CLAUDE.md`](../CLAUDE.md) and each of which has cost a real bug: a primitive constructed inside an open builder joins it twice; `add()` places relative to the *current workplane*; `.locate()` discards an existing transform; `Plane.XZ`'s normal is −Y. None of them raise, and the part still builds, is watertight, passes every check, and renders as something plausible.

**Checks run on `pieces()` when a part is multi-piece**, not on the assembly — an assembly's envelope is not a thing that ever goes on a plate. Each piece must therefore arrive already in its own print pose.

**`printer.py` at the repo root is not this package.** It reads the user's git-ignored `printer.toml`, written by `cad setup` from the profiles in `printers.py`. Until it runs, every bed-fit check and mass estimate is answering for a machine nobody owns, and the harness says so on every command.

## Adding a check

Write a function taking a `Part` and returning a `Result(name, severity, detail)`, and add it to the list `run()` iterates. Two rules learned the hard way:

- **Say what to do, not just what is wrong.** The islands message explains the difference from an overhang and names the decision, because "15 islands" on its own gets ignored.
- **Never silently skip.** The islands check used to give up on parts too large for its grid, so the biggest and riskiest parts got the least checking. It now coarsens the grid until it fits and reports the grid it used.
