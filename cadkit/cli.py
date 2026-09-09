"""`cad` — one command per step of the design process.

    cad setup                   choose your printer and material (run once)
    cad new <name>              scaffold a part at the spec stage
    cad status                  every part, its stage, its history
    cad build <name>            build → assert → check → render → (optionally) export
    cad watch <name>            rebuild on save
    cad accept <name>           record a verdict on the current iteration
    cad history <name>          what has been tried, and what was ruled out
    cad stage <name> <stage>    advance (or rewind) the design process
    cad sweep <name> k=a,b,c    render a variant per value, side by side
    cad next [<name>]           the single next action

`build` is the workhorse and does the whole inner loop in one shot, because a
review step that requires three commands is a review step that gets skipped.

Every command that changes state ends by printing the next action. Working out
what to do next is itself a tax on the scarce resource here — your attention —
so the harness pays it instead of you. See cadkit/advise.py.

SPLIT THIS FILE THE NEXT TIME IT NEEDS MAJOR SURGERY
----------------------------------------------------
It is over a thousand lines, past this repo's own guideline, and it has grown a
command at a time. The decision (Charles, 2026-08-09) is to split it **as part
of the next substantial change**, not as a standalone refactor: a tidy-up with
no functional work attached is a change nobody can review against anything, and
it would have to be rebuilt against every part in the repo just to prove it
changed nothing.

If you are already here doing real work, take the opportunity. The seams:

  * `cmd_promote` and its helpers (`_scrub`, `_publish_file`, `_artwork`,
    `_undated`) are nearly a self-contained subsystem. They answer to
    PRIVACY.md rather than to the design loop, which is a different concern
    from everything else in this file.
  * `cmd_build` is the other heavy one.
  * `_freeze` belongs with `cmd_accept`.

What stays: argument parsing, and the printing. **This is the only module that
writes to the terminal, and keeping it that way is what lets everything else be
imported and tested without capturing stdout.** A split that scatters `print()`
across four modules has made things worse, not better.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

from . import advise, check as checks
from . import history, part as partlib
from . import project as projectlib
from .part import (COLLECTIONS, PRIVATE_DIR, PUBLIC_DIR, ROOT, STAGES,
                   STAGE_ORDER, collection_of, find)


def _hr(title: str = "") -> None:
    print(f"\n\033[1m{title}\033[0m" if title else "")


# Pixels per view on the contact sheet. 520 was chosen when the sheet was
# glanced at; it is read closely, and at that size a crenellation is four pixels
# and a mesh artefact is none. Rendering is O(size^2) and still seconds.
RENDER_SIZE = 900


def _open(path) -> bool:
    """Show a file to the human, using the OS viewer. **Opt in only.**

    This used to happen on every build, on the reasoning that the sheet is the
    one artifact a person has to look at and the intended way to work here is a
    conversation rather than a terminal. That reasoning was wrong in a way worth
    writing down: an agent driving this repo runs `cad build` dozens of times in
    a session, and each one stole focus and threw an image viewer over whatever
    the human was doing. A tool that interrupts on a cadence the human does not
    control is not helping them review, it is taking their attention by force —
    which is the exact thing the rest of this harness exists to conserve.

    Printing the path costs one line and the human opens it when they are
    ready. Pass --open to have it appear.
    """
    import shutil
    import subprocess
    import sys

    opener = ("open" if sys.platform == "darwin"
              else "xdg-open" if sys.platform.startswith("linux") else None)
    if not opener or not shutil.which(opener):
        return False
    try:
        subprocess.run([opener, str(path)], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except OSError:
        return False


def _show_next(part_dir, prefix: str = "\nnext") -> None:
    """Print the one next action. Called at the end of every command that
    changes state, so the human never has to work out what follows."""
    a = advise.next_action(part_dir)
    mark = "\033[33m!!\033[0m" if a.urgent else "→"
    print(f"\033[1m{prefix}:\033[0m {mark} {a.action}")
    print(f"      {a.why}")
    if a.command:
        print(f"      \033[1m{a.command}\033[0m")


def _fmt_stage(stage: str) -> str:
    i = STAGE_ORDER.index(stage) if stage in STAGE_ORDER else 0
    return f"[{i + 1}/{len(STAGE_ORDER)} {stage}]"


# --- commands --------------------------------------------------------------
_PRIVATE_README = """# parts — private

Your own designs live here. This directory is **git-ignored by `cadforge`** — nothing under it is ever seen by the public repo — so your work stays private without leaving the working directory. `cad new` scaffolds here by default.

Version-control it separately if you want history: `git init` right here gives you a private repo nested inside the public one, which is the arrangement `PRIVACY.md` describes.

Everything works exactly as it does in `examples/`: `cad status`, `cad build <name>` and the rest all run from the `cadforge/` root, and neither the commands nor the checks care which collection a part is in. Which tree a part sits in states whether it is *published*, not how it is built.

Publishing is `cad promote <name>`, and it is a decision rather than a file move — it copies a scrubbed snapshot into `examples/`, withholds `history.md` entirely and strips dates from what does go out. Read `../PRIVACY.md` before running it.

