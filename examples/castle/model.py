r"""castle — a haunted castle facade, lit from behind by tea lights.

    z
    |            /\           spire        tier 3, furthest back
    |          /----\
    |         |######|        great tower  tier 2   [puck: top turret]
    |    /\   |######|  /\
    |   |##|__|######|_|##|   keep         tier 1   [puck: second story]
    |   |################|
    |  _|################|_
    | |####################|  curtain wall tier 0   [pucks: eyes, mouth]
    | |###  (o)  (o)   ####|                        <- THE FACE
    | |####    \___/   ####|
    +-+--------------------+---- x

This is a **transformation of `inspiration/castle.png` into architecture**, not a trace of
it. The drawing is a flat elevation in four colours; the colours are a depth
map, higher up is further back. Everything else — tower radii, crenellation
size, where the face sits — was re-proportioned to survive a 0.4 mm nozzle at
printable size, because the drawing's crenellations measure 2 mm and its
portcullis bars 1.3 mm.

THE THREE FACTS THIS FILE TURNS ON
----------------------------------

1. **A tea light is not a glowing disc.** It is an opaque base with a short
   lit column above it (see `projects.halloween_lantern.shared`). Every opening
   must lie inside that column, measured from the surface its puck stands on.
   That is `_lit_span()`, and it is asserted per chamber.

2. **This cannot be a relief.** A puck is 35 mm across and 30 mm tall, and the
   drawing's four depth planes account for maybe 25 mm. So the depth map governs
   only the *front* surface; the shell runs back far enough to house pucks.

3. **One puck lights the whole face, and that is an open bet.** The eyes and the
   mouth are 30 mm apart and a puck lights ~15 mm directly. What is supposed to
   close the gap is the paper diffuser, which re-emits over its own whole
   surface — the lantern set established that it turns a near-line source into a
   lit column. `paper_spread` is that belief written as a number, and it is a
   guess. It is the reason the eyes and mouth sit where they do, and the print
   is what settles whether it was right. A second puck for the eyes is the known
   fix if it is not; it would go BEHIND the first, not above it, because height
   is spoken for and depth is not.

Read spec.md before editing, and notes.md before changing a number.
"""
from dataclasses import dataclass
from types import SimpleNamespace

from build123d import *
from build123d import Vector as _V  # noqa: F401  (star import already has it)

import printer
from cadkit import Params

# The puck is a fact about a physical object, not about Halloween — but it was
# measured for that set and that is where it lives. See spec.md's open
# questions: if a third part needs it, it should move somewhere neutral.
from projects.halloween_lantern.shared import PUCK


# ---------------------------------------------------------------------------
# The elevation.
#
# Positions are millimetres: x across (0 = the curtain wall's centre), z up from
# the base, and depth handled by `tier`. These are DESIGN DECISIONS taken with
# the drawing open, not measurements of it — several deliberately disagree with
# it where it would not print or would not light.
#
# The castle is asymmetric on purpose. It is haunted; see spec.md.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Block:
    """A rectangular mass in elevation: a wall, a keep, a buttress."""
    name: str
    tier: int
    x0: float
    x1: float
    top: float          # top of the plain body, before any crenellation
    crenel: bool = False
    depth: float = 0.0
    """How far back it runs. 0 means to the castle's rear plane, which is right
    for a storey — the depth map is about front faces, and every storey shares a
    back. It is wrong for anything small: a buttress given a storey's depth
    stops being a buttress and becomes a fin running the length of the castle at
    a height nothing else occupies."""


@dataclass(frozen=True)
class Tower:
    """A round tower standing proud of its tier's face, with a conical roof.

    Round rather than rectangular because the drawing's towers read as round —
    they have pointed roofs and an elevation only ever shows one side of them.
    A facade of flat prisms reads as a stage flat.
    """
    name: str
    tier: int
    x: float
    r: float
    body_top: float
    roof_top: float
    bore_from: float    # z at which the spill shaft starts: a chamber floor
    base: float = 0.0
    """Where the cylinder starts. 0 for a tower rising from the ground; a roof
    level for one that stands on the storey below."""
    y: float | None = None
    """Where its axis sits in depth. None means the tier's front plane, which is
    right for a tower standing PROUD of a wall — half of it bulges forward and
    that is the point.

    It is wrong for a tower standing ON something. The top turret inherited the
    tier plane and so sat a full radius forward of its own centre, fouling the
    parapet of the storey below and overhanging its front face. A tower on a
    roof should be centred on that roof."""

    hollow: bool = True
    """Whether to bore a shaft up it. False for anything too slender to hollow
    usefully — a 4 mm turret bored out is a 1.6 mm hole and a fragile wall."""


@dataclass(frozen=True)
class Opening:
    """A hole cut through one tier's front wall.

    `kind` selects the profile: a plain slot, a gothic arch, an arch with a
    retained pupil (an eye), or an arch divided by bars (the mouth).
    """
    name: str
    tier: int
    kind: str           # "slit" | "window" | "eye" | "mouth"
    x: float
    z0: float
    z1: float
    w: float
    lit_by: str         # which STATION's puck lights it; "" means spill-lit
    assert_lit: bool = True
    """Whether the model claims to know this opening is lit.

    False is not a shrug. It says the geometry is chosen by the design and the
    lighting will be settled by a print and a paper liner, rather than by
    `paper_spread` — which is a guess, and has no business vetoing a shape on
    the strength of a guess. The blind-pocket and nothing-behind-it checks still
    apply; only the reach of the flame is left open."""

    threshold: bool = False
    """This opening reaches the floor, so its foot is allowed to be dark.

    Only the entrance sets it. A gate that runs to the ground is taller than any
    puck standing on the chamber floor can light, and that is correct rather
    than a defect — a doorway darkens towards its threshold in the world too.

    It is a flag rather than a height because a height would be a number tuned
    to whatever the puck happens to reach today, and would stop meaning anything
    the moment the puck moved. The bound that keeps it honest is in check(): a
    threshold may be dark at the bottom, but not mostly dark."""


@dataclass(frozen=True)
class SideOpening:
    """A hole through one of a block's END walls, rather than its front.

    A castle seen only from the front is a stage flat, and the side walls are
    the largest blank surfaces on the part. These are cut on the other axis:
    positioned along `y` (depth) instead of x, and swept through in x.

    `side` is -1 for the left-hand wall and +1 for the right.
    """
    name: str
    block: str
    side: int
    kind: str
    y: float            # centre, measured back from the castle's front
    z0: float
    z1: float
    w: float            # width along the depth
    lit_by: str


@dataclass(frozen=True)
class TurretOpening:
    """A window cut radially through a round tower, at a bearing.

    The other two opening kinds are cut through flat walls on the two
    horizontal axes. A turret has neither: its wall is curved, so a window is
    placed by ANGLE and the cutter swept outward from the axis.
    """
    name: str
    tower: str
    angle: float        # degrees; 0 faces the front of the castle
    z0: float
    z1: float
    w: float


@dataclass(frozen=True)
class Chamber:
    """A hollow volume. One or more pucks stand inside it, at STATIONS.

    Chambers are separated in z by solid bands. That is what stops one puck
    lighting a neighbour's windows, and it is why the floors are not free
    numbers — see check().
    """
    name: str
    x0: float
    x1: float
    floor: float
    top: float
    y0: float           # front face of the tier it sits behind
    shaft: str = ""
    """A tower standing over this chamber whose bore continues upward.

    A puck is 35 mm across its base but its flame is only 10 mm, so a chamber
    too short for the whole puck can still hold one if there is a shaft above
    for the flame to stand up into. That is what lights a window in a turret far
    too slender to hold a puck of its own."""


@dataclass(frozen=True)
class Station:
    """Where one puck stands. A chamber may hold more than one.

    This exists because a puck lights about 31 mm of height even counting the
    paper, and the face is taller than that. Rather than compromise the face,
    the face chamber holds two: one on the floor at the front for the gate, one
    raised at the back for the eyes.

    They sit front-to-back rather than one above the other, and that is forced
    rather than chosen — stacking them needs 60 mm of height that the three
    chambers and the spire have already spent, while depth had nothing else
    competing for it. It is why `depth` is what it is.
    """
    name: str
    chamber: str
    stand: float        # how far above the chamber floor the puck stands
    y0: float           # front edge of its footprint


# How big this castle is pretending to be. 164 mm to the tip of the spire, read
# as a keep of about 120 feet, so a foot is a shade under a millimetre and a half.
#
# Not decoration. Until this existed, every architectural size here was picked
# by eye against the nozzle — which is why the parapets were as tall as a
# two-storey building and the merlons were six feet wide. A feature that exists
# in the world has a size in the world, and the only honest way to choose it is
# to convert. Where printability and the scale disagree, printability wins and
# the disagreement gets said out loud.
FOOT = 164.0 / 120.0

# --- tier front faces, front-most first.  Black, blue, green, red. ----------
#
# The step between tiers is not a drawing decision, it is a WALKWAY. Whatever a
# storey is set back from the one in front of it, minus the parapet standing on
# its edge, is what someone would have to walk along. At 8 mm — the step these
# started at, chosen to make the depth map legible — that came to under four
# feet, which is a ledge rather than a wall-walk. Fourteen leaves eight feet
# clear. `check()` asserts it so it cannot vanish again when something moves.
TIER_Y = (0.0, 14.0, 28.0, 42.0)

BLOCKS = (
    Block("curtain",     0, -64.0,  64.0,  50.0, crenel=True),
    Block("keep",        1, -46.0,  40.0,  90.0, crenel=True),
    Block("great_tower", 2, -17.0,  27.0, 124.0, crenel=True),
    # Tier 3 has no block. The top turret IS the fourth plane, and it is a
    # tower rather than a slab — see TOWERS.
)

# Where the top turret stands. Right of centre, like everything above the
# curtain wall — the drawing wanders and the castle is haunted.
SPIRE_X = 5.0

TOWERS = (
    Tower("corner_l",  0, -58.0, 9.0,  72.0,  96.0, bore_from=2.4),
    Tower("corner_r",  0,  58.0, 9.0,  72.0,  96.0, bore_from=2.4),
    Tower("keep_l",    1, -37.0, 8.5, 100.0, 126.0, bore_from=56.0),
    Tower("keep_r",    1,  31.0, 8.5, 100.0, 126.0, bore_from=56.0),
    # The top turret. A turret is a cylinder carrying a cone; a rectangular
    # block with a cone on it is a building wearing a hat, which is what this
    # was. Its shaft bores all the way down into the chamber below, so the
    # whole turret is one lit volume rather than a solid cap.
    # Centred on the great tower it stands on: x already matched, y is the
    # middle of that block's depth rather than the tier's front plane.
    Tower("top_turret", 3,  SPIRE_X, 14.0, 154.0, 178.0, bore_from=90.0,
          y=(28.0 + 82.0) / 2),
)

