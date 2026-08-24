r"""ghost_lantern — a ring of ghosts cut through a black cylinder.

The motif is a **cutout**: the black of the reference artwork becomes the hole,
and the ghost is the light coming through it. Same construction as
`witch_lantern`; only the outline differs.

**This part is printed WITH supports, and that is a deliberate decision.**

The ghost has raised arms, so its top profile has two peaks with a valley
between each arm and the head. A valley is a downward-hanging wedge of panel
whose lowest point begins in mid-air — an island. There are 38 of them, widest
3.8 mm, and they are structural to the pose rather than a defect: "raised arms"
and "no downward-hanging material" cannot both hold. Filling them would merge
the arms into the head and destroy the silhouette.

The set has established that supports come off cleanly from robust features —
what killed `raven_lantern`'s lettering was 0.5 mm webs, not supports. A ghost's
arm is millimetres thick. So `cad build` will report the islands, and the answer
here is "yes, known, print it with supports" rather than a reshape.

See ARTWORK.md ("One peak, or accept supports") and the project's project.md.

Body, height, bore and the datum the motif hangs from belong to the
`halloween_lantern` project and are not this file's to choose.
"""
from dataclasses import dataclass
from math import asin, degrees, pi
from types import SimpleNamespace

from build123d import *

import printer
from cadkit import Params
from projects.halloween_lantern import shared as body

from ghost_openings import OPENINGS


@dataclass(frozen=True)
class P(Params):
    n_ghosts: int = 4
    """Four, not five.

    The other motifs in the set are tall and narrow, so five of them leaves a
    comfortable rib. This window is nearly square — 18.7 mm wide against 19 mm
    tall — so at the same count the ribs get visually thin and the lantern
    starts reading as a row of windows rather than as a dark object with
    windows in it. Four restores the solid between them.

    It also cuts a fifth of the long nozzle jumps per layer, which is where
    `raven_lantern`'s stringing came from — the count is a printability
    parameter as much as a compositional one."""

    ghost_h: float = 0.0
    """0 means 'as tall as the lit wall allows', which is the sensible default:
    the lit wall IS the canvas and there is no reason to give any of it back.
    Set a number to shrink it deliberately."""

    min_rib_frac: float = 2 / 3
    """Solid between adjacent motifs, as a **fraction of the motif's width** —
    not millimetres.

    A fixed millimetre floor means different things on a 17 mm motif and a 40 mm
    one, so it cannot be the rule. What the eye judges is the ratio: how much
    black there is between two windows against how wide a window is.

    **Two thirds is a rule of thumb bracketed by one accept and one reject**,
    which is the only honest way to set a taste threshold. Judged at true scale
    on this part:

    | count | rib | as fraction of width | verdict |
    |---|---|---|---|
    | 4 | 14.37 mm | **0.767** | good |
    | 5 | 7.62 mm | **0.406** | too little |

    So the answer lies somewhere between 0.41 and 0.77 and nothing narrows it
    further yet. The midpoint is 0.586; **2/3 is the memorable number nearest
    it**, and it errs toward the side that was actually approved rather than the
    side that was rejected, which is the right way to be wrong about a threshold
    nobody has measured.

    A rule of thumb has to be *remembered* to get applied, and "two thirds"
    survives being quoted where 0.586 does not. Replace it with a measurement
    when one exists — this is a placeholder with its evidence attached, not a
    finding.

    **The right value depends on how fully the motif fills its bounding box**,
    which is why this lives in the part rather than the project — for now:

    | part | motif | rib / width | verdict |
    |---|---|---|---|
    | `raven_lantern` | bird, mostly empty box | 0.25 | reads fine |
    | `witch_lantern` | head, fairly full box | 0.64 | reads fine |
    | `ghost_lantern` | window, fills its box | 2/3 floor | this part |

    A sparse silhouette leaves black inside its own bounding box, so the true
    gap between two of them is far larger than the rib figure suggests. A window
    that fills its box has no such slack, and the rib figure IS the gap. The
    raven passing at 0.25 is not a contradiction — it is the same rule measured
    on a shape that carries its own spacing.

    A better metric would measure the actual closest approach between adjacent
    motifs rather than between their bounding boxes, and would then support one
    set-wide number. Worth doing when a fourth motif makes it pay.
    """

    open_frac_min: float = 0.04
    open_frac_max: float = 0.28
    """Fractions of the WHOLE outer wall, matching raven_lantern. Measuring
    against the motif band instead makes the number move when the layout
    changes rather than when the design does."""

    chamfer_top: float = 0.8
    chamfer_bottom: float = 0.6