`projects/` and `assemblies/` under here are the private halves of the ones at the repo root. They merge with the public ones automatically, so a private project needs no special handling to stay private.
"""


def _ensure_private_collection() -> None:
    """Create `parts/` at install time.

    It is git-ignored in full, so a fresh clone arrives without it and the one
    directory the newcomer is actually supposed to work in is the one that is
    not there. `cad new` creates it on demand, but that is too late to answer
    "where do my own designs go?" — which is a question install should have
    already answered.

    The README goes with it because an empty directory is its own small
    mystery, and because git cannot carry one anyway.
    """
    existed = PRIVATE_DIR.is_dir()
    PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
    readme = PRIVATE_DIR / "README.md"
    if not readme.exists():
        readme.write_text(_PRIVATE_README)
    if not existed:
        print(f"created {PRIVATE_DIR.relative_to(ROOT)}/ — your own parts go here, "
              f"git-ignored. See {readme.relative_to(ROOT)}.")


def cmd_setup(args) -> int:
    """Choose the machine and material every check answers for.

    Part of installation, not an advanced option: until this runs, bed-fit
    checks, mass estimates and minimum-wall assertions are all answering for a
    generic printer nobody owns.
    """
    from . import printers

    if args.list or (not args.printer and not sys.stdin.isatty()):
        print("printers:")
        for k, v in printers.PRINTERS.items():
            print(f"  {k:<10} {v.name:<24} "
                  f"{v.bed_x:.0f} × {v.bed_y:.0f} × {v.bed_z:.0f} mm")
        print("\nmaterials:")
        for k, v in printers.MATERIALS.items():
            print(f"  {k:<10} {v.name:<24} {v.density} g/cm3")
        print("\n  ./cad setup --printer <key> --material <key>")
        print("  Sizes are NOMINAL — measure your own bed before trusting a part "
              "that lands near its edge.")
        return 0

    printer_key, material_key = args.printer, args.material

    if not printer_key:
        for k, v in printers.PRINTERS.items():
            print(f"  {k:<10} {v.name} "
                  f"({v.bed_x:.0f} × {v.bed_y:.0f} × {v.bed_z:.0f} mm)")
        printer_key = input("\nprinter [a1mini]: ").strip() or "a1mini"
    if not material_key:
        for k, v in printers.MATERIALS.items():
            print(f"  {k:<10} {v.name}")
        material_key = input("\nmaterial [pla]: ").strip() or "pla"

    path = printers.write(ROOT, printer_key, material_key)
    print(f"\nwrote {path.relative_to(ROOT)}")
    _ensure_private_collection()

    # Re-read through the real module so what we print is what parts will see.
    import importlib
    import printer as printer_mod
    importlib.reload(printer_mod)
    print()
    print(printer_mod.describe())
    print("\nThese are nominal figures. Measure your bed and edit "
          f"{path.name} if a part will land near its edge.")
    return 0


def cmd_status(args) -> int:
    import printer as printer_mod
    _hr("machine")
    print(printer_mod.describe())
    if not printer_mod.CONFIGURED:
        print("\n  \033[1m./cad setup\033[0m")

    dirs = partlib.working_dirs()
    if not dirs:
        _hr("next action")
        _show_orientation(dirs, verbose=True)
        return 0
    width = max(len(d.name) for d in dirs)

    # Grouped by project, because a set is the unit people actually think in:
    # "are the lanterns done" is a real question and "is raven_lantern done" is
    # a detail of it. Unaffiliated parts are listed too, under their own
    # heading — most parts belong to no set and hiding them would be wrong.
    for pname, members in projectlib.group(dirs):
        if pname is None:
            label = "unaffiliated" if len(list(projectlib.group(dirs))) > 1 else "parts"
            print(f"\n\033[1m{label}\033[0m")
        else:
            known = projectlib.exists(pname)
            proj = projectlib.find(pname) if known else None
            tag = f"  ({proj.collection})" if proj else "  \033[33m(no project dir)\033[0m"
            print(f"\n\033[1mproject: {pname}\033[0m{tag}")
            if proj and proj.summary():
                print(f"  {proj.summary()[:100]}")
        print(f"  {'part'.ljust(width)}  where     stage      history")
        print("  " + "-" * (width + 46))
        for d in members:
            spec = d / "spec.md"
            stage = partlib.read_stage(spec)
            gen = partlib.generation(spec)
            # A part published from a private working copy is in both trees;
            # the row describes the working copy and marks that a snapshot of
            # it is public.
            where = collection_of(d) + ("*" if partlib.published_twin(d) else "")
            print(f"  {d.name.ljust(width)}  {where:<8}  {stage:<9}  "
                  f"{history.summary(d, gen)}")
        if any(partlib.published_twin(d) for d in members):
            print("  * a scrubbed snapshot is published in examples/")

    _hr("next action, most urgent first")
    printed = _show_orientation(dirs, verbose=True)
    rows = advise.board(dirs)
    for d, a in rows:
        mark = "\033[33m!!\033[0m" if a.urgent else "  "
        print(f" {mark} \033[1m{d.name}\033[0m — {a.action}")
        print(f"      {a.why}")
        if a.command:
            print(f"      {a.command}")
        print()
    if not rows and not printed:
        print(f"    nothing outstanding across {len(dirs)} parts.\n")
    return 0


def cmd_build(args) -> int:
    lp = partlib.load(args.name)
    started = time.monotonic()

    _hr(f"{lp.name} {_fmt_stage(lp.stage())}")
    print(lp.params.describe())

    part = lp.build()
    print(f"\nbuilt in {time.monotonic() - started:.2f}s  "
          f"(params {lp.params.digest()})")

    # --- history, and the oscillation guard --------------------------------
    gen = partlib.generation(lp.spec_path)
    entry, revisits = history.record(lp.dir, lp.params, note=args.note or "",
                                     generation=gen)
    if revisits:
        print("\n\033[33m!! these exact parameters were used before:\033[0m")
        for e in revisits:
            print(f"     iteration #{e.i} ({e.date}) → \033[1m{e.verdict}\033[0m"
                  + (f" — {e.note}" if e.note else ""))
        print("   check history.md before spending more effort here.")
    elif entry and entry.changed:
        print(f"\niteration #{entry.i}: "
              + ", ".join(f"{k} {a} → {b}" for k, (a, b) in entry.changed.items()))
    elif entry:
        print(f"\niteration #{entry.i}: initial")

    # --- automatic checks --------------------------------------------------
    # Checks run on the part as it sits on the plate, not as it was modeled.
    _hr("checks")
    plated = lp.oriented(part)
    pieces = lp.pieces()
    if pieces:
        # Check each printed piece on its own; the assembly's envelope is not a
        # thing that ever goes on a plate.
        results = []
        for pname, pshape in pieces.items():
            for r in checks.run(pshape):
                results.append(checks.Result(f"{pname}/{r.name}", r.severity, r.detail))
    else:
        results = checks.run(plated)
    if lp.print_rotation is None and not pieces:
        results.append(checks.Result(
            "orientation", checks.Severity.WARN,
            "no PRINT_ROTATION declared — checked as modeled, which may not be "
            "how it is printed"))
    for r in results:
        print(" ", r)
    verdict = checks.worst(results)

    # --- renders -----------------------------------------------------------
    if not args.no_render:
        from . import render as rnd
        outdir = lp.build_dir / "review"
        t = time.monotonic()
        written = rnd.write_views(part, outdir, size=args.size, section_normal=lp.section)
        print(f"\nrendered {len(written) - 1} views in {time.monotonic() - t:.2f}s")
        print(f"  \033[1m{written[0].relative_to(ROOT)}\033[0m")
        if getattr(args, "open", False) and _open(written[0]):
            print("  (opened for review)")

    # --- the live viewer, on request ---------------------------------------
    # Additive, and off by default. The render sheet stays the artifact review
    # is done against: it is a file, so it can be re-read, attached to a note,
    # or looked at by someone who is not sitting in front of this machine — and
    # a part pushed at a viewer with no tab attached succeeds silently and shows
    # nothing, which is exactly the failure that made it unfit as THE loop.
    #
    # None of which is an argument against spinning the thing by hand. Rotating
    # a shape is genuinely better than five fixed views for "what IS that", and
    # this is one flag.
    if getattr(args, "view", False):
        try:
            from ocp_vscode import show
            show(part, names=[lp.name])
            print("\n  pushed to the ocp_vscode viewer")
        except Exception as exc:
            print(f"\n\033[33m  viewer unavailable: {exc}\033[0m")
            print("    the render sheet above is unaffected.")

    # --- params provenance -------------------------------------------------
    lp.build_dir.mkdir(parents=True, exist_ok=True)
    (lp.build_dir / "params.json").write_text(
        json.dumps({"part": lp.name, "digest": lp.params.digest(),
                    "params": lp.params.to_dict()}, indent=2, default=str) + "\n")

    # --- export ------------------------------------------------------------
    if args.stl:
        if verdict is checks.Severity.FAIL:
            print("\n\033[31mnot exporting: a check FAILed\033[0m")
            return 1
        from build123d import export_stl

        # Meshes are named by EXPORT TIME, not by parameter digest.
        #
        # The digest names the parameters, which is not the same as naming the
        # mesh, and the difference bites as soon as a part reads a shared
        # assembly: change the assembly and the geometry changes while the
        # digest does not. Two different objects then claim the same filename
        # and the second silently overwrites the first — which happened, to this
        # part, between two prints of different heights.
        #
        # A timestamp cannot collide with an earlier export whatever changed to
        # produce it, which is the property actually wanted from a filename.
        # The digest is still recorded in params.json below, where it belongs:
        # it answers "which parameters", not "which file".
        stamp = time.strftime("%Y%m%d-%H%M")
        # Exported in the print pose, so the mesh drops onto the plate ready to
        # slice. A rotation done by hand in the slicer is a step nobody records.
        exported = []
        if pieces:
            for pname, pshape in pieces.items():
                out = lp.build_dir / f"{lp.name}-{pname}-{stamp}.stl"
                export_stl(pshape, str(out))
                exported.append(out)
        else:
            out = lp.build_dir / f"{lp.name}-{stamp}.stl"
            export_stl(plated, str(out))
            exported.append(out)
        for out in exported:
            print(f"\nexported {out.relative_to(ROOT)}")

        # Append rather than overwrite: this is the mesh↔parameters ledger, and
        # it is only useful if it still describes meshes exported last week.
        manifest = lp.build_dir / "exports.jsonl"
        with manifest.open("a") as fh:
            for out in exported:
                fh.write(json.dumps({
                    "stl": out.name,
                    "exported": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "digest": lp.params.digest(),
                    "params": lp.params.to_dict(),
                }, default=str) + "\n")
        print(f"  recorded in {manifest.relative_to(ROOT)}")
        print("  slice it in Bambu Studio — see CLAUDE.md; there is no CLI path.")

    # --- what the reviewer is supposed to be checking ----------------------
    # Grouped by axis, function first. An unstated axis stays unconstrained no
    # matter how detailed the others get, so the grouping is the point — a
    # section that is empty is visible as a gap rather than an absence.
    if not args.no_render:
        grouped = partlib.criteria_by_axis(lp.spec_path)
        if any(grouped.values()):
            _hr("acceptance criteria — read the renders against these")
            for axis in partlib.AXIS_ORDER:
                items = grouped[axis]
                if not items:
                    continue
                print(f"\n  \033[1m{partlib.AXIS_LABEL[axis]}\033[0m")
                for c in items:
                    print(f"    [{'x' if c.checked else ' '}] {c.text}")
            if not grouped[partlib.FUNCTION] and not grouped[partlib.UNCLASSIFIED]:
                print("\n  \033[33m!! no criteria on the function axis — geometric "
                      "invariants alone\033[0m")
                print("     will certify a part that is built perfectly and does nothing.")

    _show_next(lp.dir)
    return 1 if verdict is checks.Severity.FAIL else 0


def cmd_render(args) -> int:
    args.no_render = False
    args.stl = False
    args.note = ""
    return cmd_build(args)


def cmd_watch(args) -> int:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    import threading

    lp_dir = find(args.name)
    target = lp_dir / "model.py"
    if not target.is_file():
        raise SystemExit(f"no such part: {args.name}")
    watched = {target.resolve(), (ROOT / "printer.py").resolve()}

    lock = threading.Lock()

    def run():
        with lock:
            print("\n" + "=" * 64)
            try:
                cmd_build(argparse.Namespace(
                    name=args.name, no_render=False, stl=False,
                    size=args.size, note="", open=False))
            except SystemExit as exc:
                print(f"\033[31m{exc}\033[0m")
            except Exception:
                import traceback
                traceback.print_exc()
            print("\nwatching — ctrl-c to stop")

    class H(FileSystemEventHandler):
        def __init__(self):
            self.t: threading.Timer | None = None

        def on_any_event(self, event):
            if event.is_directory or event.event_type == "opened":
                return
            try:
                if Path(str(event.src_path)).resolve() not in watched:
                    return
            except OSError:
                return
            if self.t:
                self.t.cancel()
            self.t = threading.Timer(0.3, run)
            self.t.start()

    obs = Observer()
    h = H()
    for d in {p.parent for p in watched}:
        obs.schedule(h, str(d), recursive=False)
    obs.start()          # start before the first build: importing OCP is slow
    run()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nstopping")
    finally:
        obs.stop()
        obs.join()
    return 0


def _freeze(part_dir, entry) -> list:
    """Copy the mesh and the exact source that produced it into accepted/.

    The STL is the deliverable, and it is the only artifact here that a spec
    revision cannot regenerate: `model.py` is disposable by design and will be
    rewritten. Leaving the accepted mesh in git-ignored build output means a
    working, printed object is one revision away from being unrecoverable.

    So an accepted iteration is frozen: the mesh as printed, the parameters
    that produced it, and a copy of the generator. Tracked in git, unlike
    build/.
    """
    import json
    import shutil

    build = part_dir / "build"
    # ONLY the meshes this iteration actually produced. `build/` accumulates
    # every export ever made, and copying them all left an accepted/ directory
    # holding four candidate ghosts with nothing to say which was the accepted
    # one — the opposite of what freezing a deliverable is for.
    #
    # `exports.jsonl` is the ledger that answers it: filename to params digest.
    #
    # The digest comes from the *iteration being accepted*, not from the model
    # on disk: accepting is a judgement about a mesh that already exists, and
    # `model.py` may well have moved on since it was exported.
    digest = entry.digest or ""
    wanted = set()
    ledger = build / "exports.jsonl"
    if ledger.is_file():
        for line in ledger.read_text().splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            d = e.get("digest") or ""
            # Either may be the abbreviated form; compare on the shorter.
            if digest and d and (d.startswith(digest) or digest.startswith(d)):
                wanted.add(e.get("stl"))
    stls = sorted(build.glob("*.stl"))
    if wanted:
        stls = [f for f in stls if f.name in wanted]
    elif stls:
        print(f"  \033[33mno export ledger entry for {digest}\033[0m — "
              f"freezing all {len(stls)} mesh(es) in build/, which may include "
              f"meshes from other iterations")
    if not stls:
        return []

    out = part_dir / "accepted"
    out.mkdir(exist_ok=True)
    written = []
    for f in stls:
        shutil.copy2(f, out / f.name)
        written.append(out / f.name)
    for extra in ("params.json",):
        src = build / extra
        if src.is_file():
            shutil.copy2(src, out / extra)
            written.append(out / extra)

    # The slicer project, if one was saved into build/. It is a DELIVERABLE and
    # the most irreplaceable file a part ever has: plate layout, support
    # configuration and per-object tweaks that nothing in this repo
    # regenerates. `build/` is declared disposable and git-ignored, so a .3mf
    # left there is one careless command from gone — and that is not
    # hypothetical. Two have already been lost that way: castle's, carrying
    # settings that took two failed eleven-hour prints to find, and
    # pumpkin_lantern's.
    for proj in sorted(build.glob("*.3mf")) + sorted(build.glob("*.gcode.3mf")):
        dest = out / _undated(proj.name)
        if dest not in written:
            shutil.copy2(proj, dest)
            written.append(dest)
    shutil.copy2(part_dir / "model.py", out / "model.py")
    written.append(out / "model.py")
    sheet = build / "review" / "sheet.png"
    if sheet.is_file():
        shutil.copy2(sheet, out / "sheet.png")
        written.append(out / "sheet.png")
    (out / "ACCEPTED.md").write_text(
        f"# {part_dir.name} — accepted iteration #{entry.i}\n\n"
        f"- **date:** {entry.date}\n"
        f"- **verdict:** {entry.verdict}\n"
        f"- **params digest:** `{entry.digest}`\n"
        f"- **generation:** `{entry.generation}` (hash of the acceptance criteria)\n"
        f"- **note:** {entry.note or '—'}\n\n"
        # One line per paragraph — see the note in cadkit/history.py.
        "This directory is the deliverable, frozen. `model.py` here is the exact "
        "generator that produced this mesh — the one in the part directory has "
        "moved on. Do not edit anything in here; supersede it by accepting a "
        "later iteration.\n")
    written.append(out / "ACCEPTED.md")
    return written


def cmd_accept(args) -> int:
    d = find(args.name)
    if not d.is_dir():
        raise SystemExit(f"no such part: {args.name}")
    e = history.set_verdict(d, args.verdict, note=args.note or "", i=args.i)
    print(f"iteration #{e.i} → {e.verdict}" + (f" — {e.note}" if e.note else ""))
    print(f"updated {(d / 'history.md').relative_to(ROOT)}")

    # A good or printed verdict is the moment the mesh becomes the deliverable.
    if e.verdict in ("good", "printed"):
        frozen = _freeze(d, e)
        if frozen:
            print(f"\nfroze the deliverable → {(d / 'accepted').relative_to(ROOT)}/")
            for f in frozen:
                print(f"  {f.name}")
        else:
            print("\n(no mesh to freeze — run `cad build --stl` first)")

    _show_next(d)
    return 0


def _show_orientation(dirs, verbose: bool = False) -> bool:
    """Print the repo-wide advice. True if anything was printed."""
    lines = advise.orientation(dirs)
    for a in lines:
        mark = "\033[33m!!\033[0m" if a.urgent else "  "
        print(f" {mark} \033[1m{a.action}\033[0m")
        if verbose:
            print(f"      {a.why}")
        if a.command:
            print(f"      {a.command}")
        if verbose:
            print()
    return bool(lines)


def cmd_next(args) -> int:
    if args.name:
        _show_next(find(args.name), prefix=args.name)
        return 0
    dirs = partlib.working_dirs()
    printed = _show_orientation(dirs)
    rows = advise.board(dirs)
    for d, a in rows:
        mark = "\033[33m!!\033[0m" if a.urgent else "  "
        print(f" {mark} \033[1m{d.name}\033[0m — {a.action}")
        if a.command:
            print(f"      {a.command}")
    if not rows and not printed:
        print(f"    nothing outstanding across {len(dirs)} parts.")
    return 0


def cmd_history(args) -> int:
    d = find(args.name)
    md = d / "history.md"
    if not md.is_file():
        history.render_markdown(d)
    print(md.read_text())
    return 0


def cmd_stage(args) -> int:
    d = find(args.name)
    spec = d / "spec.md"
    if not spec.is_file():
        raise SystemExit(f"no spec.md for {args.name}")
    before = partlib.read_stage(spec)
    partlib.set_stage(spec, args.stage)
    print(f"{args.name}: {before} → {args.stage}")
    print(f"  {STAGES[args.stage]}")
    _show_next(d)
    return 0


def cmd_new(args) -> int:
    d = (PUBLIC_DIR if args.public else PRIVATE_DIR) / args.name
    if d.exists():
        raise SystemExit(f"{d} already exists")
    tpl = ROOT / "template"   # public: a fresh clone must be able to scaffold
    if not tpl.is_dir():
        raise SystemExit(f"missing template at {tpl}")
    import shutil
    d.parent.mkdir(parents=True, exist_ok=True)   # parts/ is absent in a fresh clone
    shutil.copytree(tpl, d)
    for f in list(d.rglob("*.md")) + list(d.rglob("*.py")):
        f.write_text(f.read_text().replace("_template", args.name))
    if args.project:
        if not projectlib.exists(args.project):
            print(f"\n\033[33m  no project '{args.project}' yet\033[0m — "
                  f"create {projectlib.DIRNAME}/{args.project}/project.md to describe it")
        projectlib.set_project(d / "spec.md", args.project)
        print(f"  declared project: {args.project}")
    print(f"created {d.relative_to(ROOT)}")
    _show_next(d)
    return 0


def cmd_project(args) -> int:
    """List projects, or show one and who belongs to it."""
    dirs = partlib.working_dirs()
    if not args.name:
        projects = projectlib.all_projects()
        if not projects:
            print("no projects yet.\n"
                  "  A project groups parts that BELONG together — a shared\n"
                  "  envelope, material and standards — as opposed to assemblies/,\n"
                  "  which is for parts that must FIT each other.\n"
                  f"  Create {projectlib.DIRNAME}/<name>/project.md to start one.")
            return 0
        for p in projects:
            n = len(projectlib.members(p.name, dirs))
            print(f"  \033[1m{p.name:<24}\033[0m {p.collection:<8} {n} part(s)")
            if p.summary():
                print(f"    {p.summary()[:96]}")
        return 0

    p = projectlib.find(args.name)
    _hr(p.title())
    print(f"  {p.dir.relative_to(ROOT)}   ({p.collection})")
    if p.shared.is_file():
        print(f"  shared numbers: {p.shared.relative_to(ROOT)}")
    if not p.doc.is_file():
        print("\n  \033[33mno project.md\033[0m — the set's shared decisions have "
              "nowhere to live, so they will end up scattered through whichever "
              "part happens to discover them.")
    members = projectlib.members(p.name, dirs)
    _hr("members")
    if not members:
        print("  none yet. A part joins by declaring `project: "
              f"{p.name}` in its spec.md front matter.")
    for d in members:
        spec = d / "spec.md"
        print(f"  {d.name:<24} {collection_of(d):<8} {partlib.read_stage(spec):<9} "
              f"{history.summary(d, partlib.generation(spec))}")
    return 0


# Never published. The iteration ledger is the most useful thing in a part and
# also the most revealing: one dated row per build reconstructs which evenings
# were spent how. It stays in the working copy, where it does its actual job of
# stopping the search circling.
PUBLISH_EXCLUDE = {"history.jsonl", "history.md"}

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".pxd"}

# Artwork kept in the working copy but NOT published. A .pxd is a Pixelmator
# working document — layers, history, whatever was tried and hidden — and it is
# an editable source rather than a deliverable. The exported .png is what a
# reader needs to see what the part was made from; the working file is the
# author's, in the same way `history.md` is.
PRIVATE_ART_SUFFIXES = {".pxd", ".psd", ".xcf", ".ai", ".afdesign", ".sketch"}

_ISO = r"20\d\d-\d\d-\d\d"
# `<part>-YYYYmmdd-HHMM.stl` — the export stamp, which is precise to the minute.
# The time is optional because not every artifact here is written by `cad build`:
# a slicer project is saved by hand and gets named `<part>-YYYYmmdd.3mf`. That
# form once published a date, because a pattern that demanded `-HHMM` matched
# nothing and passed the name through silently — the one failure mode the date
# scrubbing is supposed not to have.
_STAMP = re.compile(r"-(20\d{6})(?:-(\d{4}))?(?=\.[A-Za-z0-9]+\b|$)")


def _undated(name: str) -> str:
    """Strip the export timestamp from a mesh filename."""
    return _STAMP.sub("", name)


def _scrub(text: str) -> tuple[str, int]:
    """Remove calendar information from a file bound for publication.

    Removing `history.md` alone does not achieve much: the print log's headings
    are dated, `ACCEPTED.md` carries a date field, and the accepted mesh is
    named to the minute. Any one of them reconstructs the schedule that
    dropping the ledger was meant to protect.
    """
    n = 0

    def sub(pattern, repl, s):
        nonlocal n
        s, k = re.subn(pattern, repl, s)
        n += k
        return s

    # `### 2026-08-06 — iteration #25, printed at 50%` → `### Iteration #25, …`
    def _heading(m):
        rest = m.group(2)
        return m.group(1) + (rest[:1].upper() + rest[1:] if rest else rest)
    text = sub(rf"(?m)^(#{{1,6}} +){_ISO} +[—-] +(.*)$", _heading, text)

    # `- **date:** 2026-08-07` — the whole line goes.
    text = sub(rf"(?m)^ *[-*] +\*\*date:\*\* +{_ISO} *\n", "", text)

    # `(measured 2026-08-04, calipers)` → `(measured, calipers)`
    text = sub(rf" +{_ISO}(?=[,)])", "", text)
    # `(2026-08-04, calipers)` → `(calipers)`. No leading space to consume, so
    # the rule above cannot see it — this form is common in spec front matter.
    text = sub(rf"\({_ISO}, +", "(", text)
    text = sub(rf"(?i)\b(measured|taken|MEASURED) +{_ISO}\b", r"\1", text)

    # `(2026-08-04)` — a bare parenthetical date carries nothing else.
    text = sub(rf" *\({_ISO}\)", "", text)
    # `Settled 2026-08-05: five` / `on this part, 2026-08-05:` → drop the date,
    # keep the clause and its colon.
    text = sub(rf",? +{_ISO}(?=:)", "", text)
    # `ABANDONED 2026-08-04 — …` → `ABANDONED — …`
    text = sub(rf" +{_ISO}(?= +[—–-] )", "", text)
    # `settled by the 2026-08-05 print` → `settled by that print`
    text = sub(rf"\bthe +{_ISO} +", "that ", text)

    # References to artwork sources that are withheld. Left in, they are
    # dangling pointers in a published part — the reader is told to look at a
    # file that was deliberately not shipped.
    for suf in PRIVATE_ART_SUFFIXES:
        text = sub(rf"`[^`]*\{suf}`,?[ ]*", "", text)

    # Timestamped mesh names referenced in prose.
    text = sub(_STAMP.pattern, "", text)

    # Anything left. Deliberately loud rather than silent: if this shows up in a
    # published file it means the scrubber met a form it did not know, and that
    # is worth seeing rather than papering over.
    text = sub(rf"\b{_ISO}\b", "[date removed]", text)
    return text, n


def _publish_file(src: Path, dst: Path, changes: list) -> None:
    import shutil
    if src.suffix in (".md", ".py", ".txt", ".json", ".jsonl"):
        scrubbed, n = _scrub(src.read_text(errors="replace"))
        dst.write_text(scrubbed)
        changes.append(n)
    else:
        shutil.copy2(src, dst)
        changes.append(0)


def _all_art(part_dir: Path) -> list[Path]:
    """Every image beside the part, including sources that stay private."""
    out = []
    d = part_dir / "inspiration"
    if d.is_dir():
        out += [f for f in d.iterdir() if f.is_file() and not f.name.startswith(".")]
    out += [f for f in part_dir.iterdir()
            if f.is_file() and f.suffix in IMAGE_SUFFIXES]
    return sorted(out, key=lambda p: p.name)


def _artwork(part_dir: Path) -> list[Path]:
    """Source imagery: `inspiration/` only, minus the editable working files.

    This is what the part was made *from*. A part traced from a picture is not
    fully described without it, which is why it publishes.
    """
    d = part_dir / "inspiration"
    if not d.is_dir():
        return []
    return sorted((f for f in d.iterdir()
                   if f.is_file() and not f.name.startswith(".")
                   and f.suffix.lower() not in PRIVATE_ART_SUFFIXES),
                  key=lambda p: p.name)


def _root_images(part_dir: Path) -> list[Path]:
    """Images at the part root, published **at the root**, not into `inspiration/`.

    These are the opposite of artwork: a photograph of the finished object, a
    detail crop, a diagram. Filing them under `inspiration/` would say the part
    was made *from* them, which is a lie about a photo of the result.

    Publishing them where they sit is also what keeps a README portable. The
    part directory and its published snapshot are the same shape, so a relative
    `![](finished_owl.jpg)` resolves identically in both trees — and a link that
    works privately and 404s publicly is the kind of breakage nobody sees until
    a stranger reads it.
    """
    return sorted((f for f in part_dir.iterdir()
                   if f.is_file() and f.suffix in IMAGE_SUFFIXES
                   and f.suffix.lower() not in PRIVATE_ART_SUFFIXES),
                  key=lambda p: p.name)


def cmd_promote(args) -> int:
    """Publish a private part into examples/.

    This is a publishing decision, not a file move, and the command is built to
    make that hard to forget. `notes.md`, `history.md` and `prints.md` carry the
    whole record of how a design went wrong — measurements, dead ends, whatever
    was muttered after a failed print. That record is what makes a promoted part
    worth reading, and it is exactly what deserves a look before it goes out.

    So: nothing is copied until the files have been listed and confirmed, and a
    part that depends on a still-private assembly is refused outright — it would
    be a broken example the moment somebody cloned the repo.
    """
    import shutil

    src = find(args.name)     # resolves to the private copy where both exist
    if collection_of(src) == "public":
        raise SystemExit(
            f"{args.name} lives only in examples/ — there is no working copy "
            f"to publish from.")
    dst = PUBLIC_DIR / args.name    # may exist: re-promoting refreshes it

    # Refuse to publish a part that imports something that stays private.
    model = (src / "model.py").read_text()
    private_assemblies = set()
    if (PRIVATE_DIR / "assemblies").is_dir():
        private_assemblies = {
            f.stem for f in (PRIVATE_DIR / "assemblies").glob("*.py")
            if not f.name.startswith("_")
        }
    # Both import forms, because only one of them was matched here and the
    # other is the one `castle_base` actually used:
    #
    #     import assemblies.castle_ground          -> "assemblies.castle_ground"
    #     from assemblies import castle_ground     -> no such substring
    #
    # The second slipped through, and the part was offered for publication with
    # an import that resolves only inside the private tree — a broken example
    # the moment somebody cloned the repo, which is the exact outcome the
    # paragraph above promises to prevent.
    used = {
        a for a in private_assemblies
        if re.search(rf"\bassemblies\.{re.escape(a)}\b", model)
        or re.search(rf"^\s*from\s+assemblies\s+import\b.*\b{re.escape(a)}\b",
                     model, re.MULTILINE)
    }
    if used:
        raise SystemExit(
            f"\n{args.name} imports {', '.join(sorted('assemblies.' + a for a in used))}, "
            f"which live in the private tree.\nPublishing it would ship an example "
            f"that cannot build. Promote the assembly first, or\ninline what this "
            f"part actually needs."
        )

    # Same rule for the part's project, and it bites harder. An assembly is
    # obviously code; a project carries a project.md full of measurements,
    # workshop standards and a slicer profile — the kind of thing nobody thinks
    # of as a document until it is published.
    pname = projectlib.read_project(src / "spec.md")
    if pname and projectlib.exists(pname):
        proj = projectlib.find(pname)
        if proj.collection == "private":
            raise SystemExit(
                f"\n{args.name} belongs to project '{pname}', which is private "
                f"({proj.dir.relative_to(ROOT)}).\nPublishing the part alone would "
                f"ship something that cannot build, and publishing the project means"
                f"\npublishing its project.md — measurements, standards, and whatever "
                f"was learned the hard way.\nPromote the project deliberately first, "
                f"or drop the part's membership."
            )

    carried = sorted(f for f in src.iterdir()
                     if f.is_file() and not f.name.startswith(".")
                     and f.name not in PUBLISH_EXCLUDE
                     and f.suffix not in IMAGE_SUFFIXES)
    # `accepted/` is a directory, so a files-only sweep silently drops it — and
    # it is the one thing here that cannot be regenerated. `model.py` is
    # disposable by design, so an example published without its accepted mesh
    # ships the recipe and not the dish. `build/` is the opposite: generated,
    # git-ignored, and never published.
    carried_dirs = [d for d in (src / "accepted",) if d.is_dir()]
    art = _artwork(src)
    photos = _root_images(src)

    _hr(f"{'refreshing' if dst.exists() else 'about to publish'} "
        f"{args.name} → examples/{args.name}")
    for f in carried:
        n = len(f.read_text(errors="replace").splitlines()) if f.suffix in (".md", ".py") else 0
        print(f"  {f.name:<16} {n or ''}{' lines' if n else ''}")
    for d in carried_dirs:
        kids = sorted(p.name for p in d.iterdir() if p.is_file())
        print(f"  {d.name + '/':<16} {len(kids)} files: {', '.join(kids)}")
    for f in photos:
        print(f"  {f.name:<16} {f.stat().st_size // 1024} kB")
    if art:
        print(f"  {'inspiration/':<16} {len(art)} files: "
              f"{', '.join(sorted(p.name for p in art))}")

    withheld = sorted(f.name for f in _all_art(src)
                      if f.suffix.lower() in PRIVATE_ART_SUFFIXES)
    print("\n\033[1mnot published\033[0m")
    print("  history.jsonl / history.md — every parameter tried, dated. The")
    print("    dates alone describe your working schedule; they stay private.")
    print("  build/ — generated.")
    if withheld:
        print(f"  {', '.join(withheld)} — editable artwork sources. The exported")
        print("    image is what a reader needs; the working file is yours.")
    print("\nDates are stripped from what does go out: print-log headings, the")
    print("accepted mesh's timestamped filename, and ACCEPTED.md's date field.")
    print("notes.md and prints.md still carry measurements and dead ends —")
    print("that is what makes a published part worth reading. Check them.")
    if not args.yes:
        print("\nre-run with --yes to confirm")
        return 1

    if dst.exists():
        shutil.rmtree(dst)      # a refresh replaces the snapshot wholesale
    dst.mkdir(parents=True)

    changes = []
    for f in carried:
        _publish_file(f, dst / f.name, changes)
    for d in carried_dirs:
        (dst / d.name).mkdir()
        for f in sorted(p for p in d.iterdir() if p.is_file()):
            _publish_file(f, dst / d.name / _undated(f.name), changes)
    for f in photos:
        shutil.copy2(f, dst / f.name)
    if art:
        (dst / "inspiration").mkdir(exist_ok=True)
        for f in art:
            shutil.copy2(f, dst / "inspiration" / f.name)

    print(f"\npublished to {dst.relative_to(ROOT)}")
    if changes:
        print(f"  scrubbed {sum(changes)} date reference(s) across "
              f"{len([c for c in changes if c])} file(s)")
    print(f"  the working copy stays at {src.relative_to(ROOT)} and keeps its "
          f"history")
    print("  re-run `cad promote` after further refinement to refresh the "
          "snapshot")
    return 0


def cmd_sweep(args) -> int:
    """Render one variant per value of a single parameter, side by side.

    The cheapest way to answer "how much is enough?" without printing five
    times. The sheet goes to build/sweep-<param>.png.
    """
    from PIL import Image
    from . import render as rnd

    lp = partlib.load(args.name)
    key, _, raw = args.assignment.partition("=")
    if not raw:
        raise SystemExit("usage: cad sweep <part> <param>=<v1>,<v2>,...")
    values = [float(v) if "." in v or v.lstrip("-").isdigit() else v
              for v in raw.split(",")]

    tiles = []
    for v in values:
        p = lp.params.replace(**{key: v})
        try:
            shape = lp.build(p)
        except Exception as exc:
            print(f"  {key}={v}: \033[31m{type(exc).__name__}: {exc}\033[0m")
            continue
        img = rnd.render(shape, rnd.STANDARD_VIEWS[0], size=args.size)
        tiles.append((f"{key}={v}", img))
        print(f"  {key}={v}: ok")

    if not tiles:
        raise SystemExit("every variant failed")
    w = args.size
    sheet = Image.new("L", (w * len(tiles), w), rnd.BG)
    for i, (label, img) in enumerate(tiles):
        sheet.paste(rnd._label(img, label), (i * w, 0))
    lp.build_dir.mkdir(parents=True, exist_ok=True)
    out = lp.build_dir / f"sweep-{key}.png"
    sheet.save(out)
    print(f"\n{out.relative_to(ROOT)}")
    if getattr(args, "open", False):
        _open(out)
    return 0


def cmd_welcome(args) -> int:
    """`./cad` with no arguments — the likeliest first keystroke after cloning.

    It used to be an argparse error listing thirteen subcommand names, which
    is the wrong answer twice over: it implies the tool is driven by typing
    commands, and it does not say what to do. This is the one place the repo
    can state its own premise to someone who has not read the README.
    """
    print("\033[1mcadforge\033[0m — designing 3D-printed parts with Claude Code.\n")
    print("You are not meant to drive this by typing commands. Start a session")
    print("with \033[1mclaude\033[0m in this directory and describe the part you want;")
    print("Claude drafts the spec, writes the model, runs the builds and reads")
    print("the checks. Your side is judgment, the printer, and words.\n")

    dirs = partlib.working_dirs()
    _show_orientation(dirs)
    rows = advise.board(dirs)
    if rows:
        d, a = rows[0]
        mark = "\033[33m!!\033[0m" if a.urgent else "  "
        print(f" {mark} \033[1m{d.name}\033[0m — {a.action}")
        if a.command:
            print(f"      {a.command}")
        if len(rows) > 1:
            print(f"      (+{len(rows) - 1} more — ./cad next)")
    print()
    print("  \033[1m./cad status\033[0m    every part, its stage, its history")
    print("  \033[1m./cad --help\033[0m    every command, to drive a step by hand")
    # Counted rather than stated: this line has been wrong twice, once at four
    # and once at five, because publishing a part does not touch this file.
    n = len([d for d in PUBLIC_DIR.iterdir()
             if d.is_dir() and (d / "model.py").is_file()]) if PUBLIC_DIR.is_dir() else 0
    print(f"  \033[1mexamples/\033[0m       {n} printed parts, and how to make your own")
    return 0


# --- wiring ----------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="cad", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    ap.set_defaults(fn=cmd_welcome)

    p = sub.add_parser("setup", help="choose your printer and material (run once)")
    p.add_argument("--printer", help="profile key, e.g. a1mini")
    p.add_argument("--material", help="profile key, e.g. pla")
    p.add_argument("--list", action="store_true", help="show the profiles and exit")
    p.set_defaults(fn=cmd_setup)

    sub.add_parser("status", help="every part and where it is in the process").set_defaults(fn=cmd_status)

    p = sub.add_parser("project", help="list projects, or show one and its parts")
    p.add_argument("name", nargs="?")
    p.set_defaults(fn=cmd_project)

    p = sub.add_parser("new", help="scaffold a new part (private by default)")
    p.add_argument("name")
    p.add_argument("--public", action="store_true",
                   help="create it in examples/ instead of parts/")
    p.add_argument("--project", default="",
                   help="declare membership of a project (a set of parts that "
                        "share an envelope, material and standards)")
    p.set_defaults(fn=cmd_new)

    p = sub.add_parser("promote", help="publish a private part into examples/")
    p.add_argument("name")
    p.add_argument("--yes", action="store_true", help="confirm; without it, dry-run")
    p.set_defaults(fn=cmd_promote)

    p = sub.add_parser("build", help="build, check, render, optionally export")
    p.add_argument("name")
    p.add_argument("--stl", action="store_true", help="export the mesh too")
    p.add_argument("--no-render", action="store_true")
    p.add_argument("--size", type=int, default=RENDER_SIZE)
    p.add_argument("--note", default="", help="why this iteration exists")
    p.add_argument("--open", action="store_true",
                   help="put the render sheet on screen when it is written. Off "
                        "by default: builds are frequent and stealing focus is "
                        "not the tool's to do")
    p.add_argument("--view", action="store_true",
                   help="also push the part to the ocp_vscode viewer, to spin "
                        "by hand. Additive: the sheet is still written.")
    p.set_defaults(fn=cmd_build)

    p = sub.add_parser("render", help="build and render only")
    p.add_argument("name")
    p.add_argument("--size", type=int, default=RENDER_SIZE)
    p.add_argument("--open", action="store_true")
    p.set_defaults(fn=cmd_render)

    p = sub.add_parser("watch", help="rebuild and re-render on save")
    p.add_argument("name")
    p.add_argument("--size", type=int, default=RENDER_SIZE)
    p.set_defaults(fn=cmd_watch)

    p = sub.add_parser("accept", help="record a verdict on an iteration")
    p.add_argument("name")
    p.add_argument("verdict", choices=sorted(history.VERDICTS))
    p.add_argument("note", nargs="?", default="")
    p.add_argument("--i", type=int, default=None, help="iteration number (default: latest)")
    p.set_defaults(fn=cmd_accept)

    p = sub.add_parser("next", help="the single next action (all parts, or one)")
    p.add_argument("name", nargs="?")
    p.set_defaults(fn=cmd_next)

    p = sub.add_parser("history", help="what has been tried and what was ruled out")
    p.add_argument("name")
    p.set_defaults(fn=cmd_history)

    p = sub.add_parser("stage", help="move a part through the design process")
    p.add_argument("name")
    p.add_argument("stage", choices=STAGE_ORDER)
    p.set_defaults(fn=cmd_stage)

    p = sub.add_parser("sweep", help="render a parameter's variants side by side")
    p.add_argument("name")
    p.add_argument("assignment", help="param=v1,v2,v3")
    p.add_argument("--size", type=int, default=420)
    p.set_defaults(fn=cmd_sweep)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