CHAMBERS = (
    Chamber("face",       -61.6, 61.6,   2.4,  47.6, y0=TIER_Y[0]),
    Chamber("second",     -43.6, 37.6,  52.0,  87.6, y0=TIER_Y[1]),
    Chamber("top_turret", -14.6, 24.6,  90.0, 121.6, y0=TIER_Y[2],
            shaft="top_turret"),
)

STATIONS = (
    # The face takes two. The gate's puck sits on the floor at the front, where
    # it can reach as far down the entrance as anything can; the eyes' puck
    # stands on a riser behind it, lighting the top of the wall. Neither could
    # do the other's job — see the Station docstring.
    Station("gate",   "face",        stand=0.0,  y0=2.4),
    Station("eyes",   "face",        stand=0.0,  y0=42.0),
    Station("second", "second",      stand=0.0,  y0=16.4),
    Station("top",    "top_turret",  stand=0.0,  y0=30.4),
)

# Where the face is centred. Not 0: the castle above it wanders right, and a
# face bolted to the geometric centre of an asymmetric building looks applied
# rather than inhabited.
FACE_X = 2.0

# Which teeth are canines, counting from the left, zero-based — so these are
# the 2nd and the 6th of seven. Not the outermost pair: the arch curves down
# over those, so they are already short, and a canine has to reach lower than
# its neighbours to read as one.
CANINES = (1, 5)

OPENINGS = (
    # --- the face. This is the design; everything else is a castle around it.
    #     z0 is the chamber floor, not zero. An opening reaching below the
    #     cavity behind it stops being an opening: the base slab is still there,
    #     so it becomes a blind pocket with a visible step in it. Asserted.
    Opening("mouth", 0, "mouth", FACE_X,        2.4, 35.0, 28.0, "gate",
            threshold=True),
    #     The eyes sit just under the wall head, and their sills are flush with
    #     the mouth's apex. They are lit by their own puck, not the gate's.
    #     The eyes sit high on the wall by design, above what a puck standing on
    #     the floor is calculated to reach. With the pedestal gone that sum no
    #     longer works out — but the sum is a guess and the position is not, so
    #     the position wins and the print settles it.
    Opening("eye_l", 0, "eye",   FACE_X - 20.0, 35.0, 47.0,  8.0, "eyes",
            assert_lit=False),
    Opening("eye_r", 0, "eye",   FACE_X + 20.0, 35.0, 47.0,  8.0, "eyes",
            assert_lit=False),
    # --- spill-lit arrow slits: no puck of their own, they glow on what leaks
    #     up the tower shafts. Widened from 3 mm and lengthened: at arrow-slit
    #     proportions they read as scratches on a tower rather than as windows,
    #     and nothing here is defending against archers.
    Opening("slit_cl", 0, "slit",  -58.0,  54.0,  68.0,  5.0, ""),
    Opening("slit_cr", 0, "slit",   58.0,  54.0,  68.0,  5.0, ""),
    Opening("slit_kl", 1, "slit",  -37.0,  72.0,  86.0,  5.0, ""),
    Opening("slit_kr", 1, "slit",   31.0,  72.0,  86.0,  5.0, ""),
    # --- the second story's double window, off-centre as the drawing has it,
    #     though on the other side of the keep from where the drawing put it.
    #     The whole second storey front is one great arched window with a bat
    #     standing in it. The pair of small windows that were here are gone:
    #     the motif needs the width, and its eyes need the width most of all.
    #     A THIRD of the wall's width, no more — the keep front is 86 mm and
    #     this is 26. It was 36, which read as a hole with a castle round it.
    Opening("win_bat", 1, "bat",     -3.0, 60.0,  87.0, 26.0, "second"),
    # The turret's own windows are not here — a round tower needs an angle,
    # not an x. See TURRET_WINDOWS.
)


SIDE_OPENINGS = (
    # Three a side along the curtain wall, two along the keep, one on the great
    # tower — the storeys get fewer and smaller as they get higher, which is
    # what stops the sides reading as a row of identical holes.
    #
    # The lower three are shared between the face chamber's two pucks: the
    # front one is lit by the gate's, the rear two by the eyes'. Nothing forces
    # every window in a chamber onto the same puck.
    *[SideOpening(f"side_low_{sd:+d}_{i}", "curtain", sd, "window",
                  y, 18.0, 34.0, 10.0, lit)
      for sd in (-1, 1)
      for i, (y, lit) in enumerate(((20.0, "gate"), (44.0, "eyes"),
                                    (66.0, "eyes")))],
    *[SideOpening(f"side_mid_{sd:+d}_{i}", "keep", sd, "window",
                  y, 68.0, 82.0, 8.0, "second")
      for sd in (-1, 1) for i, y in enumerate((34.0, 60.0))],
    *[SideOpening(f"side_top_{sd:+d}", "great_tower", sd, "window",
                  50.0, 108.0, 120.0, 7.0, "top")
      for sd in (-1, 1)],
)

# Four windows round the turret, evenly spaced, high up its shaft.
#
# They are NOT declared lit by the top puck, and that is a statement about what
# is known rather than about what will happen. The flame stops ~16 mm below
# them and `paper_spread` — the model's guess at how far a diffuser carries
# light — is not evidence about a 23 mm shaft that can itself be lined with
# paper. The lantern set found a paper liner turns a near-line source into a lit
# COLUMN, which is precisely this geometry. So the model declines to assert
# either way, the windows go where the design wants them, and the print settles
# it. Asserting a guess would have vetoed a good design on bad evidence.
TURRET_WINDOWS = (
    *[TurretOpening(f"turret_{a:03d}", "top_turret", float(a), 138.0, 150.0, 7.0)
      for a in (0, 90, 180, 270)],
    # The two front turrets get slits on their flanks as well as their faces.
    # A tower with an opening only where the elevation shows it is a tower
    # nobody has walked round.
    *[TurretOpening(f"{t}_{a:03d}", t, float(a), 54.0, 68.0, 5.0)
      for t in ("corner_l", "corner_r") for a in (90, 270)],
)

# The bat, traced from `inspiration/source-bat-image.png` rather than drawn by eye.
#
# u runs across the animal from -1 to +1; v runs up from the image's bottom edge
# — which is where the artwork is cropped, so v=0 is the line the wings run off.
# 66 points, Douglas-Peucker at 3 px from a 3493-pixel boundary trace.
#
# BAT_ASPECT is the number that matters most and the one an eye-trace gets
# wrong: the animal is 1.071 as wide as it is tall. Drawn freehand into a wide
# window it came out at 1.64 — squashed flat, and unrecognisable in a way that
# was hard to name and easy to see.
#
# It is RETAINED MATERIAL, dark against a lit window. Its widest point is near
# the bottom, where it meets both jambs, and its lower edge sits on the sill —
# so it is held on three sides. A bat floating inside its window would be a chip
# with no path to anything supported, which is what destroyed raven_lantern's
# lettering. The ears are the only parts that project, and they stand on the
# head beneath them.
BAT_ASPECT = 1.071
BAT = (
    (+0.250, 1.000), (+0.259, 0.995), (+0.275, 0.842), (+0.252, 0.782), (+0.201, 0.731),
    (+0.229, 0.675), (+0.215, 0.576), (+0.312, 0.506), (+0.380, 0.432), (+0.426, 0.417),
    (+0.521, 0.465), (+0.610, 0.529), (+0.635, 0.558), (+0.628, 0.577), (+0.638, 0.590),
    (+0.689, 0.597), (+0.733, 0.586), (+0.733, 0.566), (+0.703, 0.555), (+0.705, 0.532),
    (+0.882, 0.322), (+0.974, 0.165), (+1.000, 0.078), (+0.991, 0.000), (-0.984, 0.000),
    (-1.000, 0.058), (-1.000, 0.119), (-0.984, 0.177), (-0.889, 0.337), (-0.703, 0.529),
    (-0.689, 0.566), (-0.721, 0.582), (-0.717, 0.601), (-0.675, 0.611), (-0.626, 0.602),
    (-0.621, 0.563), (-0.589, 0.527), (-0.510, 0.465), (-0.433, 0.422), (-0.387, 0.435),
    (-0.312, 0.520), (-0.231, 0.572), (-0.289, 0.581), (-0.350, 0.598), (-0.394, 0.653),
    (-0.391, 0.664), (-0.357, 0.678), (-0.333, 0.680), (-0.315, 0.675), (-0.294, 0.687),
    (-0.301, 0.714), (-0.275, 0.741), (-0.322, 0.784), (-0.354, 0.836), (-0.366, 0.884),
    (-0.359, 0.945), (-0.329, 0.942), (-0.245, 0.900), (-0.185, 0.861), (-0.124, 0.805),
    (-0.066, 0.812), (-0.006, 0.807), (+0.027, 0.863), (+0.096, 0.929), (+0.180, 0.979),
)

# Its eyes: holes in a dark head, and the reason the window has to be as big as
# it is. MOVED from where they were traced, and that is worth explaining.
#
# Traced, they are 3.1% of the half-width — 0.4 mm here, which is not an eye but
# a gap between two extrusions. Enlarged to something printable they no longer
# fit where they sat: the head is 6.85 mm wide at this line, and at 1.1 mm across
# the left eye reached the edge of the head with 0.04 mm to spare and the strip
# between the two fell to 0.44 mm. Both showed up as ISLANDS, which is the
# check earning its keep — neither is visible in a render.
#
# So they are placed by the material available rather than by the reference:
# as far left as the material allows rather than centred in the head. The
# muzzle is on the left, and eyes centred behind a muzzle that is not read as
# a different animal facing forward. About a millimetre clear of the head's
# edge is the floor; the reference's own position leaves 0.04 mm.
BAT_EYES = ((-0.190, 0.711), (-0.048, 0.711))

BLOCK = {b.name: b for b in BLOCKS}
TOWER = {t.name: t for t in TOWERS}


