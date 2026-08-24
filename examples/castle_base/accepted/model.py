r"""castle_base — moated ground for `castle`, with a drawbridge that lets down.

    z
    |                        C A S T L E                     (seated 2.4 deep)
    |     ____________________________________________
    |    |                                            |
    |  __|                                            |__   island, z = island_h
    | |  |     posts  ||        ||  posts             |  |
    | |  |____________||________||____________________|  |
    | |               |  deck   |                        |   <- drawbridge, hinged
    | |___   ~~~~~~~~~|_________|~~~~~~~~~~   ______     |   <- water, z = water_z
    | |   \___________            ___________/      |    |
    +-+------------------------------------------------------ y

THE THREE FACTS THIS FILE TURNS ON
----------------------------------

1. **The castle is already printed.** It is 178 mm tall and published, so nothing
   here may require making it again. That single constraint decided the chain
   anchors (posts belonging to this part, not eyelets in the facade) and it is
   why the seat is cut to a contract rather than to a measurement.

2. **The gate is at x = +2.** The castle's whole face is built about that line
   because the castle is asymmetric on purpose. A drawbridge centred on this
   part's own centreline would sit two millimetres off its own doorway — an
   error small enough to read as a rendering artefact right up until the object
   is in your hand. Everything about the bridge is placed from `ground.GATE_X`.

3. **The seat depth is not a free choice.** The castle's gate opens onto its
   floor slab, 2.4 mm above its underside. Sink the castle by exactly that slab
   and the floor inside comes level with the ground outside, so the bridge can
   lie flush and lead somewhere. Any other seat depth puts a step in the one
   place on the whole object that a person's eye is guaranteed to travel.

Read spec.md before editing, and notes.md before changing a number.
"""
import random
from dataclasses import dataclass
from functools import lru_cache
from types import SimpleNamespace

from build123d import *

import printer
from cadkit import Params

# The ground plan. Every castle dimension used here comes from this module and
# none is repeated as a literal; `castle.check()` asserts it still describes the
# castle, so the two parts cannot drift apart without a build failing.
from assemblies import castle_ground as ground


