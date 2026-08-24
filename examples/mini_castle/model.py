r"""mini_castle — the castle at half size, hollowed into one tall cavity.

    ______                       the two internal slabs are removed, so the
   |  /\  |   top turret         face chamber, the second storey and the top
   |______|                      turret become a single continuous void that
   |      |   bat window         one tea light stands at the bottom of.
   |  ()  |
   |______|   face: eyes
   | oo   |         + mouth
   |_||||_|

The full-size castle gives each storey its own puck. At half size no chamber
can take one — the binding constraint is **height**, not footprint: the face
chamber halves to 22.6 mm of clear height against a puck that is 30 mm tall,
while its 61.6 x 41.0 mm floor accepts the 35 mm diameter with room to spare.

Removing the two slabs merges the three chambers into 59.6 mm of clear height,
and the puck fits.

WHAT THIS PART IS NOT
---------------------
It is **not a redesign**. It is `castle` scaled, with two boxes subtracted.
`model.py` is disposable here in the strongest sense — the geometry lives next
door and this file is the transformation. If the castle changes, this follows
for free.

THE THING TO WATCH
------------------
**The puck does not scale.** A tea light is 35 mm across with a 15 mm opaque
base whatever size the castle is, so at half size that base covers 66% of the
face storey rather than 33%. The emitting band sits opposite the TOP of the
face and the BOTTOM of the bat window. Expect the eyes to light well, the mouth
to darken towards its threshold more than it does full size, and the top turret
to be ambient rather than lit.

That is a prediction, not a measurement, and it is what the first print is for.
`check()` asserts the geometry; only the object can settle the light.
"""
from dataclasses import dataclass
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

from build123d import *

from cadkit import Params
from projects.halloween_lantern.shared import PUCK


def _load_castle():
    """Import the castle's model by path.

    Parts are not packages and their directories go on `sys.path` one at a
    time, so a plain `import model` would collide with this file. The private
    working copy wins over the published snapshot, matching `cad`'s own rule:
    the snapshot is a thing that gets overwritten.
    """
    here = Path(__file__).resolve().parent
    for cand in (here.parent / "castle" / "model.py",
                 here.parents[1] / "examples" / "castle" / "model.py"):
        if cand.is_file():
            spec = importlib.util.spec_from_file_location("_castle_model", cand)
            mod = importlib.util.module_from_spec(spec)
            sys.path.insert(0, str(cand.parent))
            try:
                spec.loader.exec_module(mod)
            finally:
                sys.path.pop(0)
            return mod
    raise FileNotFoundError("castle/model.py not found in parts/ or examples/")


CASTLE = _load_castle()


@dataclass(frozen=True)
class P(Params):
    scale: float = 0.5
    """Half size. 68 x 46 x 89 mm, about two hours against eleven."""

    floors: bool = False
    """Keep the internal slabs. False is the whole point of this part; True
    builds a plain scaled castle, which is what the first 50% test print was
    and which no puck fits."""

    slack: float = 1.0
    """Extra cut beyond each slab's nominal z range, so a slab is removed
    cleanly rather than leaving a wafer behind. Cuts into the void above and
    below, never sideways into a wall."""


PARAMS = P()

SECTION = "x"
"""Cut lengthwise. The whole point of this part is the interior column, and a
side view is the only one that shows it."""

PRINT_ROTATION = (0, 0, 0)
"""Upright, as modelled — same as the castle. Halving does not change which way
anything faces."""


def geometry(p: P) -> SimpleNamespace:
    """Derived values, read by both build() and check().

    All in MODEL units, i.e. the castle's full-size frame. Multiply by
    `p.scale` for finished dimensions; the puck is NOT scaled, because it is a
    physical object that does not care what we do here.
    """
    ch = {c.name: c for c in CASTLE.CHAMBERS}
    face, second, turret = ch["face"], ch["second"], ch["top_turret"]

    # One slab per storey transition: the ceiling of the chamber below is the
    # floor of the chamber above, and the gap between them IS the slab.
    slabs = (
        SimpleNamespace(name="under_second", z0=face.top, z1=second.floor,
                        x0=second.x0, x1=second.x1, y0=second.y0),
        SimpleNamespace(name="under_turret", z0=second.top, z1=turret.floor,
                        x0=turret.x0, x1=turret.x1, y0=turret.y0),
    )

    return SimpleNamespace(
        face=face, second=second, turret=turret, slabs=slabs,
        depth=CASTLE.PARAMS.depth,
        # The merged void, in finished millimetres.
        void_z0=face.floor * p.scale,
        void_z1=turret.top * p.scale,
        void_h=(turret.top - face.floor) * p.scale,
        floor_w=(face.x1 - face.x0) * p.scale,
        floor_d=(CASTLE.PARAMS.depth - face.y0) * p.scale,
    )