@dataclass(frozen=True)
class P(Params):
    """The tunables. The elevation above is structure; these are the knobs."""

    wall: float = 2.4
    """Front and side walls. NOT an optical parameter here — unlike the lantern
    set, light leaves only through the openings, so this is structure, and it is
    what pays for the mortar grooves when they arrive."""

    floor_t: float = 2.4

    depth: float = 82.0
    """Front face to open back. Set by the deepest chamber having to swallow a
    puck plus fingers, not by the facade, which needs about 25 mm of it."""

    paper_spread: float = 8.0
    """How far beyond the flame the glued-on paper diffuser is assumed to carry
    light, at each end.

    **A guess, and the one the face depends on.** The lantern set established
    that the diffuser re-emits over its whole surface rather than merely
    softening a hot spot, but nobody has measured how far. It is named here
    rather than buried so that when the print comes back it can be corrected to
    a measurement instead of re-derived."""

    parapet_h: float = 3.0 * FOOT
    parapet_d: float = 2.0 * FOOT
    """The railing round the top of a storey: how far it stands above the
    wall-walk, and how deep it is front to back.

    A parapet is a **low wall standing on the front edge of a roof**, not a
    notch through the building. Cutting the crenellations full depth — which is
    what this did at first — turns the whole roof into a square wave in plan and
    leaves nothing to walk on. Nobody sees that in a front elevation, which is
    exactly why it survived several reviews."""

    min_walk: float = 6.0 * FOOT
    """The narrowest wall-walk worth calling one. Six feet — enough for two
    people to pass, which is what the thing is for."""

    merlon_w: float = 3.0 * FOOT
    embrasure_w: float = 2.0 * FOOT
    """Tooth and gap. The drawing's are 2 mm, which is five nozzle widths and
    invisible at arm's length; the first correction overshot to 8 mm, which is
    a six-foot merlon. Three feet and two feet are what a real one measures and
    they still clear the nozzle comfortably."""

    tip_r: float = 0.4
    """Radius a roof cone stops at instead of coming to a point.

    A tip finer than the nozzle is fiction — the printer cannot draw it — and
    OCC tessellates a true apex into slivers, triangles with two coincident
    vertices, which a slicer reports as degenerate. Half a square millimetre,
    at the top of a spire, in exchange for a clean mesh."""

    roof_flare: float = 1.2
    flare_h: float = 3.0
    """How far a conical roof oversails its tower, and over what height it grows
    out to do so.

    `flare_h` is why there is no flat ring under any roof here. A cone whose base
    is simply wider than the cylinder it sits on leaves a horizontal annulus with
    nothing under it — attached all the way round, so it droops rather than
    falling, but it droops on every tower and it is the ugliest surface on the
    part. Growing the same 1.2 mm out over 3 mm of height makes it a 68° cone
    instead: no flat face, no droop, and the silhouette is unchanged."""

    brick: bool = True
    brick_l: float = 9.0 * FOOT
    brick_h: float = 4.5 * FOOT
    mortar_w: float = 0.9
    mortar_d: float = 0.35
    """Nine feet by four and a half — megalithic rather than merely large, and
    half again the size first tried, which still read as brickwork rather than
    as a castle's stones.

    The mortar is 0.9 mm wide so it survives a 0.4 mm nozzle, and only 0.35 mm
    deep into a 2.4 mm wall. Depth is not what makes a joint read; the shadow
    line is, and a deep groove just eats wall and collects support material."""

    gate_margin: float = 3.0
    """How far the gate's plain-stone surround reaches beyond the archway."""

    shingle_course: float = 3.2
    shingle_w: float = 6.0
    shingle_groove: float = 0.8
    shingle_d: float = 0.5
    """Roof tiles. Shallower and finer than the walls' courses, because a roof
    is tiled rather than built, and because the cone runs out of circumference
    as it climbs."""

    corbel_max: float = 16.0
    """How far a chamber may close in below its ceiling, at 45 deg.

    A flat ceiling over a hollow is the one thing a slicer cannot do without
    support, and these are the largest surfaces on the part by a wide margin —
    the face chamber's ceiling alone is 9700 mm2. Corbelling is what a vaulted
    undercroft does anyway, and it costs nothing in light or in function.

    A maximum, not a value: the real limit is the puck standing underneath, and
    that is worked out per chamber in geometry(). A corbel that reached lower
    than a puck's shoulder would be a chamber that cannot be loaded."""

    deck_t: float = 6.0
    pillar_w: float = 6.0
    riser_span: float = 45.0
    """How far back a chamber's riser runs. Solid rather than a shelf on legs:
    a shelf is a bridge, and this is behind the show side where ugly is free."""

    eye_spring: float = 0.45
    mouth_spring: float = 0.04
    """Where each pointed arch starts to curve, as a fraction of its height.
    The mouth springs low so the head is most of the opening — that is what
    makes it read as a gate rather than as a tall window."""

    bat_scale: float = 1.03
    bat_drop: float = 0.0
    """How wide the bat is drawn as a fraction of its window, and how far its
    feet sit above the sill. Its HEIGHT is never set here — it follows from
    BAT_ASPECT, so the animal cannot be stretched to fill a box.

    Slightly OVER 1 on purpose. Traced exactly, the widest point of the wings
    lands 0.15 mm short of the jambs, which leaves a pair of hairline slots down
    the sides of the window: too thin to print, and read as a defect rather than
    as light. A few percent of bleed merges the wings into the jambs instead,
    which is also where the motif wants to be held."""

    bat_eye_r: float = 0.041
    bat_rise: float = 7.0
    """The bat's eye radius, and how far its window's segmental head rises."""

    pupil_w: float = 0.46
    pupil_h: float = 0.38
    pupil_bury: float = 0.30
    """The pupil: its width and its VISIBLE height as fractions of the eye, and
    how much of the oval hides below the sill. Burying part of it is what makes
    it an eye rather than a bead — a whole oval floating in a window is a hole
    with a lump in it."""

    pupil_toe: float = 0.07
    """How far the pupil sits towards the middle of the face, as a fraction of
    the eye's width. Small on purpose: enough to converge the gaze on something
    close in front, not enough to read as cross-eyed."""

    mouth_bars: int = 6
    lower_h: float = 8.0
    transom_h: float = 5.0
    canine_drop: float = 3.5
    tooth_short: float = 0.20
    """How much is taken off the bottom of every upper tooth EXCEPT the canines,
    as a fraction of that tooth's own length. Lifting the row makes the canines
    read as fangs rather than as two teeth that happen to be pointed."""

    canine_taper: float = 0.33
    """Where a canine starts narrowing, as a fraction of the tooth's height
    above the gum line. A third up is what makes it read as pointed rather than
    as chamfered."""
    """The lower jaw, the solid gum line above it, and how far the two canines
    reach down into that band. `canine_drop` must stay short of `transom_h` —
    a canine that punched through would divide the gum line and the mouth would
    stop reading as a mouth."""

    bar_w: float = 1.4
    """The BARS of the gate — the solid between the teeth, not the teeth.

    Getting this backwards made a speaker grille: at 2.2 mm on a 3.4 mm pitch
    the solid was wider than the gap, so the eye read a perforated panel rather
    than a row of bars with light between them. A portcullis is thin iron and
    mostly air; the teeth want to be roughly twice the bar, because equal reads
    as a grid.

    SEVEN teeth is the count that makes it a mouth — five looked like a vent —
    and holding both the count and the ratio is what sets the mouth's width.
    1.4 mm is three and a half extrusions: below the four this repo usually
    treats as a floor, and deliberately so. A bar of a gate is meant to be thin,
    it is a column standing on the sill with the full wall behind it, and the
    alternative was widening a mouth that was made narrow on purpose."""

    fit: float = 1.6
    """Radial clearance around a puck, from the lantern set: measured in the hand
    after 0.6 mm proved too tight, not calculated."""


PARAMS = P()

# Cut along X, through the centreline: the section that shows the three chambers
# stacked, the solid bands between them, and the plinth. The interior is the
# whole design problem here and a shaded exterior cannot show any of it.
SECTION = "x"

# Upright on its base, as modelled. The show side is then a vertical wall — the
# right orientation for brickwork — and the open back faces sideways, so no
# interior surface has to bridge across a cavity.
PRINT_ROTATION = (0, 0, 0)


# ---------------------------------------------------------------------------
# derived
# ---------------------------------------------------------------------------


def _ty(t: Tower) -> float:
    """A tower's axis in depth."""
    return TIER_Y[t.tier] if t.y is None else t.y


def geometry(p: P) -> SimpleNamespace:
    """Everything derived, in one place, read by both build() and check()."""
    _ch = {c.name: c for c in CHAMBERS}
    _stn = {s.name: s for s in STATIONS}
    xs = [b.x0 for b in BLOCKS] + [b.x1 for b in BLOCKS]
    xs += [t.x - t.r for t in TOWERS] + [t.x + t.r for t in TOWERS]
    # A tower must stand wholly on something, or its footprint hangs in air.
    for t in TOWERS:
        if t.base <= 0.0:
            continue
        under = [b for b in BLOCKS
                 if b.x0 <= t.x - t.r and t.x + t.r <= b.x1
                 and TIER_Y[b.tier] <= _ty(t) - t.r
                 and _ty(t) + t.r <= TIER_Y[b.tier] + (b.depth or p.depth)]
        assert under, (f"{t.name} stands at z={t.base} on nothing that "
                       f"contains its footprint")
    tops = [b.top + (p.parapet_h if b.crenel else 0.0) for b in BLOCKS]
    tops += [t.roof_top for t in TOWERS]
    front = min(-t.r for t in TOWERS)      # towers bulge forward of y=0

    return SimpleNamespace(
        width=max(xs) - min(xs),
        height=max(tops),
        depth=p.depth - front,
        front=front,
        chambers={c.name: c for c in CHAMBERS},
        # How far each chamber may corbel. Two limits, and the second is the
        # one that matters: a corbel narrows the chamber as it nears the
        # ceiling, so it closes in BEHIND anything cut in the walls up there.
        # Most windows sit just under their ceiling, which leaves very little
        # room — and on this castle, almost none. That is the correct answer,
        # not a disappointing one: a window with material behind it is not a
        # window, and no amount of saved support material buys that back.
        corbel={
            c.name: max(0.0, min(
                p.corbel_max,
                # clear of the shoulder of the tallest puck standing in it
                c.top - p.fit - max(
                    (c.floor + st.stand + PUCK.opaque_h
                     for st in STATIONS if st.chamber == c.name),
                    default=c.floor),
                # and clear of the head of every opening it serves
                c.top - max(
                    (o.z1 for o in (*OPENINGS, *SIDE_OPENINGS)
                     if o.lit_by and _stn[o.lit_by].chamber == c.name
                     and o.z1 <= c.top),
                    default=c.floor)))
            for c in CHAMBERS},
        stations={s.name: s for s in STATIONS},
        stand_z={s.name: _ch[s.chamber].floor + s.stand for s in STATIONS},
        puck_r=PUCK.dia / 2 + p.fit,
    )