@dataclass(frozen=True)
class P(Params):
    """The tunables."""

    # --- the ground ------------------------------------------------------
    island_h: float = 20.0
    """Ground level, above the underside of the slab.

    This is the plinth's **presence**, and it is a separate question from how
    deep the water is. At 13 mm the whole thing read as a cookie tray under a
    178 mm castle. The fix is material below the waterline, not a deeper
    trench: the side channel is only 9 mm across, so deepening it turns a moat
    into a chasm."""

    water_z: float = 10.0
    """The moat floor, so the water is `island_h - water_z` deep. Everything
    below it is the slab that ties 164 mm of plinth together and gives the thing
    the height it needs to stop looking like a tray."""

    ledge: float = 2.0
    """Ground left standing between the castle's wall and the water.

    Deliberately tiny. A moated wall meets its water directly; a lawn between
    them reads as a model of a castle rather than as a castle. The plate has no
    width to spare for one either — see the bed assertion."""

    seat_clear: float = 0.3
    """Per-side slack in the seat. The castle is a printed object with printed
    tolerances and it has to drop in without being persuaded."""

    # --- the moat --------------------------------------------------------
    moat_side: float = 8.0
    moat_front: float = 28.0
    """How far the water reaches at the flanks, and in front of the gate.

    They differ by a lot, and deliberately. **Width is spent and depth is free**:
    the castle is 134 mm across on a 170 mm plate, so the flanks get whatever is
    left after the shore and the outer bank, and it is not much. Front-to-back
    nothing is competing, so the front — which is the side anyone actually looks
    at, and the side the bridge crosses — gets a pond."""

    pond_to: float = 22.0
    pond_half: float = 46.0
    pond_taper: float = 22.0
    """Where the pond gives way to the channel. `pond_to` is how far back along
    the flanks the extra width has faded out; `pond_half` and `pond_taper` do the
    same across the width, and they are the reason the water narrows toward the
    corners instead of running the castle's full breadth at full depth.

    That taper is not styling. At the turrets the shore is already at x = ±68.5
    and the usable plate is ±85, so a pond-width moat there would put the base
    over the bed by a good centimetre. The shape the plate allows and the shape a
    real moat takes happen to agree: wide where the road comes in, pinched at the
    corners."""

    shore_wobble: float = 0.22
    """How much the outer bank wanders, as a fraction of its reach. The inner
    shore never wobbles — it is masonry against the castle's wall."""

    wobble_calm: float = 20.0
    """How far beyond the road's edge the wobble takes to come back in. Across
    the crossing itself the bank is regular, because the bridge is cut to that
    span and because a real moat would be revetted where the road meets it."""

    moat_back: float = 56.0
    moat_taper: float = 18.0
    """How far back the flank channels run, and over what distance they narrow
    to nothing rather than stopping dead.

    The water DID go all the way round for a while, and closing that ring was a
    real correction — the first version stopped it a quarter of the way down the
    castle on the mistaken reasoning that a full wrap needed a base wider than
    the plate, when width governs how *wide* the channel is and not how far back
    it runs.

    It is given up here deliberately, and traded for something worth more: the
    forecourt that gets the gate posts off the castle's face. The back of the
    castle is not a show side — its own spec says so, it is open and full of tea
    lights — so a moat there was the cheapest thing on the part to sell."""

    rim_side: float = 3.0
    rim_back: float = 5.0
    rim_front: float = 20.0
    back_margin: float = 5.0
    """Ground beyond the water. The sides are as narrow as the plate demands; the
    back is a little more generous because that is the edge you pick the whole
    thing up by. The front is wide because that is where the road is."""

    # --- the ground surface ----------------------------------------------
    terrain_amp: float = 0.7
    terrain_grain: float = 6.0
    terrain_r: float = 8.5
    """Dirt that has been piled up and loosely compacted, rather than poured.

    A flat extruded plane reads as plastic however good the shape around it is,
    and this part is mostly ground. The surface is roughed by scooping shallow
    spherical dishes out of it on a jittered grid, varying both how deep each one
    bites and how broad it is. Overlapping dishes of different depths leave the
    ground between them standing proud, so the result undulates in both
    directions even though nothing is ever added.

    **Subtractive on purpose, and this was learned the hard way.** The first
    version also buried spheres to raise mounds, which is the obvious way to get
    hills. A 13 mm sphere sunk until only its cap shows has its far side 3.5 mm
    BELOW the underside of the plinth, so the part grew lumps on the face it
    stands on; near the shore the same spheres bulged sideways into the moat
    below the waterline. Cutting can only ever take material out of the envelope.
    Adding has to be clipped to it, and the clip is the whole problem.

    A dish is upward-facing, so none of this costs an overhang.

    **Two couplings govern these three numbers**, and both were learned by
    hitting them.

    *Coverage.* For the scallops to merge instead of leaving isolated dimples,
    the bite must be at least `grain² / 8R`. That is why the minimum depth below
    is a fraction of the amplitude rather than free: turn the amplitude down on
    its own and the ground stops being continuous and starts being pocked.

    *Cost.* The kernel's work climbs superlinearly in the number of overlapping
    cut tools. Fine dirt wants roughly five hundred dishes, and a single cut with
    that many never finished — see `_terrain`, which is why they are batched.
    Cutting overlapping spheres out of one solid costs superlinearly in their
    number: at 6 mm spacing this part is 330 dishes and the build never finished
    in a workable time; at 9 mm it is a third of that. The dishes are made
    broader to compensate, which keeps the surface continuous rather than
    leaving flat plateaus between scoops.

    Set `terrain_amp` to 0 to get the flat version back — useful when iterating
    on shape, because the roughing is most of the build time."""

    # --- the approach ----------------------------------------------------
    bank_drop: float = 6.0
    road_w: float = 38.0
    road_kerb: float = 2.5
    """The ground outside the moat falls away toward the front edge of the
    plinth, and a road climbs back up it to meet the bridge.

    Without this the approach ends at a cliff: the bridge lands on a plateau
    whose outer face is a 20 mm vertical wall, so the road leads off the edge of
    the world. `bank_drop` is how far the ground falls over the length of the
    approach; the road holds a shallower slope than the bank either side of it,
    so it stands out as a causeway by `road_kerb` at the front edge and by
    nothing at all where it meets the bridge."""

    berm_crest_r: float = 18.0
    """How far the flat ground rolls over into the slope, instead of creasing.

    The approach used to read as **ice cream scooped out of a tub**, and the two
    things that fixed it were this and a placement bug — not a new texture. A
    third attempt at one, laying the slope in furrows along the contour, made it
    worse: courses of one width at one spacing read as fluting, which is a
    machined surface rather than a heaped one. The ground the flat half already
    carries, placed correctly, is what the slope wants too.

    *The bug is worth spelling out because it is invisible.* A dish is placed
    tangent to a HORIZONTAL plane at its own grid point, so on a slope its
    perpendicular bite is `r(1 − cos θ) + d cos θ` rather than `d`. The approach
    falls 8.5 mm over 13, which is 33°, and an 8.5 mm sphere set for a 0.7 mm
    bite digs 1.9 mm. Same code, same numbers, three times the crater — the whole
    error is in "tangent" meaning two different things on a level and on a slope.
    `_ground_z` answers with a normal now, and every dish is set against it.

    *And the crease was doing as much damage as the craters.* A knife leaves a
    crease; a heap of earth has a rounded crest. At 147° of included angle the
    radius has to be large to show at all — the rounding reaches only about
    `r * 0.3` along each face, which is why 18 mm buys a soft shoulder rather
    than a bevel. The road keeps its sharp crest, because it is a made causeway
    with a kerb and because its setts are cut on a flat plane."""

    # --- the gate --------------------------------------------------------
    abutment_out: float = 24.0
    abut_half: float = 30.0
    post_setback: float = 1.0
    hinge_standoff: float = 2.0
    """The forecourt: flat ground projecting forward of the castle's face, which
    the hinge is carried on and the gate posts stand on.

    It began as an 8 mm pier, sized by what a hinge needs behind it. That put the
    posts half a millimetre off the castle's front wall, where they stood
    directly in front of the facade and **cut the sightline to the mouth** — and
    the mouth is the whole design. The castle's spec is explicit that anything
    making it less face-like is the wrong change.

    So it is now a short causeway instead: the gate opens onto flat ground, you
    cross that, and the posts and the bridge are at the far end of it clear of
    the facade. `post_setback` holds the posts off the forecourt's own front edge
    so they do not crowd the water either.

    The depth this costs was bought by giving up the moat behind the castle —
    see `moat_back`.

    `hinge_standoff` holds the hinge axis clear of the forecourt's front face,
    and it exists because **without it the pin cannot be fitted at all**. The
    axis used to sit exactly on that face, so outboard of the piers the pin had
    to pass through fifteen millimetres of solid stone with no hole in it.
    Nothing in the model objected: the pin was the right size, the bores lined
    up, no two pieces interfered, and the assembled render looked perfect. It is
    only unbuildable if you try to put it together — which a render cannot do
    and an assertion now does."""

    # --- the drawbridge --------------------------------------------------
    deck_w: float = 30.0
    deck_t: float = 4.0
    landing: float = 5.0
    """The deck, and how far it overlaps the far bank. Slightly wider than the
    28 mm gate, so that raised it covers the opening rather than sitting in it."""

    knuckle_r: float = 4.0
    pin_d: float = 3.0
    pier_w: float = 6.0
    """The hinge. `knuckle_r` has to clear the pin by a real wall and has to fit
    under the deck's top surface, which is what ties it to `deck_t`."""

    hinge_clear: float = 0.4
    """Per-side slack at the hinge — between pin and deck, and between deck and
    pier. A printed hinge is one test print from either seized or sloppy, so
    this is named rather than buried."""

    # --- the chain -------------------------------------------------------
    post_w: float = 9.0
    post_d: float = 7.0
    post_h: float = 30.0
    post_gap: float = 5.0
    """The two gate posts the chains hang from. Height is set by how the chain
    looks, not by structure: a taller post makes a longer taut chain when the
    bridge is up, which is the state the chain is doing visible work in.

    They are wider than structure needs because they are **masonry** and have to
    carry coursing. A 7 mm face took a stone and a half across it, which reads as
    a striped stick rather than as a built pier."""

    stone_l: float = 3.0 * ground.FOOT
    stone_h: float = 2.0 * ground.FOOT
    mortar_w: float = 0.5
    mortar_d: float = 0.4
    """The posts are built of stone, like the castle, but **smaller stone**.

    The castle is megalithic — nine feet by four and a half — because it is a
    fortress wall seen from across a room. A gate pier is a different piece of
    building: it is small, it is close to the eye, and dressed stone at that size
    is a couple of feet. Sized in feet from the shared scale rather than in
    millimetres, so the two read as the same world; a post coursed to look right
    on its own would be a different building.

    `mortar_w` is above one extrusion so the groove is actually laid rather than
    gap-filled, and `mortar_d` is shallow because these are joints, not gaps."""

    plank_w: float = 4.2
    plank_gap: float = 0.5
    plank_d: float = 0.5
    """The deck is boards laid across the span, which is how a drawbridge is
    built: planks bearing on the two side rails, so the joints run across the
    direction you walk. Cut as grooves rather than modelled as separate boards —
    a plank a nozzle wide would be a separate part to place and glue."""

    cobble_l: float = 3.5
    cobble_w: float = 4.0
    joint_w: float = 0.5
    joint_d: float = 0.45
    """The road is paved, not dirt: setts laid in rows, staggered course to
    course.

    **Deliberately far too big.** A real sett is six to eight inches, which at
    this castle's scale is under a millimetre — well below what a 0.4 mm nozzle
    can draw a joint around. So these are about two and a half feet, and read as
    cobbles anyway. The castle made the same trade with its crenellations and
    said so out loud; where printability and the scale disagree, printability
    wins and the disagreement gets stated rather than hidden."""

    # --- the sign --------------------------------------------------------
    sign_x: float = -54.0
    sign_y: float = -51.5
    sign_yaw: float = 0.0
    """Where the sign stands, and which way it faces.

    On the front-left ground, in from the left edge and back from the crest, so
    it is read on the way in without standing between anyone and the castle's
    face — which is the mistake the gate posts already made once and which the
    forecourt exists to undo.

    **Square to the front, and that is a decision rather than a default.** It was
    turned toward the road at first, on the reasoning that a visitor should meet
    it face-on, and the yaw also swung its right-hand end clear of the water in a
    band of ground that narrows toward the moat. Both true, and both beside the
    point: the plinth is a rectangle seen straight on, and one thing in it set at
    an angle reads as knocked rather than as placed. So the board is parallel to
    the front edge and the water is cleared by moving the sign instead — which is
    what `sign_y` is doing this far forward."""

    sign_w: float = 32.0
    sign_h: float = 15.0
    sign_t: float = 3.6
    sign_stand: float = 7.0
    sign_bury: float = 7.0
    sign_post_w: float = 6.0
    sign_gap: float = 26.0
    """A board on two posts, in the National Park manner: routed letters on a
    plank, held up by a pair of square posts sunk in the ground.

    Modelled as ONE flat slab — board and posts in the same plane and the same
    thickness — so it prints face-up on the bed with no overhang anywhere and the
    lettering, which is the whole point of the object, lands on the surface that
    takes the best finish. `sign_bury` is the peg length; `sign_stand` is how far
    the board floats above the ground.

    **Scale is a deliberate lie, and the same one the cobbles tell.** At the
    castle's 1.37 mm to the foot this board is twenty-three feet across. A real
    sign would be six, and six feet of board carries lettering a quarter of a
    millimetre tall — which a 0.4 mm nozzle cannot draw and no eye could read.
    Where printability and the scale disagree, printability wins and the
    disagreement gets said out loud rather than hidden."""

    sign_fit: float = 0.25
    """Per-side slack between peg and socket. Generous enough to drop in without
    persuasion, tight enough that the sign does not lean."""

    sign_font: str = "Rockwell"
    sign_lines: tuple = ("KATHY'S", "CASTLE")
    sign_type: float = 5.4
    sign_lead: float = 2.4
    sign_relief: float = 0.0
    sign_letter_relief: float = 3 * printer.LAYER_H
    sign_border: float = 2.2
    """The lettering. A slab serif because that is what a routed park sign is cut
    in, bold because the stems have to survive a nozzle: at this type size
    Rockwell Bold's stems come out around 0.75 mm, which is not quite two
    extrusions. `check()` asserts the block fits inside its margin rather than
    trusting the number, so changing the font or the wording fails loudly instead
    of running off the end of the board.

    **`sign_relief` is 0, which means there is no raised frame** — the same idiom
    `terrain_amp` uses. It is a **two-colour decision, not a styling one**, and
    that is worth recording because the frame looked fine and was dropped anyway.

    The sign prints face-up, so a filament change at a layer boundary recolours
    everything above it. With a frame, the frame and the bottom 0.8 mm of every
    letter print *in the same layers*, and a pause is per-layer rather than
    per-region — so a single change could give frame-and-letters together, or
    letter tops with two-tone letter sides, but never letters alone. Removing the
    frame makes everything above the board face a letter, so one pause at
    z = `sign_t` yields clean lettering in the second colour and nothing else.
    Set it back above zero and the frame returns, at the cost of that.

    `sign_border` stays either way: with a frame it is where the frame sits, and
    without one it is the margin the type may not run into. A board whose
    lettering reaches its own edge reads as a mistake.

    **`sign_letter_relief` depends on whether the sign is two-colour, and that is
    the single most useful thing on this part.** It is stated in LAYERS rather
    than millimetres because that is how the finding was made and how it survives
    a change of layer height:

    | printed | letters | why |
    |---|---|---|
    | two colours | **3 layers** | the colour carries it; depth adds nothing |
    | one colour | **~12 layers** (2.4 mm) | shadow is the only thing making it read |

    A one-colour sign is legible only by the shadow the type throws. At 4 layers
    it read as an outline rather than as letters, and tripling it was what fixed
    that. **Give the letters a contrasting filament and the entire argument goes
    away** — three layers is enough, verified by stopping a print at that height
    because it already looked right.

    Three layers is better in every way *once the colour is there*: the type stops
    being a stack of thin walls, so it cannot be snapped off; the print above the
    pause is minutes rather than longer; and there is less of the second colour to
    recover from purge bleed. `check()` bounds the stem's aspect ratio at the deep
    end and says so out loud at the shallow end, because which regime you are in
    is a fact about the *print*, and nothing in the model can see it."""

    chain_hole: float = 3.0
    chain_inset: float = 4.0
    """The holes a real chain is tied through. Generous and named, because the
    chain has not been measured — see spec.md."""


PARAMS = P()

SECTION = "x"
"""Cut on x, which puts the knife a whisker off the gate's centreline and shows
the whole story in profile: seat depth, water, hinge, deck, landing."""

PRINT_ROTATION = (0, 0, 0)
"""The base is modelled in its print pose — island upward, every hollow opening
toward the nozzle. `pieces()` poses the bridge and the pin."""


# ---------------------------------------------------------------------------
# Derived geometry. One helper, read by both build() and check(), so an
# assertion can never be checking different arithmetic than the model used.
# ---------------------------------------------------------------------------

