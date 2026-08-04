# cadforge — status

The public repo: the harness and the worked example. Personal parts live in the
private `parts/` collection and have their own STATUS.md there — see
`PRIVACY.md` for the arrangement.

2026-08-04.

## Where things stand

| | |
|---|---|
| `cadkit/` | complete and exercised |
| `examples/desk_edge_hook` | builds, renders, checks clean — **never printed** |
| docs | README, CLAUDE.md, PRIVACY.md, three skills |

`./cad status` is the live view.

## What was built

- **Headless renderer** (`cadkit/render.py`) — tessellate → numpy z-buffer →
  PNG, with silhouette and crease edges; four orthographic views plus a cutaway
  on a contact sheet. No VTK, no GL, ~0.1 s per view. Review is an artifact
  anything can open, rather than a person watching a live viewer.
- **Part contract** (`cadkit/part.py`) — `build(p) -> Part`, nothing on import.
  Optional `check`, `pieces`, `SECTION`, `PRINT_ROTATION`. Two collections,
  public and private, treated identically.
- **Iteration history** (`cadkit/history.py`) — automatic parameter diffing and
  an oscillation guard that fires when a previously-judged parameter set comes
  back. Verified working.
- **Printability checks** (`cadkit/check.py`) — validity, bed fit, planar
  overhangs, mass. Explicit about what it does *not* check (true min wall).
- **`cad` CLI** — status / new / build / watch / accept / history / stage /
  sweep / promote.

## Open threads

- **`desk_edge_hook` has never been printed.** Every number in it is reasoned
  and none is validated. `grip` is the one most likely to be wrong and the one
  that decides whether the part works at all. Printing it would also test the
  layer-orientation claim its `notes.md` rests on — which is the lesson the
  whole example exists to teach.
- **Nobody has followed the README from a fresh clone and an empty venv.** The
  clone itself is verified; the `pip install` path is not.
- **Minimum wall thickness is not checked** and there is no cheap, reliable way
  to do it. Thickness invariants belong in each part's `check()`.
- **The overhang check reports small planar faces** on many parts. They are
  warnings by design, but the threshold has never been tuned against a real
  print.
- `cad sweep` only varies one parameter at a time. Two-parameter grids would be
  a natural extension and are not implemented.

## Next session

Read `CLAUDE.md` for the process, then `./cad status`. The obvious next move is
to print `desk_edge_hook`: it exercises the outer loop end to end, validates the
claim the example is built around, and `prints.md` / `cad accept` have never
been used on a real print.