def _lit_span(stand: float, p: P, paper: bool = True) -> tuple[float, float]:
    """The z range a puck standing at height `stand` puts light behind.

    Two spans, and the difference between them matters. The DIRECT one is the
    flame itself: opaque base below it, nothing above it. The PAPER one adds
    `paper_spread` at each end, because the diffuser re-emits over its own
    surface rather than only softening a hot spot — that is the lantern set's
    finding, and `paper_spread` is how far it is *assumed* to reach.

    Openings are checked against the paper span, so a failure means genuinely
    dark rather than merely dim. Coverage against the direct span is reported,
    not asserted, because how dim is too dim is a question for a print.
    """
    lo, hi = stand + PUCK.opaque_h, stand + PUCK.flame_top
    return (lo - p.paper_spread, hi + p.paper_spread) if paper else (lo, hi)


# ---------------------------------------------------------------------------
# primitives
# ---------------------------------------------------------------------------


# Mode.PRIVATE on every primitive, and every one of these called BEFORE the
# builder context is entered. build123d adds a primitive to whatever builder is
# active at the moment it is constructed — so a helper that returns `Pos(...) *
# Box(...)` from inside a `with BuildPart()` contributes the box TWICE: once
# where the caller puts it, and once unplaced at the origin. It costs nothing to
# be explicit and it cost a whole phantom mass to find out.


def _box(x0, x1, y0, y1, z0, z1) -> Part:
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0,
                                 align=(Align.MIN, Align.MIN, Align.MIN),
                                 mode=Mode.PRIVATE)


def _cyl(x, y, r, z0, z1) -> Part:
    return Pos(x, y, z0) * Cylinder(
        r, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN),
        mode=Mode.PRIVATE)


def _frustum(x, y, r0, r1, z0, z1) -> Part:
    # OCC's Cone is degenerate when the two radii match — a straight course
    # round a tower shaft is a cylinder, not a cone with zero taper.
    if abs(r1 - r0) < 1e-9:
        return _cyl(x, y, r0, z0, z1)
    return Pos(x, y, z0) * Cone(
        r0, r1, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN),
        mode=Mode.PRIVATE)


def _cone(x, y, r, z0, z1) -> Part:
    return Pos(x, y, z0) * Cone(
        r, 0.0, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN),
        mode=Mode.PRIVATE)


def _taper_box(lo: tuple, hi: tuple, z0: float, z1: float) -> Part:
    """A box whose footprint changes with height. Each tuple is (x0,x1,y0,y1)."""
    with BuildPart() as bp:
        for (a0, a1, b0, b1), z in ((lo, z0), (hi, z1)):
            with BuildSketch(Plane.XY.offset(z)):
                with Locations((((a0 + a1) / 2), ((b0 + b1) / 2))):
                    Rectangle(a1 - a0, b1 - b0)
        loft()
    return bp.part


def _through(sk: Sketch, y0: float, y1: float) -> Part:
    """Extrude a front-elevation sketch through the y range [y0, y1].

    The sketch arrives drawn on the DEFAULT plane, in (x, z) — this is the one
    place that maps it onto the elevation, so the mapping happens exactly once.
    Profiles that place themselves on Plane.XZ and are then added to another
    Plane.XZ sketch get transformed twice and land somewhere plausible-looking
    but wrong.

    Extruded symmetrically and then positioned, so it does not depend on which
    way Plane.XZ's normal points — a detail that is easy to get backwards and
    that yields a cutter which misses the wall silently.
    """
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            add(sk)
        extrude(amount=(y1 - y0) / 2, both=True)
    return Pos(0, (y0 + y1) / 2, 0) * bp.part


def _radial(sk: Sketch, t: "Tower", reach: float) -> Part:
    """Sweep a profile outward from a tower's axis, on a bearing.

    Extruded in ONE direction only. Both ways would punch a matching window out
    of the far side of the tower — which looks fine in any single elevation and
    is how a facade quietly acquires holes nobody asked for.
    """
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            add(sk)
        extrude(amount=reach)
    return bp.part


def _through_side(sk: Sketch, x0: float, x1: float) -> Part:
    """Extrude a profile through the x range [x0, x1], for a wall facing sideways.

    The same profile helpers serve both directions. They draw in local (u, v);
    on Plane.XZ that lands as (x, z) and on Plane.YZ as (y, z), so an arch is an
    arch whichever wall it is cut in and nothing has to be written twice.
    """
    with BuildPart() as bp:
        with BuildSketch(Plane.YZ):
            add(sk)
        extrude(amount=(x1 - x0) / 2, both=True)
    return Pos((x0 + x1) / 2, 0, 0) * bp.part


# ---------------------------------------------------------------------------
# opening profiles, drawn in the XZ plane
# ---------------------------------------------------------------------------


def _arch(x: float, z0: float, z1: float, w: float, spring: float = 0.45) -> Sketch:
    """A pointed arch: straight sides to the springing line, then two arcs
    meeting at a point.

    `spring` is the fraction of the height at which the curve starts. The head
    is the intersection of two equal discs whose centres sit on the springing
    line, which is how a real pointed arch is struck — pick the radius and the
    apex follows.

    A pointed head, not a semicircular one, because a semicircular head is only
    possible while the opening is at least twice as tall as it is wide.
    Widen one past that and the head eats the whole opening: the first mouth
    here was 22 mm across and 15 mm tall and came out a perfect circle.
    """
    z_s = z0 + (z1 - z0) * spring
    hh = z1 - z_s
    assert hh > w / 2, (
        f"a pointed arch {w:.1f} mm wide needs more than {w / 2:.1f} mm of head; "
        f"this one has {hh:.1f}. Raise z1, lower `spring`, or narrow it."
    )
    c = (hh * hh - w * w / 4) / w        # arc centres, offset either side
    with BuildSketch() as head:
        with Locations((x - c, z_s)):
            Circle(w / 2 + c)
        with Locations((x + c, z_s)):
            Circle(w / 2 + c, mode=Mode.INTERSECT)
        with Locations((x, z_s + hh / 2)):     # discard the lower half-lens
            Rectangle(w, hh, mode=Mode.INTERSECT)
    with BuildSketch() as sk:
        with Locations((x, (z0 + z_s) / 2)):
            Rectangle(w, z_s - z0)
        add(head.sketch)
    return sk.sketch


def _segmental(x: float, z0: float, z1: float, w: float, rise: float) -> Sketch:
    """A wide opening with a shallow arc on top — a segmental arch.

    A POINTED arch cannot be wide. Its head must be more than half the opening's
    width in height, so at 36 mm across it needs 18 mm of head, and an opening
    that is wider than it is tall becomes all head: the arch closes in over the
    lower corners and eats whatever the window was cut to show. That is what
    swallowed the bat's wings.

    A segmental head is struck from a much larger radius, so the opening stays
    full width nearly to the top and the head is only `rise` tall. Real
    architecture, and the only shape that lets a wide motif be seen.
    """
    r = (w * w / 4) / (2 * rise) + rise / 2
    with BuildSketch() as sk:
        with Locations((x, (z0 + z1 - rise) / 2)):
            Rectangle(w, (z1 - rise) - z0)
        with Locations((x, z1 - r)):
            Circle(r)
        with Locations((x, (z0 + z1) / 2)):        # trim the circle to the window
            Rectangle(w, z1 - z0, mode=Mode.INTERSECT)
    return sk.sketch


def _pupil(x: float, sill: float, visible: float, w: float, p: P) -> Sketch:
    """An oval whose lower part falls below the sill and is therefore never seen.

    Not a slot with a rounded cap. Every opening in this castle is an arch of
    some kind, which is right for windows and wrong here — an arch has straight
    sides, and straight sides read as another little window rather than as an
    eye looking back at you.

    The whole shape is an ellipse; `p.pupil_bury` of its height sits below the
    sill, so the sill crops it. Nothing has to clip it explicitly: the pupil is
    subtracted from the window, and below the sill there is no window to
    subtract from.
    """
    full = visible / (1.0 - p.pupil_bury)
    with BuildSketch() as sk:
        with Locations((x, sill + visible - full / 2)):
            Ellipse(w / 2, full / 2)
    return sk.sketch


def _arch_top(dx: float, w: float, z0: float, z1: float, spring: float) -> float:
    """Height of a pointed arch's head at horizontal offset `dx` from centre.

    Needed because the teeth are clipped by the arch, so each one is a different
    length and "shorten them by a fifth" means a fifth of ITS OWN length. A flat
    fraction of the nominal height would take the same millimetres off the short
    outer teeth as off the tall middle ones, and delete them.
    """
    z_s = z0 + (z1 - z0) * spring
    hh = z1 - z_s
    c = (hh * hh - w * w / 4) / w
    R = w / 2 + c
    tops = []
    for cx in (-c, c):
        d = dx - cx
        if abs(d) >= R:
            return z_s
        tops.append(z_s + (R * R - d * d) ** 0.5)
    return min(tops)


def _eye(x: float, z0: float, z1: float, w: float, p: P, inward: float) -> Sketch:
    """A pointed window with a pupil standing in it.

    The pupil is what makes this an eye rather than a window. It is a small arch
    of its own, **rising from the sill** rather than floating in the middle of
    the opening — so it is material continuous with the wall below, not the
    detached chip that destroyed `raven_lantern`'s lettering. Lit, it reads as a
    dark pupil in a bright eye; printed, there is nothing to hold up.

    It is also **off-centre, towards the middle of the face**. A pupil centred
    in its window stares through you; a pair converged slightly inward is
    looking at something just in front of them, which is a great deal more
    unsettling for a shift of a millimetre or two. `inward` points at the
    face's centreline.
    """
    with BuildSketch() as sk:
        add(_arch(x, z0, z1, w, p.eye_spring))
        add(_pupil(x + inward * w * p.pupil_toe, z0,
                   (z1 - z0) * p.pupil_h, w * p.pupil_w, p),
            mode=Mode.SUBTRACT)
    return sk.sketch