@lru_cache(maxsize=8)
def geometry(p: P) -> SimpleNamespace:
    island_half = ground.EXTENT_HALF_W + p.ledge

    # The plinth is sized to the water it has to contain, not the other way
    # round. With an irregular shoreline the extents are an OUTPUT — work them
    # out from the discs, and the bed assertion becomes a real check on the
    # wobble rather than on a number that was chosen to pass it.
    shore = _shore(p)
    base_half = max(abs(x) + r for x, _, r in shore) + p.rim_side
    base_y0 = min(y - r for _, y, r in shore) - p.rim_front
    # The back of the plinth is set by the castle now that the water stops short
    # of it, not by the water — whichever reaches further.
    base_y1 = max(max(y + r for _, y, r in shore) + p.rim_back,
                  ground.WALL_Y1 + p.back_margin)

    # The hinge axis: just clear of the forecourt's front face, at the deck's
    # underside. The height is forced — put it anywhere else and the deck either
    # cannot lie flush or cannot stand up. The standoff is what leaves the pin a
    # path in; see `hinge_standoff`.
    #
    # NOTE `_island_plan` uses `-abutment_out` bare, and must keep doing so:
    # that is the forecourt's FRONT FACE, and carrying the stone forward to meet
    # the pin is exactly what this standoff exists to prevent. The crossing
    # rectangle in `_water_plan` is the opposite case and takes the standoff,
    # because what the bridge spans is measured from the hinge.
    hinge_y = -(p.abutment_out + p.hinge_standoff)
    axis_z = p.island_h - p.deck_t

    # The deck spans the water and then some. `landing` is bearing, not overlap:
    # a bridge that arrives exactly at the bank rests on an edge.
    water_span = p.moat_front
    deck_len = water_span + p.landing
    # Where the ground starts falling away: exactly where the deck stops, so the
    # road runs up to meet the bridge with nothing flat and pointless between.
    ramp_from = hinge_y - deck_len

    # How deep the deck must be notched at the pier positions. The pier's most
    # distant corner from the axis is its front-top one, and the deck sweeps
    # only the front-upper quadrant, so that corner is the whole problem.
    pier_reach = ((p.knuckle_r) ** 2 + (p.island_h - axis_z) ** 2) ** 0.5
    notch = pier_reach + p.hinge_clear

    deck_x0 = ground.GATE_X - p.deck_w / 2
    deck_x1 = ground.GATE_X + p.deck_w / 2
    piers = ((deck_x0, deck_x0 + p.pier_w), (deck_x1 - p.pier_w, deck_x1))
    lug = (piers[0][1] + p.hinge_clear, piers[1][0] - p.hinge_clear)

    post_x = p.deck_w / 2 + p.post_gap + p.post_w / 2
    post_y = hinge_y + p.post_d / 2 + p.post_setback   # on the forecourt, clear of its lip
    eyelet_z = p.island_h + p.post_h - 4.0

    # Where a chain would be tied, at both ends of travel. The deck hole is at
    # `chain_inset` from the far corners; raising rotates it about the axis.
    hole_x = p.deck_w / 2 - p.chain_inset
    hole_y = hinge_y - (deck_len - p.chain_inset)
    hole_z = p.island_h - p.deck_t / 2
    r_along = hinge_y - hole_y            # distance from the axis, along the deck
    r_up = hole_z - axis_z                # and above it
    down = (ground.GATE_X + hole_x, hole_y, hole_z)
    up = (ground.GATE_X + hole_x, hinge_y - r_up, axis_z + r_along)
    anchor = (ground.GATE_X + post_x, post_y, eyelet_z)
    dist = lambda a, b: sum((i - j) ** 2 for i, j in zip(a, b)) ** 0.5

    return SimpleNamespace(
        island_half=island_half, base_half=base_half,
        base_y0=base_y0, base_y1=base_y1,
        width=2 * base_half, depth=base_y1 - base_y0,
        hinge_y=hinge_y, axis_z=axis_z,
        water_span=water_span, deck_len=deck_len, notch=notch, ramp_from=ramp_from,
        deck_x0=deck_x0, deck_x1=deck_x1, piers=piers, lug=lug,
        post_x=post_x, post_y=post_y, eyelet_z=eyelet_z,
        seat_depth=ground.FLOOR_T,
        castle_underside=p.island_h - ground.FLOOR_T,
        chain_up=dist(up, anchor), chain_down=dist(down, anchor),
    )


# ---------------------------------------------------------------------------
# Plan geometry — the footprint and everything measured off it.
# ---------------------------------------------------------------------------

def _footprint(grow: float = 0.0):
    """The castle's ground plan as a sketch, optionally grown outward.

    Built from the contract, not from the castle solid: the castle takes eighty
    seconds to build and a base that costs eighty seconds an iteration is a base
    nobody iterates. `castle.check()` is what keeps this honest.
    """
    wall = Pos(0, (ground.WALL_Y0 + ground.WALL_Y1) / 2) * Rectangle(
        2 * ground.WALL_HALF_W, ground.WALL_Y1 - ground.WALL_Y0)
    sx0, sx1 = ground.SURROUND_HALF
    surround = Pos((sx0 + sx1) / 2, (ground.SURROUND_Y0 + ground.WALL_Y0) / 2) * Rectangle(
        sx1 - sx0, ground.WALL_Y0 - ground.SURROUND_Y0)
    turrets = sum((Pos(sgn * ground.TURRET_X, 0) * Circle(ground.TURRET_R)
                   for sgn in (-1, 1)), Sketch())
    foot = wall + surround + turrets
    return offset(foot, amount=grow, kind=Kind.ARC) if grow else foot


def _island_plan(p: P) -> Sketch:
    """Everything that stands at ground level: the shore, plus the gate pier."""
    hinge_y = -p.abutment_out
    abutment = Pos(ground.GATE_X, (hinge_y + ground.WALL_Y0) / 2) * Rectangle(
        2 * p.abut_half, ground.WALL_Y0 - hinge_y)
    return _footprint(p.ledge) + abutment


def _wobble(u: float) -> float:
    """A smooth, closed, deterministic wiggle on the unit loop, roughly ±1.

    Three sinusoids at coprime whole-number frequencies, so it joins up with
    itself where the shoreline does. Fixed phases rather than random numbers:
    an irregular coastline is a design decision and it should come back the same
    on every build, or two renders of "the same" part cannot be compared.
    """
    from math import pi, sin
    return (0.55 * sin(2 * pi * (3 * u + 0.13))
            + 0.30 * sin(2 * pi * (7 * u + 0.61))
            + 0.15 * sin(2 * pi * (13 * u + 0.29)))


@lru_cache(maxsize=8)
def _shore(p: P) -> list[tuple[float, float, float]]:
    """Walk the island's shoreline and decide how far the water reaches at each
    step. Returns (x, y, reach) — the centres and radii of the discs whose union
    is the wet ground.

    **A moat is not an offset.** The inner edge is revetted masonry against the
    castle's wall, so it is straight and follows the building exactly — that part
    of the old shape was right. The outer edge was DUG, and the first version
    made it a constant distance from the inner one, which is why the water came
    out looking like a lap pool.

    So the outer edge is built by rolling a disc of varying radius along the
    shore. Three things vary it:

    - **How far forward the point is.** The water opens out into a pond in front
      of the gate and narrows to a channel down the flanks. That is where the
      approach is, and it is also the only direction the plate has room in.
    - **How far out to the side it is.** The bonus fades off toward the corners,
      because at the turrets the plate has nothing left to give — see the width
      assertion.
    - **A wiggle**, so the bank is not a machined curve.

    The wiggle is damped to nothing across the gate's corridor. The crossing has
    to be a known span for the bridge to be cut to, and a real one would be
    revetted there anyway.
    """
    wire = _island_plan(p).faces()[0].outer_wire()
    n = 220
    out = []
    for i in range(n):
        u = i / n
        pt = wire @ u
        x, y = float(pt.X), float(pt.Y)
        forward = min(1.0, max(0.0, (p.pond_to - y) / p.pond_to)) if p.pond_to else 0.0
        lateral = min(1.0, max(0.0, (p.pond_half - abs(x)) / p.pond_taper))
        reach = p.moat_side + (p.moat_front - p.moat_side) * forward * lateral
        # Peter out before the back of the castle rather than closing the ring.
        # Tapering the reach to nothing, rather than simply stopping, is what
        # makes the channel end as water running out into a bank instead of as
        # a trench that hits a wall.
        reach *= min(1.0, max(0.0, (p.moat_back - y) / p.moat_taper))
        if reach < 1.5:
            continue
        calm = min(1.0, max(0.0, (abs(x - ground.GATE_X) - p.road_w / 2)
                            / p.wobble_calm))
        out.append((x, y, reach * (1.0 + p.shore_wobble * calm * _wobble(u))))
    return out


@lru_cache(maxsize=8)
def _water_plan(p: P) -> Sketch:
    """The wet ground, as the union of the shoreline discs.

    A union of overlapping discs rather than a spline through offset points,
    because a union cannot self-intersect. An offset curve on a shape with
    reflex corners — and this one has four, where the gate pier meets the shore
    and where the turrets meet the wall — will happily cross itself and produce
    a face that looks fine until it is cut from something.
    """
    wet = Sketch()
    for x, y, r in _shore(p):
        wet += Pos(x, y) * Circle(r)

    # The crossing, cut square. Rolling discs leaves a scalloped bank — between
    # two neighbouring centres the union falls a few microns short of their
    # radius — and where the bridge lands that is not cosmetic: the deck's
    # rebate is cut to the nominal edge, so the scallop leaves 15-micron ridges
    # of bank standing inside the deck. The interference check found them.
    #
    # Adding the crossing as a rectangle fixes it at the root rather than by
    # opening a tolerance, and it is what the thing would be anyway: the one
    # stretch of a moat that gets revetted is the stretch the road crosses.
    # Measured from the HINGE, not from the forecourt's front face. What the
    # bridge spans is water-from-the-hinge, and the deck's landing is cut from
    # the same origin; taking this one from the face instead left the two out of
    # step by the hinge standoff and dropped the deck's tip onto two millimetres
    # of un-rebated ground. A small sliver of water therefore sits under the
    # hinge itself, which is correct — the piers stand in it.
    hinge_y = -(p.abutment_out + p.hinge_standoff)
    wet += Pos(ground.GATE_X, hinge_y - p.moat_front / 2) * Rectangle(
        p.road_w, p.moat_front)
    return wet - _island_plan(p)


