"""Projects — parts that belong together, as distinct from parts that fit.

    assemblies/   parts that must FIT each other.
                  Two parts are really one object cut into printable pieces,
                  and the interface is the numbers along the cuts.

    projects/     parts that BELONG together.
                  Independent objects sharing an envelope, a material, a set of
                  standards and a slicer profile. Nothing mates with anything.

The distinction is not pedantry, and it was learned by getting it wrong. A set
of tea light lanterns went into `assemblies/` because that was the only grouping
mechanism that existed — but the lanterns do not fit each other at all. They are
siblings. What they share is a fixed height, a bore, "no supports, ever", and a
slicer profile, and *none* of that is an interface.

The cost of having nowhere to put it was concrete: set-level decisions ended up
scattered through whichever part happened to discover them, so the second
lantern in the set inherited the numbers and none of the knowledge.

A project is a directory::

    <collection>/projects/<name>/
        project.md    what the set is, what is settled for all of it, and why
        shared.py     the numbers every member reads.  Optional.

Membership is declared by the part, in `spec.md` front matter::

    ---
    stage: model
    project: halloween_lantern
    ---

Declared rather than inferred, for the same reason `stage` is: a part that
imports a module has not thereby joined a set, and a set you can join by
accident is one you can leave by accident.

PRIVACY
-------
A project sits in a collection exactly as a part does, and the rule is the same:
`parts/projects/` is private and git-ignored, `examples/projects/` is public.
Both merge on `sys.path` as namespace packages, so `projects.<name>.shared`
resolves wherever it lives and a private project needs no special handling.

This matters more for a project than for a part. A project carries measurements
of real objects, the standards a workshop actually works to, and a slicer
profile — the kind of thing that is genuinely private and easy to publish by
accident, because nobody thinks of a shared-constants module as a document.
`cad promote` therefore refuses to publish a part whose project is private.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .part import COLLECTIONS, PRIVATE_DIR, ROOT

DIRNAME = "projects"

# Also searched at the repo root, so a project shared by both collections has
# somewhere to live that belongs to neither.
_ROOTS = (ROOT, *COLLECTIONS)


@dataclass(frozen=True)
class Project:
    name: str
    dir: Path

    @property
    def doc(self) -> Path:
        return self.dir / "project.md"

    @property
    def shared(self) -> Path:
        return self.dir / "shared.py"

    @property
    def collection(self) -> str:
        """Where this project lives, which is a statement about publication.

        A project at the repo ROOT is public: the root tree is committed. Only
        `parts/projects/` is private, because only `/parts/` is git-ignored.
        """
        return "private" if PRIVATE_DIR in self.dir.parents else "public"

    def title(self) -> str:
        """First markdown heading in project.md, or the bare name."""
        if not self.doc.is_file():
            return self.name
        for line in self.doc.read_text(errors="replace").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return self.name

    def summary(self) -> str:
        """The first paragraph of prose under the heading — a one-line 'what'."""
        if not self.doc.is_file():
            return ""
        body, seen_heading = [], False
        for line in self.doc.read_text(errors="replace").splitlines():
            if line.startswith("# "):
                seen_heading = True
                continue
            if not seen_heading:
                continue
            if line.strip().startswith("---"):
                continue
            if not line.strip():
                if body:
                    break
                continue
            body.append(line.strip())
        return " ".join(body)


def project_dirs() -> list[Path]:
    out = []
    for root in _ROOTS:
        base = root / DIRNAME
        if not base.is_dir():
            continue
        out += sorted(
            d for d in base.iterdir()
            if d.is_dir() and not d.name.startswith((".", "_", "__"))
        )
    return out


def all_projects() -> list[Project]:
    return [Project(name=d.name, dir=d) for d in project_dirs()]


def names() -> list[str]:
    return [p.name for p in all_projects()]


def find(name: str) -> Project:
    hits = [p for p in all_projects() if p.name == name]
    if not hits:
        known = ", ".join(names()) or "(none)"
        raise SystemExit(f"no project '{name}'. known projects: {known}")
    if len(hits) > 1:
        where = " and ".join(str(h.dir.relative_to(ROOT)) for h in hits)
        raise SystemExit(
            f"project '{name}' exists in {where}. Two collections claim the same "
            f"set — reconcile them, or delete one."
        )
    return hits[0]


def exists(name: str) -> bool:
    return any(p.name == name for p in all_projects())


# --- membership ------------------------------------------------------------
_PROJECT_RE = re.compile(r"^project:\s*([A-Za-z0-9_\-]+)\s*$", re.MULTILINE)


def read_project(spec_path: Path) -> str | None:
    """Read `project:` from spec.md front matter. None means unaffiliated,
    which is a perfectly good state — most parts belong to no set."""
    if not spec_path.is_file():
        return None
    head = spec_path.read_text(errors="replace")[:800]
    m = _PROJECT_RE.search(head)
    return m.group(1) if m else None


def set_project(spec_path: Path, name: str | None) -> None:
    """Declare (or clear) a part's project in its front matter."""
    text = spec_path.read_text()
    if name is None:
        text = _PROJECT_RE.sub("", text, count=1)
    elif _PROJECT_RE.search(text):
        text = _PROJECT_RE.sub(f"project: {name}", text, count=1)
    elif text.startswith("---"):
        end = text.index("\n---", 3)
        text = text[:end] + f"\nproject: {name}" + text[end:]
    else:
        text = f"---\nproject: {name}\n---\n\n{text}"
    spec_path.write_text(text)


def members(name: str, part_dirs: list[Path]) -> list[Path]:
    """Which of `part_dirs` declare membership of this project."""
    return [d for d in part_dirs if read_project(d / "spec.md") == name]


def group(part_dirs: list[Path]) -> list[tuple[str | None, list[Path]]]:
    """Parts grouped by project, declared projects first, unaffiliated last.

    Unaffiliated parts are not an error and are not hidden — most parts belong
    to no set, and a grouping that implies otherwise would push people to invent
    projects that do not exist.
    """
    buckets: dict[str | None, list[Path]] = {}
    for d in part_dirs:
        buckets.setdefault(read_project(d / "spec.md"), []).append(d)
    named = sorted((k, v) for k, v in buckets.items() if k is not None)
    return named + ([(None, buckets[None])] if None in buckets else [])