def _mouth(x: float, z0: float, z1: float, w: float, p: P) -> Sketch:
    r"""The grand entrance, and a mouth with upper and lower teeth.

        z1  ──      /\        pointed head, self-bridging
                   /  \
                  |||||||     upper teeth
        t1  ──    ═V═════V═   ↑ the canines taper into the band, not through it
                  ═════════   THE GUM LINE: solid, unbroken, full width
        t0  ──    |||||||||   lower teeth
        z0  ──    ─────────   the floor: this is an entrance, so it reaches it

    The band between the two rows is **solid material across the whole width**,
    and no tooth crosses it. That is what separates an upper jaw from a lower
    one; without it the mouth is a portcullis rather than a face.

    The canines are two upper teeth that reach further down than their
    neighbours, ending *inside* the band. Note which way round that is: a tooth
    here is an opening, so a canine is a slot with solid material below its tip,
    and there is nothing unsupported anywhere in the mouth. Teeth that hung the
    other way — material projecting down over an opening — would be an island on
    every layer of their length, needing supports inside the mouth where the
    scars would show. The drawing's arrangement is also the printable one.

    The gate runs to the floor because it is the castle's entrance as well as
    its mouth. Its lower reach is therefore below anything a puck standing on
    the chamber floor can light; see `lit_from`. A doorway that darkens towards
    its threshold is what happens in the world too.
    """
    t0 = z0 + p.lower_h
    t1 = t0 + p.transom_h
    pitch = w / (p.mouth_bars + 1)

    def bar_x(i: int) -> float:             # bars are numbered 1..mouth_bars
        return x - w / 2 + i * pitch

    def slot_x(i: int) -> float:            # slot i lies between bars i and i+1
        return x - w / 2 + (i + 0.5) * pitch

    def slot_span(i: int) -> tuple[float, float]:
        """Where slot i actually begins and ends.

        The outermost two are NOT a bar's width narrower than the pitch — they
        are bounded by the arch itself. Treating every slot alike left an
        L-shaped step in the bottom of the first and last teeth, because the cut
        was centred and sized for an interior slot.
        """
        lo = x - w / 2 if i == 0 else bar_x(i) + p.bar_w / 2
        hi = x + w / 2 if i == p.mouth_bars else bar_x(i + 1) - p.bar_w / 2
        return lo, hi

    with BuildSketch() as sk:
        add(_arch(x, t1, z1, w, p.mouth_spring))       # the head
        with Locations((x, (z0 + t0) / 2)):            # the lower jaw
            Rectangle(w, t0 - z0)
        for i in range(1, p.mouth_bars + 1):           # divide both into teeth
            with Locations((bar_x(i), (z0 + z1) / 2)):
                Rectangle(p.bar_w, z1 - z0, mode=Mode.SUBTRACT)
        # The other upper teeth stop short of the gum line, so the two canines
        # are not merely pointed but visibly LONGER than the row they sit in.
        # Each loses a fraction of its own length, measured against where the
        # arch cuts it off — see _arch_top.
        for i in range(p.mouth_bars + 1):
            if i in CANINES:
                continue
            lo, hi = slot_span(i)
            cut = ((_arch_top((lo + hi) / 2 - x, w, t1, z1, p.mouth_spring) - t1)
                   * p.tooth_short)
            if cut > 0.05:
                with Locations(((lo + hi) / 2, t1 + cut / 2)):
                    Rectangle(hi - lo, cut, mode=Mode.SUBTRACT)

        # The canines: they carry on below the other teeth and TAPER TO A POINT.
        #
        # The taper begins ABOVE the gum line, partway up the tooth itself, not
        # at the point where the row ends. Starting it at the gum line makes a
        # 3 mm-wide slot end in a 3 mm-tall wedge, which reads as a slot with a
        # corner knocked off. Starting it a third of the way up the tooth gives
        # a taper three times as long as it is wide, which reads as a fang.
        #
        # Still an opening biting down into solid material, so nothing is
        # unsupported: the tip has material below it and on both sides.
        half = (pitch - p.bar_w) / 2
        for i in CANINES:
            xc = slot_x(i)
            tip = t1 - p.canine_drop
            start = t1 + (z1 - t1) * p.canine_taper
            # Clear the column first, so the taper alone defines the shape here.
            with Locations((xc, (tip + start) / 2)):
                Rectangle(pitch - p.bar_w, start - tip, mode=Mode.SUBTRACT)
            with BuildLine():
                Polyline((xc - half, start), (xc + half, start),
                         (xc, tip), close=True)
            make_face()
    return sk.sketch


def _opening_y(o: Opening, p: P) -> tuple[float, float]:
    """The y range a cutter must sweep to pierce the wall this opening is in.

    A block's front is its tier plane. **A tower's front is a radius in front of
    that**, and getting this wrong does not fail — it cuts a slab through the
    middle of a tower that is already bored hollow, so it removes nothing at all
    and the model builds clean. Every arrow slit in this part was silently
    absent for exactly that reason, through a dozen builds and several reviews:
    an elevation cannot tell a hole from a shaft seen end-on.

    For a tower the cutter runs from in front of the curved wall all the way to
    the axis, so it cannot miss whatever the wall thickness happens to be.
    """
    t = next((t for t in TOWERS
              if t.tier == o.tier and abs(t.x - o.x) < 1e-6), None)
    if t is None:
        return TIER_Y[o.tier] - 2.0, TIER_Y[o.tier] + p.wall + 2.0
    return _ty(t) - t.r - 2.0, _ty(t) + 1.0


def _bat(x: float, z0: float, z1: float, w: float, p: P) -> Sketch:
    """The bat silhouette, oversized so the window crops it.

    Drawn LARGER than the opening on purpose. The reference is cropped — its
    wings run off both sides and the bottom — and that framing is most of why
    the head reads big and the animal reads close. Fitted neatly inside the
    window instead, the same outline gives a small head marooned in a wide
    space, which is what the first attempt looked like.

    Anything outside the window is simply not subtracted, so the crop costs
    nothing and needs no clipping.
    """
    bw = w * p.bat_scale
    bh = bw / BAT_ASPECT          # the animal's own proportions, never the box's
    def at(u, v):
        return x + u * bw / 2, z0 + p.bat_drop + v * bh
    with BuildSketch() as sk:
        with BuildLine():
            Polyline(*[at(u, v) for u, v in BAT], close=True)
        make_face()
        for u, v in BAT_EYES:
            with Locations(at(u, v)):
                Circle(p.bat_eye_r * bw / 2, mode=Mode.SUBTRACT)
    return sk.sketch


def _opening_sketch(o: Opening, p: P) -> Sketch:
    if o.kind == "bat":
        with BuildSketch() as sk:
            add(_segmental(o.x, o.z0, o.z1, o.w, p.bat_rise))
            add(_bat(o.x, o.z0, o.z1, o.w, p), mode=Mode.SUBTRACT)
        return sk.sketch
    if o.kind == "eye":
        return _eye(o.x, o.z0, o.z1, o.w, p, 1.0 if o.x < FACE_X else -1.0)
    if o.kind == "mouth":
        return _mouth(o.x, o.z0, o.z1, o.w, p)
    return _arch(o.x, o.z0, o.z1, o.w)


# ---------------------------------------------------------------------------
# masonry
#
# The whole point is to build it CHEAPLY. A castle this size is some 1500
# bricks, and cutting them one at a time is 1500 solid booleans, which OCC will
# take minutes over. Two tricks avoid that:
#
#   * a flat face's mortar is one SKETCH — every bed and every joint placed with
#     GridLocations, fused in 2D where it is cheap, then extruded and cut once.
#     About a second a face.
#   * a roof's shingles use PolarLocations for the same reason, and the courses
#     are frustum rings, so a roof is a handful of solids rather than a hundred.
#
# Nothing here is deep: the grooves are 0.6 mm into a 2.4 mm wall. They are
# there to catch a shadow, not to model masonry.
# ---------------------------------------------------------------------------


def _jitter(i: int) -> float:
    """A repeatable pseudo-random number in [0, 1).

    Deliberately NOT `random`: a build must give the same castle every time, or
    the history and the oscillation guard are comparing different objects. This
    is a hash of the course index, so the masonry is irregular but fixed.
    """
    x = (i * 1103515245 + 12345) & 0x7FFFFFFF
    x ^= x >> 13
    return ((x * 2654435761) & 0x7FFFFFFF) / 0x7FFFFFFF


def _brick_sketch(u0: float, u1: float, v0: float, v1: float,
                  p: P, seed: int) -> Sketch:
    """The mortar for a face, in that face's own absolute coordinates.

    Absolute rather than centred, so a caller can cut a region OUT of it — the
    gate is wrought iron and takes no mortar at all — without having to work out
    where the grid ended up.

    Irregular on purpose. A running bond with a strict half-brick offset is
    still a perfect lattice, and it reads as machine-laid tile rather than as
    stone: every course starts at its own jittered offset and every block is a
    different length. Deterministic, so the castle does not change between
    builds.
    """
    cz = p.brick_h + p.mortar_w
    with BuildSketch() as sk:
        v = v0
        course = 0
        while v + p.mortar_w <= v1:
            # the bed
            with Locations(((u0 + u1) / 2, v + p.mortar_w / 2)):
                Rectangle(u1 - u0, p.mortar_w)
            # The perpends of this course, walking it with varied block lengths.
            #
            # Clipped to what is left above the bed. The loop admits a course
            # whenever its BED fits, and the joints then stand a full block
            # higher — so the topmost course used to overshoot v1 by up to
            # `brick_h` and carve straight up through whatever sat above. On the
            # keep that is the parapet, whose merlons are shorter than a block:
            # each is one stone in the world and was arriving quartered.
            ph = min(p.brick_h, v1 - (v + p.mortar_w))
            u = u0 - p.brick_l * _jitter(seed * 131 + course)
            k = 0
            while u < u1 and ph > 0.5:
                bl = p.brick_l * (0.78 + 0.44 * _jitter(seed * 977 + course * 31 + k))
                u += bl
                if u0 < u < u1 - p.mortar_w:
                    with Locations((u, v + p.mortar_w + ph / 2)):
                        Rectangle(p.mortar_w, ph)
                u += p.mortar_w
                k += 1
            v += cz
            course += 1
    return sk.sketch


def _no_mortar(b: Block, p: P) -> list[Sketch]:
    """Regions of a block's front face that are not masonry at all.

    Three kinds, and each is a statement about what the thing IS:

    * **the gate** is a wrought-iron portcullis hung in a stone wall, so the
      whole archway — head, jambs, teeth and the ground between them — carries
      no coursing, and gets a plain surround round it besides.
    * **a pupil** is an eye, not a block of the wall it happens to sit in.
    * **the bat** is a creature in a window. Coursing over it makes it part of
      the masonry, which is the one thing it is not.

    The gate's surround is a true 2D OFFSET of the gate's own outline, not a
    larger arch drawn from the same recipe. A re-derived arch is only parallel
    to the original by accident: it gave a generous margin round the lower teeth
    and almost none round the upper ones, because a pointed arch's width falls
    away fastest exactly where the two outlines were closest.
    """
    out = []
    for o in OPENINGS:
        if o.tier != b.tier:
            continue
        if o.kind == "mouth":
            t1 = o.z0 + p.lower_h + p.transom_h
            with BuildSketch() as sk:
                add(_arch(o.x, t1, o.z1, o.w, p.mouth_spring))
                with Locations((o.x, t1 / 2)):        # jambs, down to the ground
                    Rectangle(o.w, t1)
                offset(amount=p.gate_margin, kind=Kind.INTERSECTION)
            out.append(sk.sketch)
        elif o.kind == "eye":
            out.append(_arch(o.x, o.z0, o.z1, o.w, p.eye_spring))
        elif o.kind == "bat":
            out.append(_segmental(o.x, o.z0, o.z1, o.w, p.bat_rise))
    return out