PARAMS = P()

# Cut across Y so the section passes through a ghost, which is where the wall
# thickness around an opening actually shows.
SECTION = "y"

# Upright on its base, as modelled. Every opening is in a vertical wall and
# bridges across its own top the way a circular hole does. The project forbids
# supports outright; its project.md records what that cost to learn.
PRINT_ROTATION = (0, 0, 0)


def geometry(p: P) -> SimpleNamespace:
    """Everything derived, in one place, read by both build() and check()."""
    e, puck = body.ENVELOPE, body.PUCK
    inner_r, outer_r = body.inner_r(), body.outer_r()
    lit_lo, lit_hi = body.lit_window()
    top = body.motif_top()
    opaque_top = e.floor_t + puck.opaque_h

    ghost_h = p.ghost_h or (top - opaque_top)

    return SimpleNamespace(
        inner_r=inner_r,
        outer_r=outer_r,
        floor_t=e.floor_t,
        opaque_top=opaque_top,
        lit_lo=lit_lo,
        lit_hi=lit_hi,
        ghost_h=ghost_h,
        ghost_w=ghost_h * max(abs(x) for poly in OPENINGS for x, _ in poly) * 2,
        band_hi=top,
        band_lo=top - ghost_h,
        holder_h=e.height,
        angles=[i * 360.0 / p.n_ghosts for i in range(p.n_ghosts)],
    )


def _opening_faces(height: float) -> list[Sketch]:
    """The traced holes, scaled to a motif of this height, sitting on y=0.

    Stored normalised to height 1.0 and centred in x, so scaling is all that
    happens here and `ghost_h` stays the single size knob.
    """
    out = []
    for poly in OPENINGS:
        with BuildSketch() as sk:
            with BuildLine():
                Polyline(*[(x * height, y * height) for x, y in poly], close=True)
            make_face()
        out.append(sk.sketch)
    return out


def _radial_cutter(face: Sketch, z: float, angle_deg: float, g) -> Part:
    """Punch `face` through ONE wall, square to the wall at `angle_deg`.

    Extruded a single direction only. The ghost is not left-right symmetric,
    so a bidirectional extrude — exact for a symmetric heart — would stamp a
    mirrored ghost onto the far wall.
    """
    with BuildPart() as cutter:
        with BuildSketch(Plane.XZ):
            with Locations((0, z)):
                add(face)
        extrude(amount=g.outer_r + 1.0)
    return cutter.part.rotate(Axis.Z, angle_deg)


def build(p: P) -> Part:
    g = geometry(p)
    faces = _opening_faces(g.ghost_h)

    with BuildPart() as bp:
        Cylinder(g.outer_r, g.holder_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, g.floor_t)):
            Cylinder(g.inner_r, g.holder_h - g.floor_t,
                     align=(Align.CENTER, Align.CENTER, Align.MIN),
                     mode=Mode.SUBTRACT)

        # Chamfer while the shell is still a plain tube. Every opening reaches
        # the outer surface and splits the cylindrical face, splitting the rim
        # circle with it, and a split rim cannot be selected whole.
        chamfer(bp.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[-1], p.chamfer_top)
        chamfer(bp.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[0], p.chamfer_bottom)

        for angle in g.angles:
            for face in faces:
                add(_radial_cutter(face, g.band_lo, angle, g), mode=Mode.SUBTRACT)

    return bp.part


