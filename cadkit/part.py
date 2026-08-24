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
_RESERVED = {"assemblies", "projects", "_template"}


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


def working_dirs() -> list[Path]:
    """One directory per part name — the private copy where both exist.

    `part_dirs()` reports the filesystem; this reports the *parts*. Since
    promotion copies rather than moves, a published part appears in both trees,
    and a board that lists it twice is describing the storage rather than the
    work.
    """
    seen, out = set(), []
    for d in sorted(part_dirs(), key=lambda p: collection_of(p) != "private"):
        if d.name not in seen:
            seen.add(d.name)
            out.append(d)
    return sorted(out, key=lambda p: p.name)


def part_names() -> list[str]:
    return [d.name for d in part_dirs()]


def published_twin(part_dir: Path) -> Path | None:
    """The examples/ copy of a private part, if one has been published."""
    if collection_of(part_dir) != "private":
        return None
    twin = PUBLIC_DIR / part_dir.name
    return twin if (twin / "model.py").is_file() else None


def find(name: str) -> Path:
    """Locate a part by name. **The private copy wins.**

    Promotion copies rather than moves, so a published part normally exists in
    both trees and that is not an error. The private one is the working copy —
    it carries the history the published one deliberately does not, and it is
    where refinement continues. Resolving to the published snapshot would mean
    editing a thing that gets overwritten by the next `cad promote`.
    """
    hits = [d for d in part_dirs() if d.name == name]
    if not hits:
        known = ", ".join(sorted(set(part_names()))) or "(none)"
        raise SystemExit(f"no part '{name}'. known parts: {known}")
    private = [d for d in hits if collection_of(d) == "private"]
    return private[0] if private else hits[0]


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

    # The part's OWN directory goes on the path too, so a part can carry helper
    # modules beside model.py — generated data especially. `witch_lantern` keeps
    # a traced outline in `moon_openings.py`, written by a script that reads a
    # PNG; pasting several hundred coordinates into model.py would bury the
    # design, and importing the image at build time would make every build
    # depend on a file outside the repo.
    #
    # Helper modules from a DIFFERENT part are evicted first. Two parts may
    # reasonably both have a `shapes.py`, and without this the second would
    # silently get the first one's, cached from an earlier build in the same
    # process — a watch loop or a sweep would produce the wrong geometry with
    # nothing to indicate it.
    own = str(d)
    if own not in sys.path:
        sys.path.insert(0, own)
    for mname, m in list(sys.modules.items()):
        f = getattr(m, "__file__", None)
        if not f or mname.startswith("_cadforge_part_"):
            continue
        parent = Path(f).resolve().parent
        if parent != d and parent.parent in COLLECTIONS:
            del sys.modules[mname]

    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(own)

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


# --- acceptance criteria: the objective function ---------------------------
# Criteria are the only part of a spec the harness can act on, and they are
# where a spec actually constrains anything. Prose sets context; a checklist
# item is a question with an answer.
#
# They are classified by axis, because an unstated axis stays unconstrained no
# matter how detailed the rest of the spec gets. A part specified only along
# CONSTRUCTION converges tightly on a well-formed object that does not do its
# job — which is exactly what happened to this repo's first worked example.
FUNCTION = "function"          # does it do the job? — the axis that matters
CONSTRUCTION = "construction"  # is it built correctly? — cheap to state, easy to over-weight
PRINT = "print"                # only the physical object can settle it
UNCLASSIFIED = "unclassified"  # spec predates the classified sections

AXIS_ORDER = (FUNCTION, CONSTRUCTION, PRINT, UNCLASSIFIED)
AXIS_LABEL = {
    FUNCTION: "does it do its job",
    CONSTRUCTION: "is it built correctly",
    PRINT: "only a print can settle these",
    UNCLASSIFIED: "unclassified",
}


@dataclass(frozen=True)
class Criterion:
    text: str
    axis: str
    checked: bool


def _axis_for_heading(heading: str) -> str:
    h = heading.lower()
    if "print" in h or "in the hand" in h or "physical" in h:
        return PRINT
    if "job" in h or "function" in h or "for?" in h or "does it do" in h:
        return FUNCTION
    if "built" in h or "construct" in h or "correct" in h:
        return CONSTRUCTION
    return UNCLASSIFIED


def acceptance_criteria(spec_path: Path) -> list[Criterion]:
    """Every checklist item under the spec's Acceptance section, classified.

    These are what a review is read *against*. Reviewing renders without them
    degrades into "looks fine to me", which is how a part gets built with the
    right shape and the wrong purpose.
    """
    if not spec_path.is_file():
        return []
    out: list[Criterion] = []
    inside = False
    axis = UNCLASSIFIED
    for line in spec_path.read_text(errors="replace").splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level, heading = len(m.group(1)), m.group(2)
            if level <= 2:
                # A top-level heading either opens or closes the section.
                inside = "acceptance" in heading.lower()
                axis = UNCLASSIFIED
            elif inside:
                axis = _axis_for_heading(heading)
            continue
        if inside:
            c = re.match(r"^\s*[-*]\s*\[([ xX])\]\s*(.+)$", line)
            if c:
                text = c.group(2).strip()
                # The template ships placeholder bullets so the sections are
                # visible. They are scaffolding, not criteria — counting them
                # would make an untouched spec look finished.
                if text.strip("….· ") == "":
                    continue
                out.append(Criterion(text=text, axis=axis,
                                     checked=c.group(1).lower() == "x"))
    return out


def criteria_by_axis(spec_path: Path) -> dict[str, list[Criterion]]:
    grouped: dict[str, list[Criterion]] = {a: [] for a in AXIS_ORDER}
    for c in acceptance_criteria(spec_path):
        grouped[c.axis].append(c)
    return grouped


def generation(spec_path: Path) -> str:
    """A short hash of the acceptance criteria — the design's generation.

    Changing a criterion changes what "good" means, which moves the target
    rather than narrowing the search toward it. Parameters from before the
    change are answers to a different question: their verdicts no longer apply,
    and the oscillation guard must not fire on them. So iteration history is
    scoped to this value, and editing the criteria opens a new lineage.

    Prose edits don't count. Only the checklist moves the target.

    **Whitespace is normalised before hashing**, so re-wrapping a criterion is
    not a new generation. It was: reflowing every Markdown file in the repo so
    paragraphs sat on one line silently detached every part from its own
    history, because the hash saw new text where a reader would see the same
    sentence. Reformatting must never look like retargeting — the question the
    hash is trying to answer is "did what counts as success change", and a line
    break has no opinion about that.
    """
    texts = [" ".join(c.text.split()) for c in acceptance_criteria(spec_path)]
    if not texts:
        return "nocrit"
    return hashlib.sha256("\n".join(texts).encode()).hexdigest()[:8]