def _dry(p: P, x: float, y: float, margin: float = 0.0) -> bool:
    """Is (x, y) land, with `margin` to spare before the water starts?

    Cheap because it asks the same discs the water was built from rather than
    testing against the finished face. The island is land even where a disc
    covers it — the water is discs MINUS island, and forgetting that half puts
    the whole shore ring underwater.
    """
    for cx, cy, r in _shore(p):
        if (x - cx) ** 2 + (y - cy) ** 2 < (r + margin) ** 2:
            break
    else:
        return True                       # no disc reaches here at all
    if abs(x) <= ground.WALL_HALF_W + p.ledge and \
            ground.SURROUND_Y0 - p.ledge <= y <= ground.WALL_Y1 + p.ledge:
        return True                       # on the island's main mass
    for sgn in (-1, 1):
        if (x - sgn * ground.TURRET_X) ** 2 + y ** 2 < (ground.TURRET_R + p.ledge) ** 2:
            return True                   # on a turret's plinth
    return abs(x - ground.GATE_X) <= p.abut_half and -p.abutment_out <= y <= ground.WALL_Y0


def _on_road(p: P, g, x: float, y: float, margin: float = 0.0) -> bool:
    """Is (x, y) on the made road?

    Two stretches with the water between them, and they are **different widths**.
    The forecourt is paved corner to corner — it is a courtyard in front of a
    gate, not a lane crossing it — so it is as wide as the forecourt itself. The
    ramp beyond the bridge is a road cut through a bank and is only as wide as
    the road. The bridge spans the gap between them and is decked in timber.

    Paving only the lane's width across the forecourt left dirt scoops in the
    margins either side of the gate posts, which is what a courtyard does not
    look like.
    """
    if y <= g.ramp_from + margin:
        return abs(x - ground.GATE_X) <= p.road_w / 2 + margin
    if -p.abutment_out - margin <= y <= ground.WALL_Y0 + margin:
        return abs(x - ground.GATE_X) <= p.abut_half + margin
    return False


@lru_cache(maxsize=8)
def _bank(p: P) -> SimpleNamespace:
    """The earth bank's profile through the y–z plane: flat ground, a rounded
    crest, then a straight slope to the front edge.

    The crest is an arc tangent to both — the same construction a fillet is, done
    by hand because the thing being rounded is a cut rather than an edge of the
    solid, and because the numbers are wanted afterwards. `_terrain` sets its
    dishes ON this profile, so the surface the tools are placed against and the
    surface the tools produce are the same arithmetic. Setting them against a
    flat plane while the ground underneath slopes away is precisely the bug that
    made the approach look scooped.
    """
    from math import atan2, cos, hypot, pi, sin, tan

    g = geometry(p)
    run = g.ramp_from - g.base_y0
    drop = p.bank_drop + p.road_kerb
    theta = atan2(drop, run)                       # the slope, below horizontal
    half = (pi - theta) / 2                        # half the included angle
    r = p.berm_crest_r
    reach = r / tan(half)                          # how far the arc runs along each face

    # The arc's centre, offset from the crest along the bisector of the two faces.
    bx, by = 1.0 - cos(theta), -sin(theta)
    n = hypot(bx, by)
    d = r / sin(half)
    cy = g.ramp_from + d * bx / n
    cz = p.island_h + d * by / n

    return SimpleNamespace(
        run=run, drop=drop, theta=theta, r=r,
        cy=cy, cz=cz,
        t1=g.ramp_from + reach,                    # arc meets the flat ground
        t2=g.ramp_from - reach * cos(theta),       # arc meets the straight slope
    )


def _ground_z(p: P, y: float) -> tuple[float, tuple[float, float, float]]:
    """Height and upward unit normal of the earth bank at `y`. Off the road."""
    from math import cos, sin

    g = geometry(p)
    b = _bank(p)
    if y >= b.t1:
        return p.island_h, (0.0, 0.0, 1.0)
    if y >= b.t2:
        dy = y - b.cy
        dz = (b.r ** 2 - dy ** 2) ** 0.5
        return b.cz + dz, (0.0, dy / b.r, dz / b.r)
    return (p.island_h - b.drop * (g.ramp_from - y) / b.run,
            (0.0, -sin(b.theta), cos(b.theta)))


def _crest_tool(p: P) -> Part:
    """The sliver of material to take off the crest so it rolls over instead of
    creasing: the corner between the two faces, outside the tangent arc.

    Built as a profile and extruded across the width, rather than by filleting an
    edge of the solid — the crease is broken into three pieces by the road, and a
    selector that has to find the right two of them is a selector that will find
    the wrong ones the first time anything moves.
    """
    from math import cos, sin

    g = geometry(p)
    b = _bank(p)
    corner = Polygon((b.t1, p.island_h),
                     (g.ramp_from, p.island_h),
                     (b.t2, p.island_h - b.drop * (g.ramp_from - b.t2) / b.run),
                     align=None)
    prof = corner - Pos(b.cy, b.cz) * Circle(b.r)
    return extrude(Plane.YZ * prof, amount=2 * g.base_half, both=True)


@lru_cache(maxsize=4)
def _terrain(p: P) -> list[list]:
    """Shallow dishes to scoop out of the ground, **grouped into batches that
    cannot overlap within themselves**.

    Piled dirt is neither flat nor noisy — it undulates at roughly the scale of
    a shovelful. So the dishes are broad and barely break the surface, on a
    jittered grid rather than a regular one, which is what stops the result
    reading as a pattern.

    Seeded, because an irregular ground is a design decision. A build that
    reshuffles its own dirt cannot be compared against the render before it.

    The approach slope gets the same dishes as the level ground and wants them —
    what made it read as ice cream was their depth, not their shape. See
    `_ground_z`, and the note on `berm_crest_r`.

    THE BATCHING IS THE WHOLE REASON THIS IS AFFORDABLE
    ---------------------------------------------------
    Fine dirt needs roughly five hundred dishes. Cutting them as one compound
    never finished — the kernel's cost is superlinear in the number of tools
    that overlap EACH OTHER, because it has to resolve the whole tangle before
    it can subtract any of it. Three hundred and thirty already failed at four
    minutes.

    But overlapping is a property of the grid, not of the job. Colour the grid
    with a stride wide enough that two dishes of the same colour can never touch
    — including after jitter and at the largest radius the variation allows —
    and each colour is a set of DISJOINT tools. Disjoint tools are nearly free:
    there is no tangle to resolve, just N independent bites. The stride is
    derived below rather than guessed, so the guarantee survives someone
    changing the grain or the sphere.
    """
    g = geometry(p)
    rng = random.Random(20260812)
    step = p.terrain_grain
    jitter = 0.35

    # Stride: two dishes of one colour are `stride * step` apart at best, and
    # jitter can close that by `2 * jitter * step`. They must still not touch at
    # the largest radius the variation allows.
    r_max = p.terrain_r * 1.15
    stride = 1
    while (stride - 2 * jitter) * step <= 2 * r_max:
        stride += 1

    flat: dict = {}
    ny = int((g.base_y1 - g.base_y0) / step) + 1
    nx = int(2 * g.base_half / step) + 1
    for j in range(ny):
        y = g.base_y0 + j * step
        for i in range(nx):
            x = -g.base_half + i * step
            px = x + rng.uniform(-jitter, jitter) * step
            py = y + rng.uniform(-jitter, jitter) * step
            # Where the ground actually is, and which way it faces — flat,
            # rolling over the crest, or on the slope. **Asking for the height
            # alone is what made the approach look scooped**, and it is worth
            # spelling out because the bug is invisible: a dish placed tangent to
            # a HORIZONTAL plane at its own grid point takes
            # `r(1 − cos θ) + d cos θ` out of ground that is tilted by θ, not
            # `d`. At 33° an 8.5 mm sphere set for a 0.7 mm bite digs 1.9 mm, so
            # the flat half of the part came out as loose dirt and the approach
            # came out as ice cream. Same code, same numbers, three times the
            # crater. Setting the dish against the surface normal is the fix.
            z, normal = _ground_z(p, py)
            # Skip the seat. It is roughly half the plan, it is machined flat
            # afterwards, and it ends up under the castle where nobody will ever
            # see it — so every sphere placed there is paid for twice and shows
            # up nowhere. Leaving them in put the build over five minutes.
            if abs(px) <= ground.WALL_HALF_W - 3.0 and \
                    ground.WALL_Y0 + 3.0 <= py <= ground.WALL_Y1 - 3.0:
                continue
            # Vary the bite AND the breadth. Same-sized dishes at varied depth
            # read as a regular dimple pattern; varying the sphere too is what
            # makes the ground look dug rather than stippled.
            #
            # The lower bound on the bite does two jobs. It keeps every dish
            # deep enough that neighbours still merge (see the coverage rule on
            # `terrain_amp`), and it forbids a near-tangent cut — a sphere that
            # grazes the surface by microns leaves a sliver face the kernel
            # cannot represent, and a few hundred chances at that is how the
            # solid came out formally invalid while every other check passed.
            d = rng.uniform(0.7, 1.0) * p.terrain_amp
            r = p.terrain_r * rng.uniform(0.75, 1.15)
            # Keep well clear of the road, not merely off it. A dish centred
            # just outside the corridor still reaches across the kerb — the
            # vertical step where the paved road stands proud of the bank — and
            # cutting a sphere through that wall leaves slivers along it. That
            # is what turned a 30-second build into one that ran for a quarter
            # of an hour once the bank's slope was computed correctly and those
            # dishes started biting instead of hanging in the air.
            if _on_road(p, g, px, py, margin=p.terrain_r * 0.8):
                continue                   # the road is paved, not dug
            if _dry(p, px, py, -1.5):      # dishes may nibble the bank edge
                off = r - d
                flat.setdefault((i % stride, j % stride), []).append(
                    Sphere(r).moved(Location((px + normal[0] * off,
                                              py + normal[1] * off,
                                              z + normal[2] * off))))
    return list(flat.values())


