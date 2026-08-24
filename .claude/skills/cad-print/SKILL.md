---
name: cad-print
description: Export a mesh for slicing, and record what happened when a part was printed. Use when exporting an STL or when the user reports the result of a print. Triggers on "export", "STL", "I printed it", "it came out ...".
---

# Exporting, and closing the outer loop

## Exporting

`./cad build <name> --stl` exports into `parts/<name>/build/`, in the part's declared print pose, with the parameter digest in the filename. A `FAIL` check blocks the export deliberately.

Slicing is **manual, in the Bambu Studio GUI**. Do not build CLI slicing or print submission — see CLAUDE.md; it has been ruled out and the CLI has no networking flags anyway. Hand the user the path and stop.

If the part has no `PRINT_ROTATION`, say so when handing over the file: the mesh is in the modeled pose and the orientation decision is still open.

## The accepted mesh is the deliverable

`cad accept <part> good|printed` freezes `build/` into `parts/<name>/accepted/` — the STL, its `params.json`, the render sheet, and a copy of the `model.py` that produced it. That directory is git-tracked; `build/` is not.

This matters because `model.py` is disposable by design. The moment the spec is revised the generator is rewritten, and without the freeze a working, printed object becomes unreproducible. Never delete or hand-edit `accepted/`; supersede it by accepting a later iteration.

## Recording a print

This is the highest-value thing in the repo and the easiest to skip, because at the moment of a successful print everything feels obvious.

1. Append an entry to `parts/<name>/prints.md`: settings, what came out, and **measured vs. modeled** for anything that differed.
2. `./cad accept <name> good|bad|mixed "<why>"` so the iteration history carries the verdict too.
3. If a measurement turned a `nominal` constraint into a `measured` one, update `spec.md` — and check whether any other part depends on it. If the value lives in a shared `assemblies/` interface, it almost certainly does, and every part on that interface needs rebuilding and re-reviewing.
4. Put the *reasoning* in `notes.md`, not in prints.md. If the discovery is better expressed as an invariant, add an assertion to `check()` and let `notes.md` explain it. Prefer a check that fails loudly over a comment that asks nicely.
5. `./cad stage <name> done` only when it is validated in the hand.

**Record successes, not just failures.** A design that works and nobody wrote down why is one refinement away from losing the property by accident.

The shape this takes in practice: something added during assembly — a liner, a shim, a washer, a bit of tape — quietly takes over part of a clearance the model still thinks is free. Everything works. Then a later session sees a rattle, tightens the clearance, and breaks it, because nothing in the model records that the clearance was already spoken for. If a print works *because* of something outside the model, that belongs in notes.md the same day.

## Publishing a part

`cad promote <name>` copies a snapshot of a private part into the public `examples/` tree; the private original stays authoritative. It is a publishing decision, not a file move — see PRIVACY.md. Run it without `--yes` first and **read what it lists**: `notes.md` and `history.md` carry measurements, dead ends and whatever was written straight after a failed print. That record is what makes a promoted part worth reading, and what deserves a look before it goes out.

Never promote on the user's behalf without showing them the dry run first.
