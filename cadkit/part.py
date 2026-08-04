"""The part contract, and where a part sits in the design process.

A part is a directory under `parts/`:

    parts/<name>/
        spec.md     what it is for and how we will know it worked
        model.py    build(p) -> Part.  Nothing runs on import.
        notes.md    why the numbers are what they are
        prints.md   what happened when it met the physical world
        build/      generated; git-ignored

`model.py` must define:

    PARAMS   an instance of a frozen dataclass subclassing Params
    build(p) -> Part          (or Compound / Solid)

and may define:

    check(part, p) -> None    part-specific assertions
    SECTION = "x" | "y" | "z" | None      which way to cut the cutaway view

The hard rule is that importing `model.py` has no side effects. No `show()`, no
file writes. Everything that acts on a part — the renderer, the exporter, the
checker, a parameter sweep, a test — calls `build()`. In the old repo every
part called `show()` at module scope, which meant nothing could import a part
without pushing it at a viewer, which is why the STL exports all sat commented
out. One function, called by everyone, dissolves that problem.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from dataclasses import asdict, dataclass, fields, is_dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --- collections -----------------------------------------------------------
# Parts live in one of two trees, and which one a part is in is a statement
# about whether it is published, not about how it is built. The harness treats
# them identically: same contract, same commands, same everything.
#
#   examples/   public. Committed to this repo. Written to be read by strangers.
#   parts/      private. Ignored by this repo and version-controlled separately
#               (see PRIVACY.md). This is where real work happens.
#
# One working directory and one venv serve both, because a separation that adds
# daily friction is one you route around. Moving a part from private to public
# is a deliberate act — `cad promote` — and it is a publishing decision, not a
# file move: notes.md and history.md carry the whole record of how a design went
# wrong, which is what makes them worth reading and what makes them worth
# checking before they go out.
#
# Both roots go on sys.path, and `assemblies/` in each is a namespace package
# (no __init__.py), so `assemblies.<name>` merges across the two. A private
# assembly interface therefore needs no import gymnastics to stay private.
PUBLIC_DIR = ROOT / "examples"
PRIVATE_DIR = ROOT / "parts"
COLLECTIONS = (PUBLIC_DIR, PRIVATE_DIR)

# Directory names inside a collection that are not parts.
_RESERVED = {"assemblies", "_template"}


def collection_of(part_dir: Path) -> str:
    return "public" if PUBLIC_DIR in part_dir.parents else "private"


def _ensure_paths() -> None:
    for p in (ROOT, *COLLECTIONS):
        s = str(p)
        if p.is_dir() and s not in sys.path:
            sys.path.insert(0, s)


# --- the design process ----------------------------------------------------
# Stages are declared, not inferred. A part advances because someone decided it
# had, and the decision is recorded in spec.md's front matter. Inferring the
# stage from which files exist would quietly call a part "reviewed" the moment
# a render was written, which is the opposite of what review means.
STAGES: dict[str, str] = {
    "spec": "Intent is being written and refined. No geometry yet.",
    "model": "Spec is settled; model.py is being built to satisfy it.",
    "review": "Model builds. Renders are being read against the acceptance criteria.",
    "print": "Review passed. STL exported; printing or printed, not yet judged.",
    "done": "Validated in the hand. Revisit only on a new requirement.",
}
STAGE_ORDER = list(STAGES)


@dataclass(frozen=True)
class Params:
    """Base for a part's parameters.

    Being a frozen dataclass buys three things at once: the numbers are named
    and typed in one place, a build cannot mutate them halfway through, and
    every mesh can be written next to the exact values that produced it. A
    dimension you cannot trace back to its inputs is a dimension you will
    re-derive by measuring a print.
    """

    def to_dict(self) -> dict:
        return asdict(self)

    def digest(self) -> str:
        """Short stable hash of the values — goes in the STL filename so a mesh
        on disk can always be traced to the numbers behind it."""
        blob = json.dumps(self.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(blob.encode()).hexdigest()[:8]

    def replace(self, **kw):
        """A variant of these params. Used by sweeps and by refinement passes."""
        import dataclasses
        return dataclasses.replace(self, **kw)

    def describe(self, indent: int = 2) -> str:
        """Human-readable dump. A nested interface (an assembly a part belongs
        to) is summarised by its digest rather than expanded — otherwise the
        part's own numbers, which are what you are usually reading, get buried
        under sixty inherited ones."""
        pad = " " * indent
        out = []
        for f in fields(self):
            v = getattr(self, f.name)
            if isinstance(v, Params):
                out.append(f"{pad}{f.name:<22} <{type(v).__name__} {v.digest()}>")
            else:
                out.append(f"{pad}{f.name:<22} {v}")
        return "\n".join(out)


# --- loading ---------------------------------------------------------------
@dataclass
class LoadedPart:
    name: str
    dir: Path
    module: object
    params: Params

    @property
    def build_dir(self) -> Path:
        return self.dir / "build"

    def build(self, params: Params | None = None):
        p = params if params is not None else self.params
        part = self.module.build(p)
        checker = getattr(self.module, "check", None)
        if checker is not None:
            checker(part, p)
        return part

    @property
    def section(self) -> str | None:
        return getattr(self.module, "SECTION", "x")

    @property
    def print_rotation(self) -> tuple[float, float, float] | None:
        """Degrees about X, Y, Z taking the part from its MODELED pose to the
        pose it is printed in, or None if the part has not declared one.

        These are routinely different and it matters twice. The overhang check
        is meaningless in the wrong pose — a pocket floor is a ceiling when the
        part is flipped — and an STL exported in the modeled pose lands on the
        plate needing manual rotation, which is a step nobody records.

        Undeclared is reported rather than assumed, because silently treating
        the modeled pose as the print pose is exactly how a bogus overhang
        warning gets ignored, and then a real one does too.
        """
        return getattr(self.module, "PRINT_ROTATION", None)

    def pieces(self, params: Params | None = None) -> dict | None:
        """Separately-printed pieces, if this part is a multi-piece design.

        A part like a gearbox builds one assembly for review but goes to the
        plate as four loose solids. `build()` still returns the assembly — that
        is what you want to look at, and it is what proves the pieces actually
        fit together — while each piece is checked and exported on its own.
        Checking the assembly's bounding box against the bed would be nonsense,
        and exporting it as one mesh would fuse parts that must stay loose.
        """
        fn = getattr(self.module, "pieces", None)
        if fn is None:
            return None
        return fn(params if params is not None else self.params)

    def oriented(self, part):
        """The part as it sits on the build plate, dropped to z=0."""
        rot = self.print_rotation
        if rot is None:
            return part
        from build123d import Axis, Location, Vector

        out = part
        for axis, ang in zip((Axis.X, Axis.Y, Axis.Z), rot):
            if ang:
                out = out.rotate(axis, ang)
        bb = out.bounding_box()
        return Location(Vector(0, 0, -bb.min.Z)) * out

    @property
    def spec_path(self) -> Path:
        return self.dir / "spec.md"

    def stage(self) -> str:
        return read_stage(self.spec_path)


def part_dirs() -> list[Path]:
    """Every part directory, across both collections, public first."""
    out = []
    for root in COLLECTIONS:
        if not root.is_dir():
            continue
        out += sorted(
            d for d in root.iterdir()
            if d.is_dir() and d.name not in _RESERVED
            and not d.name.startswith((".", "_")) and (d / "model.py").is_file()
        )
    return out


def part_names() -> list[str]:
    return [d.name for d in part_dirs()]


def find(name: str) -> Path:
    """Locate a part by name. A name in both collections is an error rather
    than a precedence rule: it means a promoted part and its private original
    have diverged, and silently picking one would hide that."""
    hits = [d for d in part_dirs() if d.name == name]
    if not hits:
        known = ", ".join(part_names()) or "(none)"
        raise SystemExit(f"no part '{name}'. known parts: {known}")
    if len(hits) > 1:
        where = " and ".join(str(h.relative_to(ROOT)) for h in hits)
        raise SystemExit(
            f"'{name}' exists in {where}. A promoted part and its private "
            f"original have diverged — reconcile them, or delete one."
        )
    return hits[0]


def load(name: str) -> LoadedPart:
    d = find(name)
    model = d / "model.py"

    # Import under a unique module name so two parts can define the same symbol
    # without colliding, and so a rebuild in a watch loop re-executes the file.
    modname = f"_cadforge_part_{name}"
    sys.modules.pop(modname, None)
    spec = importlib.util.spec_from_file_location(modname, model)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    _ensure_paths()
    spec.loader.exec_module(mod)

    if not hasattr(mod, "build"):
        raise SystemExit(f"{model} defines no build(p) function — see cadkit/part.py")
    params = getattr(mod, "PARAMS", None)
    if params is None or not is_dataclass(params):
        raise SystemExit(f"{model} defines no PARAMS dataclass instance — see cadkit/part.py")

    return LoadedPart(name=name, dir=d, module=mod, params=params)


# --- spec front matter -----------------------------------------------------
_STAGE_RE = re.compile(r"^stage:\s*([a-z]+)\s*$", re.MULTILINE)


def read_stage(spec_path: Path) -> str:
    """Read `stage:` from spec.md's front matter. Unknown or missing reads as
    'spec' — a part with no declared stage has not started."""
    if not spec_path.is_file():
        return "spec"
    head = spec_path.read_text(errors="replace")[:800]
    m = _STAGE_RE.search(head)
    if m and m.group(1) in STAGES:
        return m.group(1)
    return "spec"


def set_stage(spec_path: Path, stage: str) -> None:
    if stage not in STAGES:
        raise SystemExit(f"unknown stage '{stage}'. one of: {', '.join(STAGES)}")
    text = spec_path.read_text()
    if _STAGE_RE.search(text):
        text = _STAGE_RE.sub(f"stage: {stage}", text, count=1)
    else:
        text = f"---\nstage: {stage}\n---\n\n{text}"
    spec_path.write_text(text)


def acceptance_criteria(spec_path: Path) -> list[str]:
    """Pull the checklist items out of the spec's Acceptance section.

    These are what a visual review is read *against*. Reviewing renders without
    them degrades into "looks fine to me", which is how a part gets printed
    with the right shape and the wrong purpose.
    """
    if not spec_path.is_file():
        return []
    lines = spec_path.read_text(errors="replace").splitlines()
    out, inside = [], False
    for line in lines:
        if re.match(r"^#{1,4}\s", line):
            inside = "acceptance" in line.lower()
            continue
        if inside:
            m = re.match(r"^\s*[-*]\s*\[.\]\s*(.+)$", line)
            if m:
                out.append(m.group(1).strip())
    return out
