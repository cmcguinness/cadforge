r"""witch_lantern — a ring of witch heads cut through a black cylinder.

    top rim ----  _________________
                 |   /\      /\    |   witch heads in profile, pierced right
    lit window   |  (  )    (  )   |   through the wall
                 |_________________|
                 |                 |   blank wall: the paper liner wraps here
    floor -------|_________________|

The motif is a **cutout**: the black of the reference artwork becomes the hole,
and the witch is the light coming through it.

This is the second motif tried for this part. The first put a flying witch
inside a moon as retained material, and it was abandoned because her legibility
depended on interior gaps — arm from body, hand from broom — that measured
0.4–0.8 mm at the size the set allows. A head in profile has no such problem:
hat, brim, nose, chin and hair are all *boundary*, so **98.4% of its area
survives a 0.4 mm nozzle at 19 mm tall with no simplification at all**. See
notes.md, and ARTWORK.md for the general rule.

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

from head_outline import OUTLINE, WIDTH_PER_HEIGHT


@dataclass(frozen=True)
class P(Params):
    n_heads: int = 5
    """Five. The geometry allows about seven before the ribs between heads fall
    under the minimum, and fewer is better for a reason that is not visual:
    every opening is a gap the nozzle must jump on each layer of the band, and
    that is where `raven_lantern`'s stringing came from. Five is a ring without
    being a colander."""

    head_h: float = 0.0
    """0 means 'as tall as the lit wall allows', which is the sensible default:
    the lit wall IS the canvas and there is no reason to give any of it back.
    Set a number to shrink it deliberately."""

    min_rib: float = 3.0

    open_frac_min: float = 0.04
    open_frac_max: float = 0.28
    """Fractions of the WHOLE outer wall, matching raven_lantern. Measuring
    against the motif band instead makes the number move when the layout
    changes rather than when the design does."""

    chamfer_top: float = 0.8
    chamfer_bottom: float = 0.6


PARAMS = P()

# Cut across Y so the section passes through a head, which is where the wall
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

    head_h = p.head_h or (top - opaque_top)

    return SimpleNamespace(
        inner_r=inner_r,
        outer_r=outer_r,
        floor_t=e.floor_t,
        opaque_top=opaque_top,
        lit_lo=lit_lo,
        lit_hi=lit_hi,
        head_h=head_h,
        head_w=head_h * WIDTH_PER_HEIGHT,
        band_hi=top,
        band_lo=top - head_h,
        holder_h=e.height,
        angles=[i * 360.0 / p.n_heads for i in range(p.n_heads)],
    )


def _head_face(height: float) -> Sketch:
    """The silhouette, scaled so its height is `height`, sitting on y=0.

    The outline is stored normalised to height 1.0 and centred in x, so scaling
    is the only thing that happens here — `head_h` stays the single size knob
    and editing a point changes the shape but never the size.
    """
    with BuildSketch() as sk:
        with BuildLine():
            Polyline(*[(x * height, y * height) for x, y in OUTLINE], close=True)
        make_face()
    bb = sk.sketch.bounding_box()
    return sk.sketch.translate((-bb.center().X, -bb.min.Y, 0))


def _radial_cutter(face: Sketch, z: float, angle_deg: float, g) -> Part:
    """Punch `face` through ONE wall, square to the wall at `angle_deg`.

    Extruded a single direction only. A head in profile is handed, so a
    bidirectional extrude — which is exact for a symmetric heart — would stamp
    a mirrored witch facing the other way onto the far wall.
    """
    with BuildPart() as cutter:
        with BuildSketch(Plane.XZ):
            with Locations((0, z)):
                add(face)
        extrude(amount=g.outer_r + 1.0)
    return cutter.part.rotate(Axis.Z, angle_deg)


def build(p: P) -> Part:
    g = geometry(p)
    head = _head_face(g.head_h)

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
            add(_radial_cutter(head, g.band_lo, angle, g), mode=Mode.SUBTRACT)

    return bp.part


def check(part: Part, p: P) -> None:
    g = geometry(p)
    head = _head_face(g.head_h)
    bb = head.bounding_box()

    assert len(part.solids()) == 1, (
        f"the part is {len(part.solids())} separate solids, not one"
    )

    # --- the load-bearing one ----------------------------------------------
    assert g.band_lo >= g.opaque_top - 1e-9, (
        f"the motif hangs from z={g.band_hi:.1f} down to z={g.band_lo:.1f}, but "
        f"the puck is opaque up to z={g.opaque_top:.1f}, so the bottom of every "
        f"head would stay dark. {g.band_hi - g.opaque_top:.1f} mm of lit wall is "
        f"available and the motif wants {g.head_h:.1f} mm. Shrink head_h, or "
        f"raise the project's height for the WHOLE SET."
    )

    # --- the outline is still the outline ----------------------------------
    # A silhouette built from a mangled outline is still a closed shape and
    # still renders as *something*. The stored aspect ratio is what notices.
    aspect = bb.size.X / bb.size.Y
    assert abs(aspect - WIDTH_PER_HEIGHT) < 1e-3, (
        f"silhouette is {aspect:.3f} wide-to-tall but the traced outline says "
        f"{WIDTH_PER_HEIGHT:.3f}; the outline or the scaling has been edited"
    )

    # A head wider than the cavity cannot be punched clean through: its edges
    # run past the inner wall and leave a ragged lip instead of an opening.
    assert bb.size.X / 2 < g.inner_r, (
        f"head is {bb.size.X:.1f} mm wide but the cavity is only "
        f"{2 * g.inner_r:.1f} mm across; reduce head_h"
    )

    # NOTE: there is deliberately no assertion on the outline's narrowest
    # feature. Every tapered point — the hat tip, the hair tendrils — has
    # vanishing local width, so any percentile of feature width is dominated by
    # tapers and says nothing about printability. The honest measure is to
    # simulate the nozzle against the artwork, which trace_head.py reports and
    # notes.md records: 98.4% of the area survives at this size, in one piece.

    # --- ribs ---------------------------------------------------------------
    # Arc on the OUTER surface, where the material is thinnest and shows.
    arc = 2 * degrees(asin(min(bb.size.X, 1.98 * g.outer_r) / 2 / g.outer_r))
    rib = (360.0 / p.n_heads - arc) / 360 * 2 * pi * g.outer_r
    assert rib >= p.min_rib, (
        f"only {rib:.2f} mm of wall between heads (min {p.min_rib}); "
        f"reduce n_heads or head_h"
    )

    # --- lantern, not colander ---------------------------------------------
    frac = p.n_heads * sum(f.area for f in head.faces()) / (2 * pi * g.outer_r * g.holder_h)
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