def _buried(b: Block) -> float:
    """How far up a block is hidden by something standing in front of it.

    Same rule as a tower's shaft, and the same saving: the great tower runs from
    the ground but is not seen below the keep's roof, so three quarters of its
    faces are inside other blocks. Texturing them costs booleans and shows
    nothing.
    """
    return max((o.top for o in BLOCKS
                if o is not b and TIER_Y[o.tier] <= TIER_Y[b.tier]
                and o.x0 <= b.x0 and b.x1 <= o.x1), default=0.0)


def _brick_flat(p: P) -> list[Part]:
    """Mortar cut into every flat face of every block, front and both sides.

    Stops at `b.top` — the roof line — so the PARAPET above it is left clean.
    Each merlon is one stone in the world, not a course of small ones, and a
    grid cut across a 4 mm crenellation is noise whichever way you look at it.
    """
    out = []
    for n, b in enumerate(BLOCKS):
        yf, back, z0 = TIER_Y[b.tier], _back(b, p), _buried(b)
        if b.top - z0 <= p.brick_h:
            continue
        with BuildSketch() as front:
            add(_brick_sketch(b.x0, b.x1, z0, b.top, p, seed=n))
            for zone in _no_mortar(b, p):
                add(zone, mode=Mode.SUBTRACT)
        cut = _through(front.sketch, yf, yf + p.mortar_d)
        # Masonry must stay inside the face it belongs to. This is the fourth
        # thing this session to escape its intended region and the second to do
        # it upwards, so it is asserted rather than trusted.
        assert cut.bounding_box().max.Z <= b.top + 1e-6, (
            f"{b.name}'s mortar reaches z {cut.bounding_box().max.Z:.1f}, above "
            f"its roof at {b.top:.1f} — it is cutting into the parapet")
        out.append(cut)
        for m, x in enumerate((b.x0, b.x1)):
            sk = _brick_sketch(yf, back, z0, b.top, p, seed=n * 7 + m + 3)
            out.append(_through_side(sk, x - p.mortar_d, x + p.mortar_d))
    return out


def _stonework(t: Tower, p: P) -> list[Part]:
    """Courses round a tower's shaft, and shingles over its roof.

    A conical roof is not brick — it is tiled, and the tiles get smaller as the
    cone closes in, which happens for free because each course is struck at the
    radius the cone actually has there.
    """
    import math
    y = _ty(t)
    out = []

    # Where a tower is embedded in a wall, only its FRONT arc is a surface.
    # A course band is a full annulus, and at the flanks its arc runs almost
    # along the depth axis — so behind the axis it stops grooving a tower and
    # starts sawing lengthways through a 2.4 mm wall, leaving slots you can see
    # daylight through. Cutters below the embedding block's roof get clipped to
    # the exposed half; above it the tower is free-standing and keeps its full
    # circumference.
    embed = [b for b in BLOCKS
             if b.x0 <= t.x + t.r and t.x - t.r <= b.x1
             and TIER_Y[b.tier] <= y <= _back(b, p)]
    embed_top = max((b.top for b in embed), default=0.0)

    def expose(part, z0, z1):
        if (z0 + z1) / 2 >= embed_top:
            return part
        # Clipped a little BEHIND the axis, not on it. On it, the clip plane
        # coincides with the tier's front face — which is exactly where the
        # wall's own bed grooves start, at exactly the same course heights,
        # since both are struck from the same pitch. Two cutters meeting
        # face-to-face there tessellate into non-manifold edges. The overlap is
        # buried inside the wall and shows nothing.
        return part & _box(t.x - t.r - 2, t.x + t.r + 2,
                           y - t.r - 2, y + 1.5, z0 - 1, z1 + 1)

    def band(z0, z1, r0, r1, depth):
        """A course groove, deepest at its bottom and CLOSING at its top.

        A groove of constant depth leaves a horizontal annulus at its head —
        only `depth` wide, but a full ring round a turret is some 50 mm2 of
        face, and a slicer's small-overhang filter works on area rather than on
        span. So the mortar beds got filtered out and the identical ledges on
        the roofs did not, and every shingle course grew its own supports.

        Tapering the groove shut removes the horizontal face entirely rather
        than hoping a setting will ignore it. It also looks more like a course
        of tiles, which overlap the one below and cast exactly this shadow.
        """
        outer = _frustum(t.x, y, r0, r1, z0, z1)
        inner = _frustum(t.x, y, max(r0 - depth, 0.05), r1, z0, z1)
        return expose(outer - inner, z0, z1)

    def joints(z0, z1, r, w, depth, course):
        # STAGGERED. Without a per-course rotation every joint sits at the same
        # bearing and they line up into continuous seams running the full height
        # of the tower — which is not masonry, it is a mould line.
        n = max(5, int(2 * math.pi * r / w))
        with BuildPart() as bp:
            with Locations(Plane.XY.offset(z0)):
                with PolarLocations(r, n,
                                    start_angle=360.0 / n * _jitter(course * 17)):
                    Box(depth * 3, p.mortar_w, z1 - z0,
                        align=(Align.CENTER, Align.CENTER, Align.MIN))
        return expose(Pos(t.x, y, 0) * bp.part, z0, z1)

    # --- the shaft: straight courses, like the walls -----------------------
    #
    # Only from where the tower EMERGES. Every tower's cylinder runs from the
    # ground up, but most of that length is buried inside the block it rises
    # through — the top turret's shaft starts at z=0 and is not seen below 124.
    # Coursing the buried part costs booleans and shows nothing; skipping it
    # took this from minutes to seconds.
    # A block buries a tower only if it swallows it in BOTH directions. Testing
    # x alone hid the keep towers to z=90, when they bulge forward of the keep's
    # face and are in plain sight from z=50 — the curtain wall in front of them
    # is what actually hides them, and only to its own height.
    buried = max((b.top for b in BLOCKS
                  if b.x0 <= t.x - t.r and t.x + t.r <= b.x1
                  and TIER_Y[b.tier] <= _ty(t) - t.r), default=0.0)
    cz = p.brick_h + p.mortar_w
    z = max(t.base, buried) + cz
    course = 0
    while z < t.body_top - p.flare_h:
        out.append(band(z, z + p.mortar_w, t.r, t.r, p.mortar_d))
        # Never below the base slab. A joint is a groove in a tower's SURFACE,
        # but the cutter is a radial box and it knows nothing about where that
        # surface is — at the bearings pointing back into the castle there is no
        # tower face there at all, just floor, and the lowest course punched
        # three small square holes clean through it. Visible only from
        # underneath, which is a view nobody had rendered.
        out.append(joints(max(z - cz, p.floor_t), z, t.r, p.brick_l,
                          p.mortar_d, course))
        z += cz
        course += 1

    # --- the roof: shingles ------------------------------------------------
    z0, z1 = t.body_top, t.roof_top
    R0, R1 = t.r + p.roof_flare, p.tip_r
    def r_at(zz):
        return R0 + (R1 - R0) * (zz - z0) / (z1 - z0)
    z = z0 + p.shingle_course
    course = 100
    while z < z1 - p.shingle_course / 2:
        out.append(band(z, z + p.shingle_groove,
                        r_at(z), r_at(z + p.shingle_groove), p.shingle_d))
        rm = r_at(z - p.shingle_course / 2)
        if rm > p.shingle_w:
            out.append(joints(z - p.shingle_course, z, rm, p.shingle_w,
                              p.shingle_d, course))
        z += p.shingle_course
        course += 1
    return out


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------


def _back(b: Block, p: P) -> float:
    """Where a block's rear face lies."""
    return TIER_Y[b.tier] + b.depth if b.depth else p.depth