def _setts(p: P, g) -> list[list]:
    """Joint grooves for the paved road: the forecourt, and the ramp beyond the
    bridge.

    Rows across the direction of travel, with the joints within each row
    staggered half a sett course to course, so no joint runs through — the same
    rule the posts are coursed by, and the same reason.

    Returned as two batches — the joints across the road, and the joints along
    it — because within each the boxes are parallel and disjoint while between
    them they form a grid that all intersects. That is the same lesson the dirt
    taught: the kernel's cost is in the tools that overlap EACH OTHER, so a
    hundred-odd criss-crossing boxes is one tangle, and two sets of parallel
    ones is nearly free. Left as a single cut it did not finish.

    **The ramp's setts are built in the road's own plane and rotated onto it.**
    Cutting a sloping surface with vertical boxes does not work: a groove that
    is the right depth at one end of a row is through the surface at the other,
    because the ground has dropped underneath it. Building the pattern flat and
    then rotating it means every joint is the same depth by construction, which
    is a property worth having rather than a tolerance to chase.
    """
    from math import atan2, degrees, hypot

    rng = random.Random(4242)

    def rows(length: float, width: float):
        """Joint boxes for a strip `length` long and `width` across, laid out
        from the origin along -y with the paved surface at z = 0. Returns
        (across, along)."""
        half = width / 2
        across, along = [], []
        n = max(1, round(length / p.cobble_l))
        for k in range(n + 1):
            u = k * length / n
            if 0 < u < length:                       # a joint across the road
                across.append(Pos(0, -u, 0) * Box(width + 2, p.joint_w,
                                                  2 * p.joint_d))
            if k == n:
                continue
            # and the joints along it, staggered every other course
            m = max(1, round(width / p.cobble_w))
            shift = 0.5 if k % 2 else 0.0
            for j in range(m + 1):
                v = (j + shift) * width / m - half
                if abs(v) >= half - 0.4:
                    continue
                v += rng.uniform(-0.18, 0.18) * p.cobble_w
                # A shade short of the full course, so joints in neighbouring
                # rows stop before touching and the batch stays disjoint.
                along.append(Pos(v, -(u + length / n / 2), 0)
                             * Box(p.joint_w, length / n - 2 * p.joint_w,
                                   2 * p.joint_d))
        return across, along

    across, along = [], []

    # The forecourt: flat, running back from the hinge to the castle's face.
    a, b = rows(ground.WALL_Y0 + p.abutment_out, 2 * p.abut_half)
    here = Location((ground.GATE_X, ground.WALL_Y0, p.island_h))
    across += [x.moved(here) for x in a]
    along += [x.moved(here) for x in b]

    # The ramp: same pattern, rotated into the slope it lies on.
    run = g.ramp_from - g.base_y0
    theta = degrees(atan2(p.bank_drop, run))
    there = Location((ground.GATE_X, g.ramp_from, p.island_h))
    a, b = rows(hypot(run, p.bank_drop), p.road_w)
    across += [x.rotate(Axis.X, theta).moved(there) for x in a]
    along += [x.rotate(Axis.X, theta).moved(there) for x in b]
    return [across, along]


def _stone_post(p: P, cx: float, cy: float, z0: float, z1: float) -> Part:
    """A gate pier, coursed as masonry.

    Beds run round all four faces; perpends are staggered course to course so
    no vertical joint runs through, which is the difference between stonework
    and a stack of blocks. Course heights are jittered a little — the castle
    learned the same lesson, that a perfect bond reads as machine-laid tile.
    """
    post = Pos(cx, cy, (z0 + z1) / 2) * Box(p.post_w, p.post_d, z1 - z0)
    rng = random.Random(int(cx * 977) & 0xFFFF)
    mw, md = p.mortar_w, p.mortar_d
    cut = []
    z = z0 + p.stone_h
    while z < z1 - 0.4 * p.stone_h:
        ring = (Pos(cx, cy, z) * Box(p.post_w + 4, p.post_d + 4, mw)
                - Pos(cx, cy, z) * Box(p.post_w - 2 * md, p.post_d - 2 * md, mw + 0.1))
        cut.append(ring)
        top = min(z + p.stone_h, z1)
        h = top - z
        for w, along, axis in ((p.post_w, p.post_d, "x"), (p.post_d, p.post_w, "y")):
            n = max(1, round(along / p.stone_l))
            for k in range(1, n + 1) if n > 1 else ():
                t = (k / n + rng.uniform(-0.12, 0.12) - 0.5) * along
                if k == n:
                    continue              # the course ends at the corner, not a joint
                for sgn in (-1, 1):
                    if axis == "x":
                        cut.append(Pos(cx + sgn * p.post_w / 2, cy + t, z + h / 2)
                                   * Box(2 * md, mw, h))
                    else:
                        cut.append(Pos(cx + t, cy + sgn * p.post_d / 2, z + h / 2)
                                   * Box(mw, 2 * md, h))
        z += p.stone_h * rng.uniform(0.88, 1.12)
    return post - Compound(children=cut)


# ---------------------------------------------------------------------------
# The pieces.
#
# Each is cached on the parameters. Without it `_base` is built three times per
# `cad build` — once for the render, once more for each half of the interference
# check, and again by `pieces()` — which was free when the part was a slab with
# some pockets and is not free now that the ground is roughed with two hundred
# spheres.
#
# The wrappers keep the (p, g) signature the call sites use. `g` is ignored
# because it is always `geometry(p)`; taking it as an argument was only ever a
# way of not recomputing it, which is what the cache is for now.
#
# CACHED SHAPES MUST NOT BE MUTATED. build123d's `.move()` moves in place and
# returns self, so calling it on one of these would quietly relocate everyone
# else's copy too. Use `.moved()`, which copies.
# ---------------------------------------------------------------------------

@lru_cache(maxsize=4)
def _base_of(p: P) -> Part:
    g = geometry(p)
    plan = Pos(0, (g.base_y0 + g.base_y1) / 2) * Rectangle(2 * g.base_half, g.depth)
    plan = fillet(plan.vertices(), radius=6.0)
    solid = extrude(plan, amount=p.island_h)

    # --- and now everything that is taken away ---------------------------
    # Roughing stays at the END of this chain, and that is not a free choice.
    # Cutting the dirt first — while the slab is still a bare prism and the
    # boolean is at its cheapest — looks obviously right and does not work: the
    # water cut against an already-roughed slab comes back EMPTY. Against a
    # plain slab the identical cut is fine. Order the carving first, texture
    # last, and hand the kernel one complicated operation rather than a
    # sequence of them on a complicated body.
    water = extrude(_water_plan(p), amount=p.island_h - p.water_z).move(
        Location((0, 0, p.water_z)))
    solid -= water

    # --- the approach ----------------------------------------------------
    # The ground falls away in front of the moat, and a road climbs back up it
    # to the bridge. Both are the same cut at two different slopes: they pivot
    # about the SAME line, where the deck lands, so the road and the bank either
    # side of it start level with each other at the bridge and diverge going
    # forward. Pivoting about a common line rather than offsetting one surface
    # below the other is what stops a step appearing at the water's edge.
    run = g.ramp_from - g.base_y0
    front = Pos(0, (g.base_y0 + g.ramp_from) / 2, p.island_h) * Box(
        4 * g.base_half, run, 4 * p.island_h)

    def above(drop: float) -> Part:
        """Whatever stands above a slope falling `drop` over the approach."""
        return split(front,
                     bisect_by=Plane(origin=(0, g.ramp_from, p.island_h),
                                     z_dir=(0, -drop, run)),
                     keep=Keep.TOP)

    road = Pos(ground.GATE_X, (g.base_y0 + g.ramp_from) / 2,
               p.island_h) * Box(p.road_w, run, 4 * p.island_h)
    solid -= above(p.bank_drop) & road
    solid -= above(p.bank_drop + p.road_kerb) - road
    # …and roll the bank's crest over, everywhere except across the road, whose
    # crest is a kerbed causeway and stays sharp.
    solid -= _crest_tool(p) - road

    if p.terrain_amp > 0:
        for batch in _terrain(p):
            solid -= Compound(children=batch)

    for batch in _setts(p, g):
        if batch:
            solid -= Compound(children=batch)
            # NOT `clean()` here. It is the obvious repair for the coincident
            # edges a hundred-odd overlapping cuts leave behind, and on a solid
            # this size it ran for over five minutes without finishing — worse
            # than the problem. The fix is upstream: never take a near-tangent
            # bite, so the slivers are not created in the first place.

    # The gate piers, standing out of the water in front of the abutment. Boxes
    # rather than half-buried cylinders on purpose: a cylinder there is a
    # 6 mm overhang hanging over the water, and a pier is what the thing would
    # actually be built as. Added after the roughing so they keep clean faces —
    # they are dressed stone carrying a hinge, not dirt.
    for x0, x1 in g.piers:
        solid += Pos((x0 + x1) / 2, g.hinge_y - p.knuckle_r / 2,
                     (p.water_z + p.island_h) / 2) * Box(
            x1 - x0, p.knuckle_r, p.island_h - p.water_z)

    for sgn in (-1, 1):
        solid += _stone_post(p, ground.GATE_X + sgn * g.post_x, g.post_y,
                             p.island_h - 2.0, p.island_h + p.post_h)

    seat = extrude(_footprint(p.seat_clear), amount=g.seat_depth).move(
        Location((0, 0, g.castle_underside)))
    solid -= seat

    # The landing: a rebate in the far bank so the deck's end lies flush with
    # the ground rather than proud of it.
    solid -= Pos(ground.GATE_X, g.ramp_from + p.landing / 2,
                 p.island_h - p.deck_t / 2) * Box(
        p.deck_w + 2 * p.hinge_clear, p.landing, p.deck_t + 0.01)

    # Relief for the deck's lug, which is a full cylinder about the axis and so
    # reaches back into the pier. Open at the top and at the front, which is why
    # it costs no overhang.
    relief = (Pos(ground.GATE_X, g.hinge_y, g.axis_z) * Rot(0, 90, 0)
              * Cylinder(p.knuckle_r + p.hinge_clear,
                         (g.lug[1] - g.lug[0]) + 2 * p.hinge_clear))
    solid -= relief

    solid -= _pin_hole(p, g, p.pin_d + 2 * p.hinge_clear)

    # --- and open those bores at the top, so the hinge can be assembled ----
    # The pin is 30 mm long and there is only about 15 mm of clear water beyond
    # each bore before the ground closes in, so it cannot be threaded in from
    # the side at any standoff worth having. Slot the bores upward instead: push
    # the pin through the deck's lug on the bench, then drop the pair in from
    # above. Gravity holds it, the chains hold it when raised, and lifting the
    # bridge straight up is now how you take it off — useful for painting.
    for x0, x1 in g.piers:
        solid -= Pos((x0 + x1) / 2, g.hinge_y,
                     (g.axis_z + p.island_h + 1) / 2) * Box(
            (x1 - x0) + 0.02, p.pin_d + 2 * p.hinge_clear,
            p.island_h + 1 - g.axis_z)
    for sgn in (-1, 1):                               # the chain eyelets
        solid -= (Pos(ground.GATE_X + sgn * g.post_x, g.post_y, g.eyelet_z)
                  * Rot(0, 90, 0) * Cylinder(p.chain_hole / 2, p.post_w + 2))

    # The sign's post holes. Cut LAST, after the roughing: a socket dug into
    # ground that is then dished loses depth wherever a dish crosses its mouth,
    # and a peg that bottoms out on a floor 0.7 mm shallower than it was cut for
    # stands proud of the ground it is supposed to be planted in.
    solid -= _sign_place(p) * _sign_sockets(p)
    return solid