def check(part: Part, p: P) -> None:
    g = geometry(p)
    faces = _opening_faces(g.ghost_h)
    bb = faces[0].bounding_box()

    assert len(part.solids()) == 1, (
        f"the part is {len(part.solids())} separate solids, not one"
    )

    # --- the load-bearing one ----------------------------------------------
    assert g.band_lo >= g.opaque_top - 1e-9, (
        f"the motif hangs from z={g.band_hi:.1f} down to z={g.band_lo:.1f}, but "
        f"the puck is opaque up to z={g.opaque_top:.1f}, so the bottom of every "
        f"ghost would stay dark. {g.band_hi - g.opaque_top:.1f} mm of lit wall is "
        f"available and the motif wants {g.ghost_h:.1f} mm. Shrink ghost_h, or "
        f"raise the project's height for the WHOLE SET."
    )

    # --- the outline is still the outline ----------------------------------
    # A silhouette built from a mangled outline is still a closed shape and
    # still renders as *something*. The stored aspect ratio is what notices.
    # Every opening must sit inside the motif's own footprint. The trace
    # normalises to height 1.0 sitting on y=0, so a point outside that says the
    # artwork or the normalisation moved and a cut would run into the rib.
    lo = min(y for poly in OPENINGS for _, y in poly)
    hi = max(y for poly in OPENINGS for _, y in poly)
    assert -0.001 <= lo and hi <= 1.001, (
        f"an opening spans y={lo:.3f}..{hi:.3f}; expected 0..1. "
        f"Re-run trace_ghost.py."
    )

    width = max(abs(x) for poly in OPENINGS for x, _ in poly) * 2 * g.ghost_h
    assert width / 2 < g.inner_r, (
        f"motif is {width:.1f} mm wide but the cavity is only "
        f"{2 * g.inner_r:.1f} mm across; reduce ghost_h"
    )

    # NOTE: there is deliberately no assertion on the outline's narrowest
    # feature. Every tapered point — the hat tip, the hair tendrils — has
    # vanishing local width, so any percentile of feature width is dominated by
    # tapers and says nothing about printability. The honest measure is to
    # simulate the nozzle against the artwork, which trace_ghost.py reports and
    # notes.md records: 98.4% of the area survives at this size, in one piece.

    # --- ribs ---------------------------------------------------------------
    # Arc on the OUTER surface, where the material is thinnest and shows.
    arc = 2 * degrees(asin(min(g.ghost_w, 1.98 * g.outer_r) / 2 / g.outer_r))
    rib = (360.0 / p.n_ghosts - arc) / 360 * 2 * pi * g.outer_r
    ratio = rib / g.ghost_w
    assert ratio >= p.min_rib_frac, (
        f"only {rib:.2f} mm of wall between ghosts — {ratio:.0%} of the "
        f"{g.ghost_w:.1f} mm motif width, under the {p.min_rib_frac:.0%} floor. "
        f"The lantern would read as a band of windows rather than a dark object "
        f"with windows in it. Reduce n_ghosts or ghost_h."
    )

    # --- lantern, not colander ---------------------------------------------
    frac = p.n_ghosts * sum(f.area for fc in faces for f in fc.faces()) / (2 * pi * g.outer_r * g.holder_h)
    assert p.open_frac_min <= frac <= p.open_frac_max, (
        f"{frac:.0%} of the outer wall is open (want {p.open_frac_min:.0%}–"
        f"{p.open_frac_max:.0%}); "
        + ("too little to light it"
           if frac < p.open_frac_min else "it stops reading as a black object")
    )

    # --- the puck can still be got out -------------------------------------
    recess = g.holder_h - (g.floor_t + body.PUCK.flame_top)
    assert recess <= 15.0, (
        f"the flame tip is {recess:.1f} mm down inside the rim; at that depth "
        f"you are fishing for it rather than pinching it"
    )
