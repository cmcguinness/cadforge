"""`cad` — one command per step of the design process.

    cad new <name>              scaffold a part at the spec stage
    cad status                  every part, its stage, its history
    cad build <name>            build → assert → check → render → (optionally) export
    cad watch <name>            rebuild on save
    cad accept <name>           record a verdict on the current iteration
    cad history <name>          what has been tried, and what was ruled out
    cad stage <name> <stage>    advance (or rewind) the design process
    cad sweep <name> k=a,b,c    render a variant per value, side by side

`build` is the workhorse and does the whole inner loop in one shot, because a
review step that requires three commands is a review step that gets skipped.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import check as checks
from . import history, part as partlib
from .part import (COLLECTIONS, PRIVATE_DIR, PUBLIC_DIR, ROOT, STAGES,
                   STAGE_ORDER, collection_of, find)


def _hr(title: str = "") -> None:
    print(f"\n\033[1m{title}\033[0m" if title else "")


def _fmt_stage(stage: str) -> str:
    i = STAGE_ORDER.index(stage) if stage in STAGE_ORDER else 0
    return f"[{i + 1}/{len(STAGE_ORDER)} {stage}]"


# --- commands --------------------------------------------------------------
def cmd_status(args) -> int:
    dirs = partlib.part_dirs()
    if not dirs:
        print("no parts yet — `cad new <name>`")
        return 0
    width = max(len(d.name) for d in dirs)
    print(f"{'part'.ljust(width)}  where    stage      iterations")
    print("-" * (width + 48))
    for d in dirs:
        stage = partlib.read_stage(d / "spec.md")
        print(f"{d.name.ljust(width)}  {collection_of(d):<7}  {stage:<9}  {history.summary(d)}")
    print()
    for s in STAGE_ORDER:
        print(f"  {s:<7} {STAGES[s]}")
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
    entry, revisits = history.record(lp.dir, lp.params, note=args.note or "")
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
        print(f"  \033[1m{written[0].relative_to(ROOT)}\033[0m   <- open this one")

    # --- params provenance -------------------------------------------------
    lp.build_dir.mkdir(parents=True, exist_ok=True)
    import json
    (lp.build_dir / "params.json").write_text(
        json.dumps({"part": lp.name, "digest": lp.params.digest(),
                    "params": lp.params.to_dict()}, indent=2, default=str) + "\n")

    # --- export ------------------------------------------------------------
    if args.stl:
        if verdict is checks.Severity.FAIL:
            print("\n\033[31mnot exporting: a check FAILed\033[0m")
            return 1
        from build123d import export_stl
        # Exported in the print pose, so the mesh drops onto the plate ready to
        # slice. A rotation done by hand in the slicer is a step nobody records.
        if pieces:
            for pname, pshape in pieces.items():
                out = lp.build_dir / f"{lp.name}-{pname}-{lp.params.digest()}.stl"
                export_stl(pshape, str(out))
                print(f"\nexported {out.relative_to(ROOT)}")
        else:
            stl = lp.build_dir / f"{lp.name}-{lp.params.digest()}.stl"
            export_stl(plated, str(stl))
            print(f"\nexported {stl.relative_to(ROOT)}")
        print("  slice it in Bambu Studio — see CLAUDE.md; there is no CLI path.")

    # --- what the reviewer is supposed to be checking ----------------------
    criteria = partlib.acceptance_criteria(lp.spec_path)
    if criteria and not args.no_render:
        _hr("acceptance criteria — read the renders against these")
        for c in criteria:
            print(f"  [ ] {c}")

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
                    size=args.size, note=""))
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


def cmd_accept(args) -> int:
    d = find(args.name)
    if not d.is_dir():
        raise SystemExit(f"no such part: {args.name}")
    e = history.set_verdict(d, args.verdict, note=args.note or "", i=args.i)
    print(f"iteration #{e.i} → {e.verdict}" + (f" — {e.note}" if e.note else ""))
    print(f"updated {(d / 'history.md').relative_to(ROOT)}")
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
    print(f"created {d.relative_to(ROOT)}")
    print("\nnext: write spec.md — purpose, constraints, and acceptance criteria.")
    print("      the spec is the durable input; model.py is what gets rewritten.")
    return 0


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

    src = find(args.name)
    if collection_of(src) == "public":
        raise SystemExit(f"{args.name} is already in examples/")
    dst = PUBLIC_DIR / args.name
    if dst.exists():
        raise SystemExit(f"{dst.relative_to(ROOT)} already exists")

    # Refuse to publish a part that imports something that stays private.
    model = (src / "model.py").read_text()
    private_assemblies = set()
    if (PRIVATE_DIR / "assemblies").is_dir():
        private_assemblies = {
            f.stem for f in (PRIVATE_DIR / "assemblies").glob("*.py")
            if not f.name.startswith("_")
        }
    used = {a for a in private_assemblies if f"assemblies.{a}" in model}
    if used:
        raise SystemExit(
            f"\n{args.name} imports {', '.join(sorted('assemblies.' + a for a in used))}, "
            f"which live in the private tree.\nPublishing it would ship an example "
            f"that cannot build. Promote the assembly first, or\ninline what this "
            f"part actually needs."
        )

    carried = sorted(f for f in src.iterdir()
                     if f.is_file() and not f.name.startswith("."))
    _hr(f"about to publish {args.name} → examples/{args.name}")
    for f in carried:
        n = len(f.read_text(errors="replace").splitlines()) if f.suffix in (".md", ".py") else 0
        print(f"  {f.name:<16} {n or ''}{' lines' if n else ''}")
    print("\nThese become public. notes.md and history.md record how the design")
    print("went wrong, including any measurements and asides. Read them first.")
    if not args.yes:
        print("\nre-run with --yes to confirm")
        return 1

    dst.mkdir(parents=True)
    for f in carried:
        shutil.copy2(f, dst / f.name)
    print(f"\npublished to {dst.relative_to(ROOT)}")
    print(f"the private original is untouched at {src.relative_to(ROOT)} —")
    print("delete it once you are happy, or the two will diverge (`cad status` "
          "will refuse a duplicate name).")
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
    return 0


# --- wiring ----------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="cad", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="every part and where it is in the process").set_defaults(fn=cmd_status)

    p = sub.add_parser("new", help="scaffold a new part (private by default)")
    p.add_argument("name")
    p.add_argument("--public", action="store_true",
                   help="create it in examples/ instead of parts/")
    p.set_defaults(fn=cmd_new)

    p = sub.add_parser("promote", help="publish a private part into examples/")
    p.add_argument("name")
    p.add_argument("--yes", action="store_true", help="confirm; without it, dry-run")
    p.set_defaults(fn=cmd_promote)

    p = sub.add_parser("build", help="build, check, render, optionally export")
    p.add_argument("name")
    p.add_argument("--stl", action="store_true", help="export the mesh too")
    p.add_argument("--no-render", action="store_true")
    p.add_argument("--size", type=int, default=520)
    p.add_argument("--note", default="", help="why this iteration exists")
    p.set_defaults(fn=cmd_build)

    p = sub.add_parser("render", help="build and render only")
    p.add_argument("name")
    p.add_argument("--size", type=int, default=520)
    p.set_defaults(fn=cmd_render)

    p = sub.add_parser("watch", help="rebuild and re-render on save")
    p.add_argument("name")
    p.add_argument("--size", type=int, default=520)
    p.set_defaults(fn=cmd_watch)

    p = sub.add_parser("accept", help="record a verdict on an iteration")
    p.add_argument("name")
    p.add_argument("verdict", choices=sorted(history.VERDICTS))
    p.add_argument("note", nargs="?", default="")
    p.add_argument("--i", type=int, default=None, help="iteration number (default: latest)")
    p.set_defaults(fn=cmd_accept)

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
