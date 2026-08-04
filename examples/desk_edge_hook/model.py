r"""desk_edge_hook — a spring clip that grips a desk edge, with a prong to hang
things from.

This is the worked example for the repo's method. It is small enough to read in
one sitting and real enough to have a genuine trap in it (see notes.md — the
print orientation is load-bearing and the intuitive choice snaps).

Profile, looking along the width; the desk slides in from the right:

        spine
         |<-------- throat -------->|
       __v__________________________
      |                             |   <- upper arm  (the spring)
      |     ____________________....|
      |    |   mouth = desk_t - grip
      |    |________________________
      |                             |   <- lower arm
      |_____________________     ___|
                            |   |
                            |   |       <- prong, hangs below
                            |___|

The whole part is one closed profile extruded along its width, which is why it
prints without a single overhang and why the orientation question below has a
clean answer.
"""
from dataclasses import dataclass
from types import SimpleNamespace

from build123d import *

import printer
from cadkit import Params


@dataclass(frozen=True)
class P(Params):
    # --- the thing it clips to ---------------------------------------------
    desk_t: float = 25.0     # MEASURED. Everything else is sized around it, so
                             # a nominal here would poison the whole part.

    # --- the grip ----------------------------------------------------------
    grip: float = 0.8        # interference: the mouth is this much narrower than
                             # the desk, and the arms spread by it when fitted.
                             # This is what actually holds it on.
    arm_t: float = 3.2       # spring arm thickness
    throat: float = 28.0     # how far the arms reach onto the desk. This is the
                             # compliance knob, NOT arm_t — see notes.md.
    spine_t: float = 5.0     # the back, which does not flex

    # --- the hook ----------------------------------------------------------
    prong_drop: float = 22.0
    prong_t: float = 5.0

    width: float = 16.0      # along the desk edge
    fillet_r: float = 2.0    # every corner; the mouth roots are stress risers


PARAMS = P()
SECTION = None      # a prism has nothing a section would reveal

# The load-bearing decision, and the reason this example exists.
#
# The profile is modeled in XZ and extruded along Y. Printed as modeled — the
# clip standing up the way it hangs on the desk — the layers stack along Z, and
# the tensile stress at the mouth root runs straight ACROSS them. The arm
# delaminates at its root the first time the clip is opened.
#
# Rotating -90 deg about X lays the profile flat on the bed and puts the width
# along the printer's Z. Now every layer is a complete copy of the profile, the
# bending stress runs WITHIN a layer, and there is not one overhang anywhere.
#
# This is invisible in the geometry: both orientations slice, print, and look
# identical. See notes.md.
PRINT_ROTATION = (-90, 0, 0)


def geometry(p: P) -> SimpleNamespace:
    mouth = p.desk_t - p.grip          # the relaxed gap, narrower than the desk
    return SimpleNamespace(
        mouth=mouth,
        height=mouth + 2 * p.arm_t,    # overall, back face
        arm_reach=p.throat - p.spine_t,  # the part of the arm that actually bends
    )


def build(p: P) -> Part:
    g = geometry(p)
    h = g.height

    # One closed profile, traced anticlockwise from the bottom of the spine.
    # Written as a point list rather than a chain of primitives because the
    # shape IS its corners — every interesting dimension is a coordinate here.
    pts = [
        (0.0, 0.0),                        # spine, bottom back
        (0.0, h),                          # spine, top back
        (p.throat, h),                     # upper arm, front top
        (p.throat, h - p.arm_t),           # upper arm, front bottom  ─┐
        (p.spine_t, h - p.arm_t),          # mouth, inner top          │ the mouth
        (p.spine_t, p.arm_t),              # mouth, inner bottom       │
        (p.throat, p.arm_t),               # lower arm, front top     ─┘
        (p.throat, -p.prong_drop),         # prong, front bottom
        (p.throat - p.prong_t, -p.prong_drop),
        (p.throat - p.prong_t, 0.0),       # prong root
    ]

    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Polyline(*pts, close=True)
            make_face()
        # both=True extrudes each way, so the amount is HALF the width.
        # Centring the prism on the profile plane keeps the origin in the
        # middle of the part, which is what the width assertion checks.
        extrude(amount=p.width / 2, both=True)

        # Only the three INTERNAL corners are rounded, and only these three
        # need to be: two mouth roots, where the arm bends and where a sharp
        # corner would start the crack, plus the prong root, which carries
        # everything hung on it.
        #
        # Rounding every corner instead is the obvious move and it does not
        # work: the arm tip's two vertices are arm_t apart, so two fillets of
        # radius r need 2r < arm_t and the operation simply fails. Filleting
        # after the extrude, by selecting edges, also makes the choice explicit
        # rather than sweeping in whatever the sketch happened to contain.
        roots = [
            (p.spine_t, h - p.arm_t),          # upper mouth root
            (p.spine_t, p.arm_t),              # lower mouth root
            (p.throat - p.prong_t, 0.0),       # prong root
        ]
        corners = [
            e for e in bp.edges().filter_by(Axis.Y)
            if any(abs(e.center().X - x) < 1e-6 and abs(e.center().Z - z) < 1e-6
                   for x, z in roots)
        ]
        assert len(corners) == len(roots), (
            f"expected {len(roots)} internal corner edges, selected {len(corners)}; "
            f"the profile changed shape"
        )
        fillet(corners, p.fillet_r)

    return bp.part


def check(part: Part, p: P) -> None:
    g = geometry(p)

    # The grip must exist, and must be small. A printed PLA arm has very little
    # elastic range: ask it to spread several millimetres and it yields or
    # cracks instead of springing back, and the clip is loose forever after.
    assert p.grip > 0, "no interference: the clip would just fall off"
    assert p.grip <= 0.08 * p.desk_t, (
        f"grip {p.grip} is {100 * p.grip / p.desk_t:.0f}% of the desk thickness; "
        f"PLA will take a set rather than spring back. Keep it under 8%."
    )
    assert g.mouth > 0, "mouth is closed: grip exceeds the desk thickness"

    # Compliance comes from arm LENGTH, not from thinning the arm. Cantilever
    # deflection goes as L^3 and only as 1/t^3, so doubling the reach buys eight
    # times the give, while halving the thickness buys the same eight times at
    # the cost of all the strength. A short arm does not flex — it splits.
    assert g.arm_reach >= 4 * p.arm_t, (
        f"arm reach {g.arm_reach:.1f} mm is under 4x its thickness {p.arm_t}; "
        f"it will crack at the root instead of springing. Increase `throat`."
    )

    assert p.arm_t >= printer.MIN_WALL, (
        f"arm_t {p.arm_t} is below the printable minimum {printer.MIN_WALL}"
    )

    # The three filleted corners are internal, so the fillet ADDS material into
    # the corner rather than eating the feature. What it must not do is run past
    # the end of either edge it blends.
    assert p.fillet_r < min(g.mouth, g.arm_reach) / 2, (
        f"fillet_r {p.fillet_r} runs past the mouth or the arm it blends"
    )
    assert p.fillet_r < p.prong_drop / 2, "fillet_r runs past the prong"

    assert len(part.solids()) == 1, f"{len(part.solids())} disjoint solids"

    bb = part.bounding_box()
    assert abs(bb.size.Y - p.width) < 1e-6, (
        f"width came out {bb.size.Y:.2f}, expected {p.width}"
    )
