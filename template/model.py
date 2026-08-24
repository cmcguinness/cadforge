"""_template — geometry only.

Nothing here runs on import. `cad build _template` calls build(), then check(),
then renders and (with --stl) exports. Read spec.md before editing, and
notes.md before changing a number.
"""
from dataclasses import dataclass

from build123d import *

import printer
from cadkit import Params


@dataclass(frozen=True)
class P(Params):
    """Every number this part depends on, named once.

    Only values genuinely shared across parts belong in printer.py — and in
    practice that is machine and material facts, nothing else. A number used by
    one part stays here even if it looks general.
    """

    size: float = 20.0
    wall: float = 2.0


PARAMS = P()

# Which way to slice the cutaway render: "x", "y", "z", or None for no section.
# Pick the plane that exposes the interior feature that matters.
SECTION = "x"


def build(p: P) -> Part:
    with BuildPart() as bp:
        Box(p.size, p.size, p.size)
        offset(amount=-p.wall, openings=bp.faces().sort_by(Axis.Z)[-1])
    return bp.part


def check(part: Part, p: P) -> None:
    """Assertions that encode what was learned, so it cannot silently regress.

    Prefer a check that fails loudly over a comment that asks nicely. The best
    ones assert a *derived* fact against the theory that produced it — a shape
    built with wrong maths still renders as a plausible shape, and no generic
    check will catch it.
    """
    assert p.wall >= printer.MIN_WALL, f"wall {p.wall} below printable minimum"
    assert part.volume > 0, "empty solid"