def _slab_cutter(s, p: P) -> Part:
    """A box covering one slab's INTERIOR footprint only.

    Deliberately clipped to the chamber it floors rather than to the block
    outline. The slab continues under the walls as their footing, and cutting
    that away would open the storeys to the outside — which is this repo's
    single most repeated bug, geometry sized from one constraint and never
    checked against its surroundings. Here the constraint is "remove a floor"
    and the surroundings are the walls holding it up.

    **`y0` is the tier line, not the inside face.** The storey's front wall
    stands on `y0` and is `wall` thick, so a cutter starting at `y0` saws a
    horizontal slot clean through it — which is precisely what the first
    version did, opening a 6.4 mm gap at the wall-walk level that let light out
    from behind the battlements. The x range needs no such inset because
    `x0`/`x1` are already the chamber interior; only y is measured from the
    outside. An asymmetry worth stating, because it is invisible at the call
    site and cost a defect to find.
    """
    inner_y = s.y0 + CASTLE.PARAMS.wall
    w = s.x1 - s.x0
    d = (CASTLE.PARAMS.depth - inner_y) + 2.0   # out through the open back
    h = (s.z1 - s.z0) + 2 * p.slack
    return Box(w, d, h, align=(Align.MIN, Align.MIN, Align.MIN)).locate(
        Location((s.x0, inner_y, s.z0 - p.slack)))


def build(p: P) -> Part:
    g = geometry(p)
    part = CASTLE.build(CASTLE.PARAMS)

    if not p.floors:
        for s in g.slabs:
            part -= _slab_cutter(s, p)

    return scale(part, p.scale)


def check(part: Part, p: P) -> None:
    g = geometry(p)

    assert len(part.solids()) == 1, (
        f"the part is {len(part.solids())} separate solids, not one — a slab "
        f"cutter has probably severed something it was not meant to touch"
    )

    bb = part.bounding_box()

    # --- the load-bearing one: does a puck actually fit? -------------------
    # The whole reason this part exists. Asserted on DERIVED clearances rather
    # than on `scale`, because each of width, depth and height can look fine
    # while the space between them is nothing.
    if not p.floors:
        assert g.void_h >= PUCK.flame_top, (
            f"the merged cavity is {g.void_h:.1f} mm tall but a puck is "
            f"{PUCK.flame_top} mm to the flame tip. Raise scale, or this part "
            f"has no reason to exist."
        )
        assert g.floor_w >= PUCK.dia and g.floor_d >= PUCK.dia, (
            f"the ground floor is {g.floor_w:.1f} x {g.floor_d:.1f} mm and the "
            f"puck is {PUCK.dia} mm across; it cannot be stood up in there"
        )
    else:
        # With the slabs in place every chamber is too short, which is the
        # observation this part was built from. Assert it so `floors=True` can
        # never quietly look like a working lantern.
        h = (g.face.top - g.face.floor) * p.scale
        assert h < PUCK.flame_top, (
            f"floors=True is meant to reproduce the un-liftable 50% print, but "
            f"the face chamber is {h:.1f} mm and a puck is {PUCK.flame_top} — "
            f"it would fit, so this branch is no longer what it claims"
        )

    # --- the slabs really are gone ----------------------------------------
    # Probe the middle of the column at each slab's old height. A cutter that
    # missed leaves geometry that still renders as a plausible castle.
    if not p.floors:
        for s in g.slabs:
            zmid = (s.z0 + s.z1) / 2 * p.scale
            x = (s.x0 + s.x1) / 2 * p.scale
            y = (s.y0 + CASTLE.PARAMS.depth) / 2 * p.scale
            probe = Box(2, 2, 1).locate(Location((x, y, zmid)))
            assert (part & probe).volume < 0.5, (
                f"the {s.name} slab is still there at z={zmid:.1f}"
            )

    # --- the front wall above each slab is still there ---------------------
    # The failure this catches is invisible to every other check here: a cutter
    # starting at the tier line instead of the inside face removes the storey's
    # FRONT WALL over the slab's z band, leaving a horizontal slot at the
    # wall-walk level that light escapes through from behind the battlements.
    # The part stays one solid and the bounding box does not move, so nothing
    # above notices. Found by eye on a render; asserted so it cannot come back.
    if not p.floors:
        wall = CASTLE.PARAMS.wall
        for s in g.slabs:
            zmid = (s.z0 + s.z1) / 2 * p.scale
            y = (s.y0 + wall / 2) * p.scale        # mid-thickness of that wall
            for frac in (0.25, 0.5, 0.75):         # across its width
                x = (s.x0 + (s.x1 - s.x0) * frac) * p.scale
                probe = Box(1, wall * p.scale * 0.5, 1).locate(Location((x, y, zmid)))
                assert (part & probe).volume > 0.05, (
                    f"the front wall above the {s.name} slab is missing at "
                    f"x={x:.1f}, z={zmid:.1f} — the slab cutter reached forward "
                    f"past the chamber and cut through it. Light would escape "
                    f"onto the wall walk behind the battlements."
                )

    # --- nothing was opened to the outside --------------------------------
    # A cutter that ran past the chamber into a wall would show up as a growth
    # in the bounding box or as a hole; the solid count above catches severance
    # and this catches over-reach.
    expect = CASTLE.build(CASTLE.PARAMS).bounding_box()
    for axis, got, want in (("X", bb.size.X, expect.size.X * p.scale),
                            ("Y", bb.size.Y, expect.size.Y * p.scale),
                            ("Z", bb.size.Z, expect.size.Z * p.scale)):
        assert abs(got - want) < 0.5, (
            f"bounding box {axis} is {got:.1f} mm, expected {want:.1f} — "
            f"removing a floor changed the outside of the castle, which means "
            f"a cutter reached past the chamber it belonged to"
        )