def _crenel_spacing(span: float, p: P) -> list[tuple[float, float]]:
    """Where the embrasures fall along a run of parapet `span` long."""
    pitch = p.merlon_w + p.embrasure_w
    n = max(1, int((span - p.merlon_w) // pitch))
    used = n * pitch - p.embrasure_w + p.merlon_w
    lead = (span - used) / 2 + p.merlon_w
    return [(lead + i * pitch, lead + i * pitch + p.embrasure_w)
            for i in range(n)]


def _parapet(b: Block, p: P) -> list[Part]:
    """The railing along the front edge of a storey's roof.

        section, looking along the wall:

            ┌──┐                     ← parapet_h above the walk
            │  │·······················  the wall-walk, flat, open behind
            │  │                     │
            └──┴─────────────────────┘  the storey below, full depth
             ↑
             parapet_d

    A parapet stands ON the roof; it is not a notch through the building. The
    first version cut the crenellations the full depth of the block, which in
    plan turns the entire roof into a square wave and leaves nothing to walk on.
    A front elevation cannot show that, which is why it survived several
    reviews before someone pictured standing on it.
    """
    y0, d = TIER_Y[b.tier], p.parapet_d
    z0, z1 = b.top, b.top + p.parapet_h
    bars = [_box(b.x0, b.x1, y0, y0 + d, z0, z1)]      # along the front

    # The returns exist only where there is a roof left to walk on. `stub` is
    # seven millimetres wide: two returns leave a mm and a half between them, so
    # what it grew was not a railing round a terrace but a pair of crenellated
    # rails running the full depth of the castle at a level nothing occupies.
    # It looked like a third storey nobody had designed.
    if (b.x1 - b.x0) - 2 * d >= p.min_walk:
        bars.append(_box(b.x0, b.x0 + d, y0, _back(b, p), z0, z1))   # left
        bars.append(_box(b.x1 - d, b.x1, y0, _back(b, p), z0, z1))   # right
    return bars


def _crenel_cutters(b: Block, p: P) -> list[Part]:
    """The embrasures: gaps notched out of a parapet, and only out of it.

    Cut LAST, once the block has been hollowed. Hollowing a crenellated profile
    would mean insetting a ragged outline, which is a reliable way to make OCC
    produce something that is not a shell.
    """
    y0, d = TIER_Y[b.tier], p.parapet_d
    z0, z1 = b.top, b.top + p.parapet_h + 1.0
    cuts = [_box(b.x0 + a, b.x0 + z, y0 - 1.0, y0 + d + 1.0, z0, z1)
            for a, z in _crenel_spacing(b.x1 - b.x0, p)]
    # The returns are notched along y. Their first merlon starts a full
    # merlon-width back, which is further than the front run is deep, so the
    # two sets never cut into each other at the corner.
    if (b.x1 - b.x0) - 2 * d >= p.min_walk:        # matches _parapet
        for a, z in _crenel_spacing(_back(b, p) - y0, p):
            cuts.append(_box(b.x0 - 1.0, b.x0 + d + 1.0, y0 + a, y0 + z, z0, z1))
            cuts.append(_box(b.x1 - d - 1.0, b.x1 + 1.0, y0 + a, y0 + z, z0, z1))
    return cuts


def _platform(st: Station, p: P, g) -> list[Part]:
    """A flat deck on pillars for a puck to stand on.

    A solid block would do the same job and did, at 16 mm thick across the whole
    footprint — which is a lot of plastic for a shelf nobody sees, and it filled
    the chamber it was meant to furnish. The deck carries the puck; the pillars
    carry the deck; the space between them stays open, which also lets light
    from below reach a window the platform would otherwise have walled off.

    Nine pillars rather than four. The deck spans between them unsupported, and
    at four the middle span is over 30 mm — a long bridge to hang the one thing
    that has to sit level.
    """
    c = g.chambers[st.chamber]
    # Wide enough for the puck, but never wider than the chamber holding it.
    # Without the clamp a deck sized from the puck alone punched clean through
    # the great tower's side walls and out into the open air, which the render
    # showed plainly and no check asked about.
    x0 = max(-g.puck_r - 2.0, c.x0 - 1.0)
    x1 = min(g.puck_r + 2.0, c.x1 + 1.0)
    y0 = st.y0 - 1.0        # bite into the wall in front rather than kiss it
    y1 = min(st.y0 + p.riser_span, p.depth)
    top = c.floor + st.stand
    deck = top - p.deck_t

    # The deck is a frustum, not a slab: its underside is inset by its own
    # thickness so it grows out at 45 deg instead of presenting a flat plate to
    # the air below.
    out = [_taper_box((x0 + p.deck_t, x1 - p.deck_t, y0 + p.deck_t, y1 - p.deck_t),
                      (x0, x1, y0, y1), deck, top)]

    # The pillars are inset clear of the deck's underside edge, and run UP INTO
    # the deck rather than stopping against it.
    #
    # Both details are about the mesh, not the shape. Two solids that meet
    # exactly face-to-face or edge-to-edge tessellate into non-manifold edges —
    # four triangles round one edge — and a slicer rejects that even though OCC
    # calls the solid valid, because BRep topology and a watertight triangle
    # mesh are different questions. Overlapping them makes the union
    # unambiguous. This cost four non-manifold edges to learn.
    m = p.deck_t + 1.0
    ax0, ax1, ay0, ay1 = x0 + m, x1 - m, y0 + m, y1 - m
    for px in (ax0, (ax0 + ax1 - p.pillar_w) / 2, ax1 - p.pillar_w):
        for py in (ay0, (ay0 + ay1 - p.pillar_w) / 2, ay1 - p.pillar_w):
            out.append(_box(px, px + p.pillar_w, py, py + p.pillar_w,
                            c.floor, deck + p.deck_t / 2))
    return out


def build(p: P) -> Part:
    g = geometry(p)

    # Everything is constructed BEFORE the builder is entered — see the note
    # above the primitives. Inside a builder these calls would each contribute
    # a stray copy at the origin.

    # Every block runs from its tier's face back to the common rear plane, so
    # the depth map shows only where a tier is exposed above the one in front of
    # it. That is what makes it read as receding planes.
    mass = [_box(b.x0, b.x1, TIER_Y[b.tier], _back(b, p), 0.0, b.top)
            for b in BLOCKS]
    mass += [q for b in BLOCKS if b.crenel for q in _parapet(b, p)]
    for t in TOWERS:
        y = _ty(t)
        mass.append(_cyl(t.x, y, t.r, t.base, t.body_top - p.flare_h))
        mass.append(_frustum(t.x, y, t.r, t.r + p.roof_flare,
                             t.body_top - p.flare_h, t.body_top))
        mass.append(_frustum(t.x, y, t.r + p.roof_flare, p.tip_r,
                             t.body_top, t.roof_top))

    # Three separate cavities with solid bands between them. The bands are the
    # whole reason a puck lights its own windows and nobody else's.
    cavities = []
    for c in CHAMBERS:
        back = p.depth + 1.0
        corb = g.corbel[c.name]
        if corb <= 1.0:
            cavities.append(_box(c.x0, c.x1, c.y0 + p.wall, back, c.floor, c.top))
            continue
        cavities.append(_box(c.x0, c.x1, c.y0 + p.wall, back,
                             c.floor, c.top - corb))
        # The corbel: the chamber closes in at 45 deg as it nears its ceiling,
        # on both sides and at the front. NOT at the back — that edge is the
        # open face, so there is nothing there to corbel and narrowing it would
        # only make the puck harder to reach.
        cavities.append(_taper_box(
            (c.x0, c.x1, c.y0 + p.wall, back),
            (c.x0 + corb, c.x1 - corb, c.y0 + p.wall + corb, back),
            c.top - corb, c.top))
    # Tower shafts. Each meets the chamber it rises from, so a turret with no
    # puck of its own still has a path to light. A sealed turret is a dark
    # turret, which reads as a black slot rather than as a lit castle.
    for t in TOWERS:
        if not t.hollow:
            continue
        r = t.r - p.wall
        cap = t.body_top - p.wall
        cavities.append(_cyl(t.x, _ty(t), r, t.bore_from, cap - r + 0.8))
        # Finish each shaft with a cone rather than a flat lid. A tower's roof
        # is a cone outside; making it one inside too costs nothing, and turns
        # the one horizontal surface up there into a 45 deg slope.
        #
        # Truncated just short of a point. A cone apex tessellates into slivers
        # — triangles with two coincident vertices — which read as degenerate
        # edges in the mesh. The 0.8 mm it leaves behind is 2 mm2 of flat
        # ceiling, hidden at the top of a shaft, and worth it.
        cavities.append(_frustum(t.x, _ty(t), r, 0.8,
                                 cap - r + 0.8, cap))

    crenels = [cut for b in BLOCKS if b.crenel for cut in _crenel_cutters(b, p)]

    # Platforms go in AFTER hollowing: material put back into a chamber, rather
    # than material the cavity has to be shaped around.
    risers = [q for st in STATIONS if st.stand > 0
              for q in _platform(st, p, g)]

    masonry = []
    if p.brick:
        masonry += _brick_flat(p)
        for t in TOWERS:
            masonry += _stonework(t, p)

    openings = [_through(_opening_sketch(o, p), *_opening_y(o, p))
                for o in OPENINGS]
    for o in TURRET_WINDOWS:
        t = TOWER[o.tower]
        cut = _radial(_arch(0.0, o.z0, o.z1, o.w), t, t.r + 2.0)
        openings.append(Pos(t.x, _ty(t), 0) * cut.rotate(Axis.Z, o.angle))
    for o in SIDE_OPENINGS:
        b = BLOCK[o.block]
        x = b.x0 if o.side < 0 else b.x1
        openings.append(_through_side(
            _arch(o.y, o.z0, o.z1, o.w), x - p.wall - 2.0, x + p.wall + 2.0))

    with BuildPart() as bp:
        for s in mass:
            add(s)
        for s in cavities + crenels:
            add(s, mode=Mode.SUBTRACT)
        for s in risers:
            add(s)
        # Masonry before the openings: the grooves are shallow surface texture
        # and must not be allowed to nibble at a window's edge afterwards.
        if masonry:
            add(Compound(children=masonry), mode=Mode.SUBTRACT)
        for s in openings:
            add(s, mode=Mode.SUBTRACT)

    return bp.part


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------


def check(part: Part, p: P) -> None:
    g = geometry(p)

    assert len(part.solids()) == 1, (
        f"the part is {len(part.solids())} separate solids, not one — "
        f"something is floating"
    )

    # --- the load-bearing one: every lit opening is inside its puck's light ---
    # This is the criterion "every lit opening lies within its puck's emitting
    # band" compiled into code. Each input can look sensible while the space
    # between them is dark.
    for o in OPENINGS:
        if not o.lit_by or not o.assert_lit:
            continue
        stand = g.stand_z[o.lit_by]
        lo, hi = _lit_span(stand, p)
        assert o.z1 <= hi, (
            f"{o.name}'s head is at z {o.z1:.1f} but the {o.lit_by} puck, "
            f"standing at z={stand:.1f}, lights only to z {hi:.1f}, "
            f"even counting the paper"
        )
        assert o.threshold or lo <= o.z0, (
            f"{o.name}'s foot is at z {o.z0:.1f} and the light starts at "
            f"z {lo:.1f}, so its bottom {lo - o.z0:.1f} mm is dark. If that is "
            f"intended because it reaches the floor, say so with threshold=True"
        )
        if o.threshold:
            dark = max(0.0, lo - o.z0) / (o.z1 - o.z0)
            assert dark <= 0.35, (
                f"{o.name} is a threshold, but {dark:.0%} of it is dark — at "
                f"that point it is not a lit opening with a shadowed foot, it "
                f"is a hole with a lit top"
            )

    # How much of each opening the FLAME alone covers. Not asserted — the paper
    # is what is meant to carry the rest, and only a print can say whether it
    # does. Reported so the face's weakest opening is a number on the record
    # before the print rather than a surprise after it.
    worst = min(
        ((max(0.0, min(o.z1, hi) - max(o.z0, lo)) / (o.z1 - o.z0), o.name)
         for o in OPENINGS if o.lit_by and o.assert_lit
         for lo, hi in [_lit_span(g.stand_z[o.lit_by], p, paper=False)]),
        default=(1.0, "-"))
    print(f"    lit directly by the flame: {worst[1]} is the weakest opening "
          f"at {worst[0]:.0%}; the rest is the paper's job")

    # --- every opening actually opens into something -------------------------
    # A hole cut where there is no cavity behind it is not a hole. It is a blind
    # pocket: dark, and with a visible step where it bottoms out on material
    # that was never removed. It renders as a plausible opening, which is how it
    # survived a review here — the shading gave it away, not the geometry.
    for o in OPENINGS:
        t = next((t for t in TOWERS
                  if t.tier == o.tier and abs(t.x - o.x) < 1e-6), None)
        if t is not None:
            lo_z, hi_z, what = t.bore_from, t.body_top - p.wall, f"{t.name}'s shaft"
        else:
            c = g.chambers[g.stations[o.lit_by].chamber]
            lo_z, hi_z, what = c.floor, c.top, f"the {c.name} chamber"
        assert lo_z <= o.z0 and o.z1 <= hi_z, (
            f"{o.name} spans z {o.z0:.1f}–{o.z1:.1f} but {what} only runs "
            f"z {lo_z:.1f}–{hi_z:.1f}; the rest of it is a blind pocket"
        )

    # --- the walkways are walkways -------------------------------------------
    for a, b in zip(TIER_Y, TIER_Y[1:]):
        walk = (b - a) - p.parapet_d
        assert walk >= p.min_walk, (
            f"a {b - a:.1f} mm tier step leaves a {walk / FOOT:.1f} ft walk "
            f"behind the parapet (want {p.min_walk / FOOT:.0f} ft). Widen the "
            f"step or thin the parapet"
        )

    # --- the side openings, on their own axis --------------------------------
    # Same two questions as a front opening — is it lit, and does it open into
    # anything — but the second one has an extra axis here. A side window is
    # positioned along the DEPTH, so it can miss its chamber front-to-back as
    # easily as top-to-bottom, and the front elevation cannot see either.
    for o in SIDE_OPENINGS:
        c = g.chambers[g.stations[o.lit_by].chamber]
        b = BLOCK[o.block]
        lo, hi = _lit_span(g.stand_z[o.lit_by], p)
        assert lo <= o.z0 and o.z1 <= hi, (
            f"{o.name} spans z {o.z0:.1f}–{o.z1:.1f}; the {o.lit_by} puck "
            f"lights z {lo:.1f}–{hi:.1f} even counting the paper")
        assert c.floor <= o.z0 and o.z1 <= c.top, (
            f"{o.name} spans z {o.z0:.1f}–{o.z1:.1f} but the {c.name} chamber "
            f"runs z {c.floor:.1f}–{c.top:.1f}; the rest is a blind pocket")
        y_lo, y_hi = o.y - o.w / 2, o.y + o.w / 2
        assert c.y0 + p.wall <= y_lo and y_hi <= p.depth, (
            f"{o.name} sits at y {y_lo:.1f}–{y_hi:.1f} and the {c.name} "
            f"chamber runs y {c.y0 + p.wall:.1f}–{p.depth:.1f}")
        wall = abs((b.x0 if o.side < 0 else b.x1)
                   - (c.x0 if o.side < 0 else c.x1))
        assert abs(wall - p.wall) < 1e-6, (
            f"{o.name} is cut through a wall {wall:.1f} mm thick where the "
            f"chamber implies {p.wall:.1f}; the block and its chamber have "
            f"drifted apart")
        assert o.z1 <= b.top, (
            f"{o.name} reaches z {o.z1:.1f} and {o.block} stops at {b.top:.1f}")

    # --- every platform is inside the room it furnishes ----------------------
    for st in STATIONS:
        if st.stand <= 0:
            continue
        c = g.chambers[st.chamber]
        w = min(g.puck_r + 2.0, c.x1 + 1.0) - max(-g.puck_r - 2.0, c.x0 - 1.0)
        assert w >= PUCK.dia, (
            f"the {st.name} platform is {w:.1f} mm wide once clamped to the "
            f"{c.name} chamber, and the puck standing on it is {PUCK.dia:.0f}")
        assert st.y0 - 1.0 >= c.y0, (
            f"the {st.name} platform starts at y={st.y0 - 1.0:.1f}, in front of "
            f"the {c.name} chamber's outer wall at y={c.y0:.1f}")

    # --- nothing stands behind an opening ------------------------------------
    # Probes the built solid rather than reasoning about it, because the things
    # that can block a window are not the things that cut it: a corbel, a deck,
    # a pillar, a riser — anything added to a chamber after it was hollowed.
    # Corbelling the ceilings to save support material walled up half the
    # windows on this castle, and every other check still passed.
    N = 5
    for o in (*OPENINGS, *SIDE_OPENINGS):
        side = isinstance(o, SideOpening)
        if side:
            b = BLOCK[o.block]
            face = b.x0 if o.side < 0 else b.x1
            u0, u1 = o.y - o.w / 2, o.y + o.w / 2
        else:
            t = next((t for t in TOWERS
                      if t.tier == o.tier and abs(t.x - o.x) < 1e-6), None)
            face = TIER_Y[o.tier] - (t.r if t else 0.0)
            u0, u1 = o.x - o.w / 2, o.x + o.w / 2
        inward = 1.0 if (side and o.side < 0) or not side else -1.0
        seen = behind = 0
        for i in range(N):
            for j in range(N):
                u = u0 + (u1 - u0) * (i + 0.5) / N
                z = o.z0 + (o.z1 - o.z0) * (j + 0.5) / N
                at = lambda d: Vector(u, face + inward * d, z) if side is False \
                    else Vector(face + inward * d, u, z)
                if part.is_inside(at(p.wall / 2)):
                    continue                      # solid here is the profile
                seen += 1
                if part.is_inside(at(p.wall + 2.0)):
                    behind += 1
        assert seen and behind / seen <= 0.15, (
            f"{o.name}: {behind}/{seen} of its open area has material directly "
            f"behind it. It is a recess, not a window"
        )

    # --- chambers are actually separate --------------------------------------
    ordered = sorted(CHAMBERS, key=lambda c: c.floor)
    for a, b in zip(ordered, ordered[1:]):
        gap = b.floor - a.top
        assert gap >= p.wall, (
            f"only {gap:.1f} mm of solid between the {a.name} and {b.name} "
            f"chambers (need {p.wall}); they will leak into each other and "
            f"every window will light at once"
        )

    # --- a puck actually fits in each chamber --------------------------------
    need = PUCK.dia + 2 * p.fit
    for c in CHAMBERS:
        assert c.x1 - c.x0 >= need, (
            f"{c.name} is {c.x1 - c.x0:.1f} mm wide; a puck needs {need:.1f}")

    for st in STATIONS:
        c = g.chambers[st.chamber]
        assert st.y0 >= c.y0 + p.wall, (
            f"the {st.name} puck starts at y={st.y0:.1f}, in front of the "
            f"{c.name} chamber's inner face at y={c.y0 + p.wall:.1f}")
        assert p.depth - st.y0 >= need, (
            f"the {st.name} puck has {p.depth - st.y0:.1f} mm of depth behind "
            f"y={st.y0:.1f} and needs {need:.1f}")
        # The BODY must fit under the ceiling — it is 35 mm across and cannot
        # go anywhere else. The flame may stand up into a shaft above, which is
        # what lets a slender turret be lit at all.
        stand_z = c.floor + st.stand
        assert stand_z + PUCK.opaque_h <= c.top, (
            f"the {st.name} puck's base reaches z "
            f"{stand_z + PUCK.opaque_h:.1f} and the {c.name} ceiling is at "
            f"{c.top:.1f}; the base is {PUCK.dia:.0f} mm across and has nowhere "
            f"else to go"
            + (f" — its {st.stand:.1f} mm riser is what ate it" if st.stand else ""))
        if stand_z + PUCK.flame_top > c.top:
            assert c.shaft, (
                f"the {st.name} puck's flame reaches z "
                f"{stand_z + PUCK.flame_top:.1f}, above the {c.name} ceiling at "
                f"{c.top:.1f}, and no shaft is declared for it to stand up into")
            t = next(t for t in TOWERS if t.name == c.shaft)
            bore = 2 * (t.r - p.wall)
            assert bore >= PUCK.flame_dia + 2 * p.fit, (
                f"{c.shaft}'s shaft is {bore:.1f} mm across and the flame plus "
                f"clearance needs {PUCK.flame_dia + 2 * p.fit:.1f}")
            assert stand_z + PUCK.flame_top <= t.body_top - p.wall, (
                f"the flame tops out at {stand_z + PUCK.flame_top:.1f} and "
                f"{c.shaft}'s shaft is capped at {t.body_top - p.wall:.1f}")

    # Two pucks in one chamber must not foul each other. They are separated in
    # depth, not height, so this is the assertion that keeps `depth` honest: cut
    # it to save material and the eyes' puck ends up sitting on the gate's.
    for a in STATIONS:
        for b in STATIONS:
            if a.name >= b.name or a.chamber != b.chamber:
                continue
            lo_s, hi_s = sorted((a, b), key=lambda st: st.y0)
            assert hi_s.y0 - lo_s.y0 >= need, (
                f"the {lo_s.name} and {hi_s.name} pucks share the "
                f"{a.chamber} chamber but are only {hi_s.y0 - lo_s.y0:.1f} mm "
                f"apart in depth; each needs {need:.1f}")

    # --- nothing is thinner than the nozzle can draw -------------------------
    thin = [(o.name, o.w) for o in (*OPENINGS, *SIDE_OPENINGS, *TURRET_WINDOWS)
            if o.w < 4 * printer.NOZZLE]

    # The turret's windows open into its shaft, so they are bounded by it at
    # both ends — below by where the bore starts, above by where it is capped.
    for o in TURRET_WINDOWS:
        t = TOWER[o.tower]
        assert t.bore_from <= o.z0 and o.z1 <= t.body_top - p.wall, (
            f"{o.name} spans z {o.z0:.1f}–{o.z1:.1f} but {t.name}'s shaft runs "
            f"z {t.bore_from:.1f}–{t.body_top - p.wall:.1f}; the rest of it is "
            f"a blind pocket")
        assert 2 * (t.r - p.wall) >= o.w + 2 * p.wall, (
            f"{o.name} is {o.w:.1f} mm wide in a shaft only "
            f"{2 * (t.r - p.wall):.1f} mm across")
    assert not thin, f"openings narrower than the nozzle can resolve: {thin}"
    assert p.bar_w >= 3 * printer.NOZZLE, (
        f"mouth bars {p.bar_w} mm — under three extrusion widths. The drawing's "
        f"1.3 mm is what this repo has already learned not to print")
    assert min(p.merlon_w, p.embrasure_w) >= 4 * printer.NOZZLE, (
        "crenellations below the nozzle's useful resolution")
    assert p.canine_drop < p.transom_h, (
        f"the canines drop {p.canine_drop} mm into a {p.transom_h} mm gum line; "
        f"punching through divides it and the mouth stops reading as a mouth")
    assert p.transom_h - p.canine_drop >= 2 * printer.NOZZLE, (
        f"only {p.transom_h - p.canine_drop:.1f} mm of material under a canine")

    # --- it fits, standing up ------------------------------------------------
    assert g.height <= printer.BED_Z, (
        f"{g.height:.0f} mm tall, bed is {printer.BED_Z:.0f}")
    for what, dim, bed in (("wide", g.width, printer.BED_X),
                           ("deep", g.depth, printer.BED_Y)):
        assert dim <= bed - 2 * printer.BED_MARGIN, (
            f"{dim:.0f} mm {what} on a {bed:.0f} mm bed with "
            f"{printer.BED_MARGIN:.0f} mm margins")