def _sign_place(p: P) -> Location:
    """Where the sign stands on the ground, as a transform.

    The sign is modelled in its own frame — origin at ground level between the
    posts, face toward −y — and placed by this one location. Both the piece and
    the sockets it drops into are built in that frame and put through the same
    transform, so a change of mind about where the sign goes cannot leave the
    holes behind.
    """
    return Pos(p.sign_x, p.sign_y, p.island_h) * Rot(0, 0, p.sign_yaw)


def _sign_posts(p: P) -> list[tuple[float, float]]:
    """The two posts, in the sign's own frame: (x, half-width)."""
    return [(sgn * p.sign_gap / 2, p.sign_post_w / 2) for sgn in (-1, 1)]


def _sign_sockets(p: P) -> Part:
    """The two post holes, in the sign's frame with the ground at z = 0."""
    # Exactly the peg's length: the socket FLOOR is what sets the sign's height,
    # and it is cut from nominal ground level after the roughing, so a dish that
    # happens to cross the socket's mouth cannot change how far the sign stands.
    depth = p.sign_bury
    return Compound(children=[
        Pos(x, 0, -depth / 2) * Box(p.sign_post_w + 2 * p.sign_fit,
                                    p.sign_t + 2 * p.sign_fit, depth)
        for x, _ in _sign_posts(p)])


def _sign_text(p: P) -> Sketch:
    """The lettering alone, centred on the board's face.

    Kept separate from the border so `check()` can measure the type on its own —
    whether it fits inside the panel, and whether a 0.4 mm nozzle can draw it.
    Measured together with the border, both questions answer themselves: the
    border is always wide enough and always fits.
    """
    n = len(p.sign_lines)
    pitch = p.sign_type * 0.72 + p.sign_lead
    art = Sketch()
    for k, line in enumerate(p.sign_lines):
        z = (n - 1 - 2 * k) * pitch / 2
        art += Pos(0, z) * Text(line, font_size=p.sign_type, font=p.sign_font,
                                font_style=FontStyle.BOLD,
                                align=(Align.CENTER, Align.CENTER))
    return art


def _sign_border(p: P) -> Sketch:
    """The routed frame alone. Only reached when `sign_relief` is above zero."""
    inner = p.sign_w - 2 * p.sign_border, p.sign_h - 2 * p.sign_border
    return (RectangleRounded(p.sign_w - 2 * 1.0, p.sign_h - 2 * 1.0, 1.5)
            - RectangleRounded(*inner, 1.0))


@lru_cache(maxsize=4)
def _sign_of(p: P) -> Part:
    """The sign: a lettered board on two posts, in its own frame.

    **One flat slab — board and posts in the same plane and the same thickness.**
    That is not laziness, it is the print pose: laid on its back the whole piece
    is a plate with raised lettering on top, so there is no overhang anywhere,
    nothing to support, and the letters — which are the entire point of the
    object — are formed on the surface a printer finishes best.
    """
    top = p.sign_stand + p.sign_h
    board = Pos(0, 0, p.sign_stand + p.sign_h / 2) * Box(p.sign_w, p.sign_t, p.sign_h)
    edges = board.edges().filter_by(Axis.Y)
    assert len(edges) == 4, (
        f"expected the board's 4 depth edges to round, found {len(edges)} — the "
        f"board is not the plain slab this selector assumes")
    board = fillet(edges, radius=2.0)

    sign = board
    for x, half in _sign_posts(p):
        sign += Pos(x, 0, (top - p.sign_bury) / 2) * Box(
            2 * half, p.sign_t, top + p.sign_bury)

    # The face, raised toward −y. Built on a plane whose normal points that way,
    # so the extrusion direction is a property of the plane rather than a sign
    # somebody has to remember to put on the amount.
    #
    # Frame and lettering are extruded SEPARATELY and by different amounts, and
    # the frame is skipped entirely at zero relief — which is the shipped state,
    # because a frame sharing layers with the letters is what stops a single
    # filament change from recolouring the type and nothing else. See
    # `sign_relief`.
    face = Plane(origin=(0, -p.sign_t / 2, p.sign_stand + p.sign_h / 2),
                 x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    if p.sign_relief > 0:
        sign += extrude(face * _sign_border(p), amount=p.sign_relief)
    return sign + extrude(face * _sign_text(p), amount=p.sign_letter_relief)


def _pin_hole(p: P, g, dia: float) -> Part:
    return (Pos(ground.GATE_X, g.hinge_y, g.axis_z) * Rot(0, 90, 0)
            * Cylinder(dia / 2, p.deck_w + 2))


@lru_cache(maxsize=4)
def _deck_of(p: P) -> Part:
    g = geometry(p)
    """The drawbridge, in its lowered pose."""
    body = Pos(ground.GATE_X, g.hinge_y - g.deck_len / 2,
               p.island_h - p.deck_t / 2) * Box(p.deck_w, g.deck_len, p.deck_t)

    lug = (Pos(ground.GATE_X, g.hinge_y, g.axis_z) * Rot(0, 90, 0)
           * Cylinder(p.knuckle_r, g.lug[1] - g.lug[0]))
    deck = body + lug

    # Notched at the pier positions, deep enough that the pier's far corner
    # never catches the deck anywhere in its travel.
    for x0, x1 in g.piers:
        deck -= Pos((x0 + x1) / 2, g.hinge_y - g.notch / 2,
                    (p.water_z + p.island_h) / 2) * Box(
            (x1 - x0) + 2 * p.hinge_clear, g.notch, p.island_h - p.water_z)

    # Boards laid across the span. Jittered a little in position and width,
    # because sawn timber is not a machined grating.
    rng = random.Random(97)
    n = max(2, round(g.deck_len / p.plank_w))
    seams = []
    for k in range(1, n):
        yy = g.hinge_y - k * g.deck_len / n + rng.uniform(-0.3, 0.3)
        seams.append(Pos(ground.GATE_X, yy, p.island_h)
                     * Box(p.deck_w + 2, p.plank_gap, 2 * p.plank_d))
    deck -= Compound(children=seams)

    deck -= _pin_hole(p, g, p.pin_d + 2 * p.hinge_clear)
    for sgn in (-1, 1):
        deck -= Pos(ground.GATE_X + sgn * (p.deck_w / 2 - p.chain_inset),
                    g.hinge_y - (g.deck_len - p.chain_inset),
                    p.island_h - p.deck_t / 2) * Cylinder(
            p.chain_hole / 2, p.deck_t + 2)
    return deck


@lru_cache(maxsize=4)
def _pin_of(p: P) -> Part:
    g = geometry(p)
    return (Pos(ground.GATE_X, g.hinge_y, g.axis_z) * Rot(0, 90, 0)
            * Cylinder(p.pin_d / 2, p.deck_w))


def build(p: P) -> Part:
    """The whole thing assembled, bridge down and sign planted. Four solids, by
    design."""
    g = geometry(p)
    return _base(p, g) + _deck(p, g) + _pin(p, g) + _sign(p, g)


def pieces(p: P) -> dict:
    """What goes on the plate, each already in its print pose.

    The base is modelled in its print pose. The pin lies down — a 3 mm rod
    standing up is a tower nobody wants to print.

    **The deck prints upside down**, and it is worth knowing why, because laying
    it down the way it sits on the castle is the obvious move and it is wrong.
    The hinge lug is a full cylinder centred on the deck's UNDERSIDE, so half of
    it hangs below that face. Lay the deck the right way up and it balances on
    that bead with its entire 830 mm2 underside floating 4 mm in the air — which
    the overhang check catches, and which no amount of looking at the assembled
    render would have shown.

    Flipped, the bead becomes a half-round sitting flat-side-down on top of the
    plate, which is self-supporting, and the deck's road surface — the face that
    shows — is against the plate, which is the best finish available.
    """
    g = geometry(p)
    deck = _deck(p, g).rotate(Axis.X, 180)
    deck = deck.move(Location((0, 0, -deck.bounding_box().min.Z)))
    # `.moved()`, not `.move()`. The pieces are cached now, and `.move()` moves
    # the shape in place and hands back the same object — so this would drop the
    # cached pin to the bed for every later caller, including the assembly the
    # renders are made from. Verified, not assumed: `.move()` returns `self`.
    pin = _pin(p, g).moved(Location((0, 0, -(g.axis_z - p.pin_d / 2))))
    # The sign lies on its back, lettering upward. Modelled in its own frame, so
    # this is the un-placed piece rotated flat — never the placed one, whose yaw
    # would put it on the plate at an angle for no reason.
    sign = _sign_of(p).rotate(Axis.X, -90)
    sign = sign.moved(Location((0, 0, -sign.bounding_box().min.Z)))
    return {"base": _base(p, g), "deck": deck, "pin": pin, "sign": sign}


def check(part: Part, p: P) -> None:
    g = geometry(p)

    # --- three objects that touch and never interpenetrate ----------------
    # Counting solids does not work here and it is worth saying why: lowered,
    # the deck RESTS on its landing, so base and deck meet on a face and fuse
    # into one solid in the model. That is the correct physical answer and a
    # useless assertion.
    #
    # What actually has to be true is that no two pieces occupy the same space.
    # Volume of intersection catches every way this part can be got wrong at
    # once — lug fouling its relief, pier catching the notch, pin too fat —
    # where a count catches none of them. Faces in contact have zero volume, so
    # resting is free and interference is not.
    for name, piece in pieces(p).items():
        assert len(piece.solids()) == 1, (
            f"piece {name!r} is {len(piece.solids())} solids — something on it "
            f"is floating and will print as loose debris")

    base, deck, pin = _base(p, g), _deck(p, g), _pin(p, g)
    sign = _sign(p, g)
    solids = {"base": base, "deck": deck, "pin": pin, "sign": sign}
    for a, b in (("deck", "base"), ("pin", "base"), ("pin", "deck"),
                 ("sign", "base")):
        clash = solids[a] & solids[b]
        vol = clash.volume if clash is not None else 0.0
        assert vol < 1e-6, (
            f"the {a} and the {b} share {vol:.3f} mm3 of space — they cannot "
            f"both be printed and then assembled")

    # --- does it do its job? ---------------------------------------------
    # The one that matters most: the deck lands level with the floor the gate
    # opens onto. Derived from the contract, not from a chosen number.
    gate_floor_z = g.castle_underside + ground.FLOOR_T
    assert abs(gate_floor_z - p.island_h) < 1e-9, (
        f"the gate's threshold sits at z {gate_floor_z:.2f} and the ground "
        f"outside is at z {p.island_h:.2f}. The seat must be sunk by exactly "
        f"the castle's floor slab or the bridge leads to a step")

    assert g.deck_len > g.water_span, (
        f"the deck is {g.deck_len:.1f} mm and the water is {g.water_span:.1f} — "
        f"it does not reach the far bank")
    assert p.landing >= 3 * printer.NOZZLE, (
        f"only {p.landing:.1f} mm of the deck rests on the bank")

    # Centred on the GATE, not on the part. This is the assertion that stops
    # the drawbridge quietly drifting to the castle's centreline.
    assert abs((g.deck_x0 + g.deck_x1) / 2 - ground.GATE_X) < 1e-9, (
        "the deck is not centred on the gate")
    assert p.deck_w >= ground.GATE_W, (
        f"a {p.deck_w:.0f} mm deck cannot cover a {ground.GATE_W:.0f} mm gate — "
        f"raised, it would sit inside the opening instead of closing it")

    # Raised, the deck stands across the opening rather than short of it.
    raised_top = g.axis_z + g.deck_len
    gate_head = g.castle_underside + ground.GATE_Z1
    covered = (raised_top - g.castle_underside - ground.GATE_Z0) / (
        ground.GATE_Z1 - ground.GATE_Z0)
    assert covered >= 0.5, (
        f"raised, the deck reaches z {raised_top:.1f} against a gate head at "
        f"z {gate_head:.1f} — it covers only {covered:.0%} of the opening")

    # The hinge clears itself at both ends of travel. `notch` is the whole
    # question: the pier's far corner is what a rotating deck catches on.
    assert g.notch > ((p.knuckle_r) ** 2 + (p.island_h - g.axis_z) ** 2) ** 0.5, (
        f"the deck is notched {g.notch:.2f} mm but the pier reaches "
        f"{((p.knuckle_r) ** 2 + (p.island_h - g.axis_z) ** 2) ** 0.5:.2f} mm "
        f"from the hinge axis — the bridge will jam part-way up")
    # --- the hinge can actually be ASSEMBLED -------------------------------
    # Every other hinge check asks whether the assembled thing is right. This
    # one asks whether it can be assembled at all, which is a different question
    # and the one that got missed. The axis sat exactly on the forecourt's front
    # face, so the pin would have had to be threaded through fifteen millimetres
    # of solid stone: correct in every static sense, and impossible to build.
    #
    # Standing the hinge off the face was not enough — the pin is 30 mm long and
    # the water beside each bore runs out after about 15. So the bores are
    # slotted upward and the test is that nothing roofs them over.
    top = p.island_h + 2.0
    drop = Pos(ground.GATE_X, g.hinge_y, (g.axis_z + top) / 2) * Box(
        p.deck_w, p.pin_d + 2 * p.hinge_clear, top - g.axis_z)
    blocked = base & drop
    vol = blocked.volume if blocked is not None and blocked.solids() else 0.0
    assert vol < 1e-6, (
        f"the hinge cannot be assembled: {vol:.1f} mm3 of the base roofs over "
        f"the pin's bore, so neither the pin nor the deck can be dropped in and "
        f"there is not enough clear run beside the part to thread the pin in "
        f"from the side either")

    assert p.knuckle_r >= p.pin_d / 2 + 2 * printer.NOZZLE, (
        f"only {p.knuckle_r - p.pin_d / 2:.2f} mm of material around the pin")
    assert g.axis_z + p.knuckle_r <= p.island_h + 1e-9, (
        "the lug stands proud of the ground — the deck cannot lie flush")
    assert g.axis_z - p.knuckle_r > p.water_z, (
        "the hinge lug dips into the water")

    # Both ends of the chain exist, and one length reaches both.
    assert p.chain_hole >= 2.5 * printer.NOZZLE, (
        f"a {p.chain_hole:.1f} mm hole is not a hole a chain goes through")
    assert g.chain_up >= 8.0, (
        f"the chain is only {g.chain_up:.1f} mm taut with the bridge up — too "
        f"short to read as a chain. Raise the posts or move them outward")
    assert g.chain_down > g.chain_up, (
        "the chain would have to get shorter to lower the bridge")

    # --- the sign ---------------------------------------------------------
    # It has to be READABLE, and it has to stand on ground that exists. Those are
    # the two ways a lettered board planted in a landscape fails, and neither is
    # visible in a plan view.
    art = _sign_text(p)
    bb = art.bounding_box()
    inner_w = p.sign_w - 2 * p.sign_border
    assert bb.size.X <= inner_w - 1.0, (
        f"the lettering is {bb.size.X:.1f} mm across a {inner_w:.1f} mm panel — "
        f"{p.sign_lines!r} in {p.sign_font} at {p.sign_type} runs into the "
        f"border. Shorten the wording, shrink the type, or widen the board")
    assert bb.size.Y <= p.sign_h - 2 * p.sign_border + 1e-6, (
        f"the lettering stands {bb.size.Y:.1f} mm tall on a "
        f"{p.sign_h - 2 * p.sign_border:.1f} mm panel")

    # Can a nozzle draw it? Measured as **twice the area over the perimeter**,
    # which for a shape made of strokes is its mean stroke width — the number the
    # extruder actually has to fill.
    #
    # ARTWORK.md prefers simulating the nozzle to reasoning about it, and warns
    # that area-based metrics mislead. Both hold for a traced silhouette and
    # neither applies here. The morphological opening it recommends is a 2D
    # offset, and eroding a glyph raises "Unexpected result type" the moment a
    # counter closes — which is exactly when the answer is interesting. And the
    # warning is about tapers: type has none, it is strokes of near-constant
    # width, so the mean is the measurement rather than a proxy for it.
    stroke = 2 * art.area / sum(e.length for f in art.faces() for e in f.edges())
    assert stroke >= 1.5 * printer.NOZZLE, (
        f"the lettering averages {stroke:.2f} mm of stroke — under one and a "
        f"half extrusions of a {printer.NOZZLE} mm nozzle, so "
        f"{p.sign_font} at {p.sign_type} mm will come out broken and patchy")

    # Raised type is legible by the shadow it throws, so the relief is doing real
    # work — but every millimetre of it makes each stem a taller, thinner wall.
    # Asserted as the ratio rather than as a height, because it is the ratio that
    # decides whether a letter snaps off when the sign is handled.
    aspect = p.sign_letter_relief / stroke
    assert aspect <= 4.0, (
        f"the letters stand {p.sign_letter_relief:.1f} mm off a {stroke:.2f} mm "
        f"stroke — {aspect:.1f} to 1, tall enough that the thin parts of a glyph "
        f"are a wall waiting to be knocked off. Raise the type size with it")
    assert p.sign_letter_relief >= p.sign_relief, (
        "the lettering is set shallower than its own border, so the frame will "
        "shade it out — the type is meant to be the proud thing on the board")
    assert p.sign_relief + p.sign_letter_relief < p.sign_t, (
        f"the raised work is deeper than the {p.sign_t:.1f} mm board it stands "
        f"on, which makes the sign mostly lettering")

    # The colour change lands ON a layer boundary. The sign prints face-up and is
    # meant to be paused at the board's face so the lettering comes out in a
    # second filament; if the board's thickness is not a whole number of layers,
    # the slicer's nearest boundary falls somewhere inside the type or somewhere
    # below it, and the colour edge comes out ragged for a reason nobody can see
    # in the model. It is the kind of thing that is obvious once and invisible
    # forever after, so it is asserted rather than written down.
    layers = p.sign_t / printer.LAYER_H
    assert abs(layers - round(layers)) < 1e-6, (
        f"the board is {p.sign_t:.2f} mm — {layers:.2f} layers at "
        f"{printer.LAYER_H} mm, so the filament change at its face would land "
        f"mid-layer and the colour edge would be ragged")
    if p.sign_relief > 0:
        # Not fatal, and not a decision this file gets to make — but it means the
        # advertised trick does not work, so it says so.
        print(f"  note: the sign has a {p.sign_relief:.1f} mm frame, which shares "
              f"layers with the base of every letter. One filament change cannot "
              f"recolour the type alone — see `sign_relief`.")

    # Which regime the lettering is cut for is a fact about the PRINT, not about
    # the model, so it cannot be asserted — but it can be said, because getting it
    # wrong gives an unreadable sign that every check passes.
    letter_layers = p.sign_letter_relief / printer.LAYER_H
    if letter_layers < 8:
        print(f"  note: the lettering is {letter_layers:.0f} layers deep, which "
              f"assumes a CONTRASTING filament above the pause at z "
              f"{p.sign_t:.1f}. Printed in one colour it wants about 12 — shadow "
              f"is the only thing that makes a one-colour sign read.")

    # Both posts stand on level, dry ground, clear of the road and of the crest.
    # A sign whose leg lands on the bank rolls over, and one whose leg lands in
    # the moat is a sign in the moat.
    b = _bank(p)
    place = _sign_place(p)
    for x, _ in _sign_posts(p):
        pt = place * Location((x, 0, 0))
        px, py = pt.position.X, pt.position.Y
        assert _dry(p, px, py, 2.0), (
            f"a sign post at ({px:.1f}, {py:.1f}) stands in the water, or within "
            f"2 mm of its edge")
        assert py >= b.t1, (
            f"a sign post at y {py:.1f} is on the bank's crest, which starts at "
            f"y {b.t1:.1f} — its hole would be cut into sloping ground")
        assert not _on_road(p, g, px, py, margin=1.0), (
            f"a sign post at ({px:.1f}, {py:.1f}) stands in the road")
        assert abs(px) + p.sign_post_w / 2 <= g.base_half and py <= g.base_y1, (
            "a sign post is off the edge of the plinth")

    # The peg fits its hole, and the hole is not so slack the sign leans.
    assert p.sign_fit >= 0.15, "the sign's pegs are a press fit and will not go in"
    assert p.sign_fit <= 0.4, (
        f"{2 * p.sign_fit:.1f} mm of slack in a {p.sign_t:.1f} mm socket — the "
        f"sign will lean")
    assert p.sign_bury >= 3 * p.sign_fit + 4.0, (
        f"only {p.sign_bury:.1f} mm of peg in the ground — with "
        f"{p.sign_fit:.2f} mm of slack per side that is a sign that wobbles")
    assert p.sign_t >= 4 * printer.NOZZLE and p.sign_post_w >= 4 * printer.NOZZLE, (
        "the sign's posts are too slender to print")

    # And it does not become the thing you see instead of the castle. The gate
    # posts already have a ceiling for that reason; this one keeps the sign
    # under them, because it is further from the eye and smaller in the world.
    sign_top = p.island_h + p.sign_stand + p.sign_h
    assert sign_top <= p.island_h + p.post_h, (
        f"the sign tops out at z {sign_top:.1f}, above the gate posts at "
        f"z {p.island_h + p.post_h:.1f} — it would be the tallest thing in front "
        f"of the castle")

    # The moat is water, not a groove — asserted at the castle's own scale
    # rather than against a millimetre figure or an aspect ratio someone liked.
    # A moat has a size in the world; the only honest way to choose one is to
    # convert it, which is the argument that put a foot in the castle.
    deep_ft = (p.island_h - p.water_z) / ground.FOOT
    wide_ft = g.water_span / ground.FOOT
    assert deep_ft >= 4.0, (
        f"the water is {deep_ft:.1f} feet deep — that is a ditch you wade")
    assert wide_ft >= 12.0, (
        f"the water is {wide_ft:.1f} feet across at the gate. Under about "
        f"twelve and a fit person clears it standing, which is not a moat — "
        f"and at this size it stops reading as one too")

    # It cannot tip forward. Asserted as the geometric fact the argument rests
    # on rather than by weighing anything: the base's footprint strictly
    # contains the castle's on every side, and all the mass this part adds sits
    # inside that footprint. So the support polygon grew and nothing moved
    # outside it — whatever the castle's balance was standing alone, and it is
    # an accepted criterion that it was fine, it is strictly better now.
    # Computing a real centre of mass would need the castle's, which would mean
    # a 190-second build to check a conclusion that already follows.
    margins = {"front": ground.EXTENT_Y0 - g.base_y0,
               "back": g.base_y1 - ground.EXTENT_Y1,
               "side": g.base_half - ground.EXTENT_HALF_W}
    for where, m in margins.items():
        assert m > 0, f"the base does not reach past the castle at the {where}"
    assert margins["front"] > margins["back"], (
        f"the ground reaches {margins['front']:.0f} mm forward of the castle and "
        f"{margins['back']:.0f} mm behind it — a facade with an open back carries "
        f"its mass forward, so the front is the margin that has to be the larger")

    # The plinth never leaves its own envelope. The ground is roughed by cutting
    # only, so this should be free — and it is exactly the assertion that would
    # have caught the version that raised mounds by burying spheres, which put
    # lumps 3.5 mm BELOW the face the whole thing stands on. A part that does
    # not sit flat still builds, still passes validity, and still renders as a
    # perfectly good plinth from every angle except the one nobody looks at.
    bb = base.bounding_box()
    assert abs(bb.min.Z) < 1e-6, (
        f"the base's underside is at z {bb.min.Z:.3f}, not 0 — something has "
        f"grown through the face it stands on and it will rock on the bed")
    assert bb.max.X <= g.base_half + 1e-3 and bb.min.X >= -g.base_half - 1e-3, (
        "the base is wider than the plan it was sized from")
    assert bb.min.Y >= g.base_y0 - 1e-3 and bb.max.Y <= g.base_y1 + 1e-3, (
        "the base is deeper than the plan it was sized from")

    # --- is it built correctly? ------------------------------------------
    # The shore is `ledge` wide until the seat is cut into it, and then it is
    # narrower by the seat clearance. That difference is the thinnest material
    # in the whole part and it stands 9 mm out of the water at the turrets,
    # which is exactly the sort of wall that gets checked against the wrong
    # number: `ledge` passes any test you like while the thing that actually
    # gets printed is 1.2 mm.
    shore = p.ledge - p.seat_clear
    assert shore >= 3 * printer.NOZZLE, (
        f"the shore is {p.ledge:.1f} mm on paper but {shore:.2f} mm once the "
        f"seat is cut — under three extrusions, standing "
        f"{p.island_h - p.water_z:.0f} mm out of the water")
    assert p.post_w >= 4 * printer.NOZZLE and p.post_d >= 4 * printer.NOZZLE, (
        "the gate posts are too slender to print")

    # A gate post that stands taller than the arch it flanks stops being a gate
    # post and becomes a pair of antennae in front of the castle's face. The
    # gate head comes from the contract, so this tracks the castle rather than a
    # number chosen by eye.
    post_top = p.island_h + p.post_h
    gate_head_z = g.castle_underside + ground.GATE_Z1
    assert post_top <= gate_head_z, (
        f"the posts top out at z {post_top:.1f}, above the gate's head at "
        f"z {gate_head_z:.1f} — they would stand over the opening they flank")
    # And the consequence of that ceiling, which is not obvious and is the
    # reason the chain geometry is what it is: the raised deck reaches nearly to
    # the gate head too, so the eyelet can never get far above the bridge's tip
    # and the chain is close to horizontal at full lift. The honest answer is
    # that a real chain will stop the bridge short of vertical, which is what a
    # drawbridge looks like anyway. Recorded rather than designed around,
    # because the chain has not been measured.
    assert g.eyelet_z < g.axis_z + g.deck_len + 12.0, (
        "the eyelet clears the raised deck by more than the gate allows — "
        "check this against the post-height ceiling above")
    assert p.rim_side >= 2 * printer.NOZZLE, (
        f"the outer bank is {p.rim_side:.1f} mm — under two extrusions")

    # It fits, with margin. This part is within a few millimetres of the plate
    # and that is close enough to want stating rather than discovering.
    usable_x, usable_y, _ = printer.usable_bed()
    assert g.width <= usable_x, (
        f"{g.width:.0f} mm wide on a {usable_x:.0f} mm usable plate")
    assert g.depth <= usable_y, (
        f"{g.depth:.0f} mm deep on a {usable_y:.0f} mm usable plate")
    assert usable_x - g.width >= 5.0, (
        f"only {usable_x - g.width:.1f} mm of plate to spare across the width — "
        f"the castle is 134 mm across the ground and that is what sets this")


def _solids_only(shape) -> Part:
    """Throw away anything a boolean left behind that is not a solid.

    Cutting a compound of tools can return a compound carrying the odd stray
    face or edge alongside the body — harmless in itself, but the NEXT
    subtraction refuses a compound whose children are of mixed dimension
    ("Dimensions of objects to subtract from are inconsistent"). It never showed
    while the roughing was the last cut in the chain; moving it to the front
    made it the first thing to hand its result to another boolean.
    """
    sols = shape.solids()
    if not sols:
        raise ValueError("a boolean left nothing solid behind")
    out = sols[0]
    for extra in sols[1:]:
        out = out.fuse(extra)
    # Fused rather than gathered into `Compound(children=...)`, which builds a
    # lazy assembly whose `wrapped` is not populated and trips an assertion the
    # moment anything asks for the actual shape.
    return Part(out.wrapped)


def _base(p: P, g=None) -> Part:
    return _base_of(p)


def _deck(p: P, g=None) -> Part:
    return _deck_of(p)


def _pin(p: P, g=None) -> Part:
    return _pin_of(p)


def _sign(p: P, g=None) -> Part:
    """The sign, standing where it stands. `.moved()`, via a fresh location —
    the piece is cached and `.move()` would relocate everyone else's copy."""
    return _sign_place(p) * _sign_of(p)
