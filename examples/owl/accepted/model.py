r"""owl — a creepy owl that stares at you, on a printed branch.

        /\        /\        two ear tufts
       (  o    o   )        eyes: apertures, level with the puck's LED
        \    v    /         beak: aperture, level with its OPAQUE BASE
         \______/
      ===<        >===      branch: a separate piece, slot-and-tab, dry
              |
           [ shelf ]        behind the head, holding the tea light

Two pieces. The **plate** is the owl cut to its own outline, printed lying flat
on the bed, with a shelf standing off its back. The **branch** is a perch with a
straight slot; the owl's tab drops into it and is held by its own weight.

THE NUMBER THIS PART TURNS ON
-----------------------------
`shelf_z` is **derived, never chosen**. The puck is opaque to 15 mm and emits
from 15 to 25 mm above whatever it stands on, so putting the middle of that band
at the eyes' centre lights the eyes and — because the beak sits directly below
them — leaves the beak behind the opaque base. One number does both jobs.

The optimum is sharp: 4 mm either way drops eye coverage from 92% to about 60%.
A hand-typed `shelf_z = 74` would look perfectly reasonable and be quietly wrong
the moment the owl is rescaled or the artwork re-traced. `check()` asserts the
coverage rather than the number.

WHY THE FEATHERED OUTLINE IS FREE
---------------------------------
The plate prints **flat**, so the artwork's plane is horizontal during printing.
Every layer-support rule that governs the lantern motifs — no downward spikes,
no stalactites, prefer a single peak — describes a motif whose plane stands
vertical. None of them can fail here. That is why this outline keeps all its
feather lobes and both ear tufts where a lantern motif would have had to give
them up. Do not import those constraints into a flat part.
"""
from dataclasses import dataclass
from types import SimpleNamespace

from build123d import *

import printer
from cadkit import Params
from projects.halloween_lantern.shared import PUCK

from owl_outline import (BEAK, BODY, BRANCH, BRANCH_TOP_AT_SLOT, EYE_L, EYE_R,
                         OWL_ASPECT, TAB_HALF)


@dataclass(frozen=True)
class P(Params):
    owl_h: float = 140.0
    """Height of the owl alone, base of the tab to the ear tips. Every other
    dimension that comes from the artwork is a fraction of this."""

    plate_t: float = 3.2
    """Plate thickness. Eight layers at 0.2, and enough to be opaque in black.

    Thicker would make each aperture a tunnel that vignettes the eye when seen
    off-axis; thinner starts to let light through the plate itself, which is the
    effect `castle` found by accident and which would ruin a design whose whole
    point is that only the apertures glow."""

    shelf_d: float = 44.0
    """How far the shelf reaches behind the plate. The puck is 35 across, so
    this leaves a lip in front of it and clearance behind."""

    shelf_t: float = 2.4
    lip_h: float = 3.0
    """A raised rim around the shelf's free edges, so a knocked ornament does
    not post its tea light onto the floor."""

    brace_w: float = 1.6
    """Gussets under the shelf, thickness. A tea light weighs about 17 g, so
    these resist almost nothing — they exist to stop the shelf/plate joint being
    a hinge, not to carry a load. 1.6 mm is four extrusion widths."""

    brace_drop: float = 0.42
    """How far the gussets reach down the plate, as a fraction of shelf depth."""

    branch_d: float = 24.0
    """Depth of the branch itself. A branch, not a plinth: extruding it deep
    enough to counterweight the puck made a 46 mm slab weighing more than the
    owl it holds. The counterweighting is the feet's job now."""

    base_trim: float = 0.5
    """How much is shaved off the branch's underside to make a true flat base.

    The traced outline wanders by about 0.2 mm along its length — noise from the
    artwork, not design — so the branch's "bottom" is a wobbly curve rather than
    a plane, and an ornament resting on it touches at whichever few points
    happen to be lowest. Trimming to a plane gives it a real footprint, and
    gives the feet something to be flush WITH."""

    foot_w: float = 9.0
    foot_h: float = 4.0
    foot_margin: float = 6.0
    """Clear distance between a foot's outer edge and the edge of the branch's
    ground-contact patch.

    The feet's x position is DERIVED from that patch, not chosen. The branch
    only touches the ground over part of its length — the forks lift off — and a
    foot placed by eye at x = 38 hung 2.5 mm outside it, sticking out past the
    branch's own footprint. Where the contact ends is a property of the traced
    outline, so it has to be measured from the outline."""

    slot_front: float = 0.45
    """Where the slot sits within the branch's depth, front to back. Deliberately
    forward of centre: the rearward mass is the puck, so more branch belongs
    behind the owl than in front of it."""

    slot_clear: float = 0.35
    """Clearance per side between tab and slot. NOT an interference fit: a
    tight slot in PLA either refuses to assemble or splits the branch.

    This value was chosen as a *glue gap*, and the printed part then turned out
    not to need glue — the plate seats on this clearance and its own weight
    holds it. Right number, dead premise. Do not tighten it to add grip: the
    seat already works, and the only thing a snugger fit buys is the split this
    clearance exists to prevent."""

    tab_h: float = 8.0
    """How far the tab reaches down into the branch."""

    tip_margin: float = 10.0
    """How far the branch must reach behind the puck's centre of mass. Stability
    is satisfied a long way before this — the combined centre of mass sits only
    about 9 mm behind the plate — so this is margin against a nudge, not against
    gravity."""

    beak: bool = True
    """Cut the beak. A filled beak is invisible — black plastic on a black body —
    so it reads only as a hole. Kept as a switch because it is the one aperture
    whose brightness is a matter of taste."""

    sleeve_bore: float = 36.0
    """Square bore of the puck's sleeve. MEASURED, not chosen — settled by
    `tealight_sleeve`'s three-bore sweep, where the tightest of the
    three was the one that went on by hand and held. Do not re-derive it here;
    if it ever moves, it moves there first."""

    sleeve_wall: float = printer.MIN_WALL
    """Thinnest the nozzle draws, which is also exactly two perimeters, so the
    wall carries no sparse infill. Same reasoning as `tealight_sleeve`."""

    sleeve_len: float = PUCK.flame_top
    """Length of the sleeve, along the puck's axis — the WHOLE puck, flame and
    all, where `tealight_sleeve` stops at the opaque base.

    That is a deliberate contradiction of that part's central rule, and the
    reason it is right here is that the two parts are doing opposite jobs. A
    sleeve on an UPRIGHT puck that reached past the base would shroud the flame
    from the thing being lit. This puck lies on its SIDE, aimed forward at the
    owl's back, so the sleeve's walls are beside the flame rather than over it:
    they block the light going sideways and pass all of the light going
    forward. Shrouding is the point, not the failure.

    The value is not a coincidence either. Charles printed this by scaling the
    15 mm sleeve 200% in Z, and `2 * opaque_h` happens to equal `flame_top` on
    this puck — so "double tall" and "as long as the whole puck" are the same
    number, arrived at from different directions. It is written as the second of
    those because that is the one that stays true if the puck is ever
    re-measured."""


PARAMS = P()

SECTION = "x"
"""Cut lengthwise. The shelf, its gussets and the slot are all in the depth
direction, and a front elevation cannot show any of them."""

PRINT_ROTATION = (0, 0, 0)
"""The assembly stands as modelled. Each piece carries its own print pose in
`pieces()`, which is what actually goes to the plate."""


def geometry(p: P) -> SimpleNamespace:
    """Everything derived, in one place, read by build() and check() alike."""
    h = p.owl_h
    eye_lo, eye_hi = _band(EYE_L, EYE_R, h)

    # The whole design in one line: centre the puck's emitting band on the eyes.
    #
    # On the midpoint of their vertical SPAN, not on `EYE_CENTRE` — which is the
    # traced centroid and sits 1.2 mm lower, because the eyes are angled
    # crescents with more area at their outer ends. Centroid is the natural
    # thing to reach for and it costs 11 points of coverage; the quantity being
    # optimised is how much of the eyes' HEIGHT the LED band covers, so the
    # height is what the derivation must use. `check()` caught this.
    eye_z = (eye_lo + eye_hi) / 2
    shelf_z = eye_z - (PUCK.opaque_h + PUCK.emit_top) / 2

    return SimpleNamespace(
        h=h,
        width=OWL_ASPECT * h,
        eye_z=eye_z,
        shelf_z=shelf_z,
        led_lo=shelf_z + PUCK.opaque_h,
        led_hi=shelf_z + PUCK.emit_top,
        opaque_hi=shelf_z + PUCK.opaque_h,
        # The branch's top UNDER THE OWL, which is 4 mm BELOW the owl's own
        # base: the artwork draws the owl floating, with the raised forks
        # flanking it. So the owl grows a tab downward to reach the slot, rather
        # than the branch being lifted to meet the owl — which would drag the
        # forks 12 mm up the owl's chest and change the composition.
        slot_top=BRANCH_TOP_AT_SLOT * h,
        slot_floor=BRANCH_TOP_AT_SLOT * h - p.tab_h,
        tab_w=2 * TAB_HALF * h,
        branch_front=-p.branch_d * p.slot_front + p.plate_t / 2,
        branch_bottom=min(y for _, y in BRANCH) * h,
        # The one ground plane everything on this piece sits on.
        ground_z=min(y for _, y in BRANCH) * h + p.base_trim,
        contact_half=_contact_half(p, h),
        foot_x=_contact_half(p, h) - p.foot_margin - p.foot_w / 2,
        foot_back=p.plate_t + PUCK.dia / 2 + p.tip_margin + 4.0,
        tab_h=p.tab_h,
        seat_z=0.0,               # the owl sits exactly where the artwork put it
        puck_centre=p.plate_t + PUCK.dia / 2,   # where the puck's mass acts
        # --- the sleeve, and the surface it stands on ---------------------
        # `floor_top`, NOT `shelf_z`. shelf_z is where the shelf's floor slab
        # BEGINS; the puck rests on top of that slab, `shelf_t` higher up. The
        # LED-band derivation above measures from shelf_z and so is 2.4 mm out
        # for an upright puck — see notes.md. It does not matter for the puck
        # this part actually uses, which lies down, but anything positioned on
        # the shelf must use this and not that.
        floor_top=shelf_z + p.shelf_t,
        sleeve_across=p.sleeve_bore + 2 * p.sleeve_wall,
        # Lying on its side the sleeve's across-flats becomes its HEIGHT, and
        # the puck sits centred in the bore, so the flame axis is half the
        # across-flats above the shelf floor — 1.3 mm higher than a bare puck
        # resting on its own cylinder. That is the sleeve's one geometric cost
        # and it is asserted against the eye band rather than assumed small.
        sleeve_axis_z=shelf_z + p.shelf_t + p.sleeve_wall + p.sleeve_bore / 2,
        sleeve_top_z=shelf_z + p.shelf_t + p.sleeve_bore + 2 * p.sleeve_wall,
        sleeve_front=p.plate_t,
        sleeve_back=p.plate_t + p.sleeve_len,
    )


def _lower_at(xn: float) -> float | None:
    """Lowest y of the branch outline at normalised x, by edge crossings."""
    ys = []
    for (x1, y1), (x2, y2) in zip(BRANCH, BRANCH[1:] + BRANCH[:1]):
        if (x1 - xn) * (x2 - xn) <= 0 and x1 != x2:
            ys.append(y1 + (y2 - y1) * (xn - x1) / (x2 - x1))
    return min(ys) if ys else None


def _contact_half(p: P, h: float) -> float:
    """Half-width of the branch's ground-contact patch, in mm.

    The branch touches the table over its middle and lifts at the forks, so
    "how wide is the branch" is the wrong question — the feet have to sit inside
    the part that actually touches. Measured by walking the traced outline
    rather than assumed from its bounding box, which is the mistake this part
    has now made three times.
    """
    ground = min(y for _, y in BRANCH) * h + p.base_trim
    best = 0.0
    for i in range(1, 2000):
        xmm = i * 0.1
        yn = _lower_at(xmm / h)
        if yn is None:
            break
        if yn * h <= ground + 0.01:
            best = xmm
    return best


def _face(poly, h) -> Sketch:
    """One traced outline as a sketch in the XZ plane, scaled to owl height `h`."""
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine():
            Polyline(*[(x * h, y * h) for x, y in poly], close=True)
        make_face()
    return sk.sketch


def _plate(p: P, g) -> Part:
    """The owl: outline extruded, apertures cut, shelf and gussets added."""
    body = _face(BODY, g.h)
    holes = [_face(EYE_L, g.h), _face(EYE_R, g.h)]
    if p.beak:
        holes.append(_face(BEAK, g.h))

    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            add(body)
        # dir is explicit: Plane.XZ's normal is -Y, so a bare extrude() builds the
        # owl BACKWARDS and puts the shelf on its face. The front elevation
        # cannot show that, and did not.
        extrude(amount=p.plate_t, dir=(0, 1, 0))
        for hole in holes:
            with BuildSketch(Plane.XZ):
                add(hole)
            extrude(amount=p.plate_t, dir=(0, 1, 0), mode=Mode.SUBTRACT)

        # The tab, reaching down from the owl's drawn base into the branch.
        with BuildSketch(Plane.XY.offset(g.slot_floor)):
            Rectangle(g.tab_w, p.plate_t, align=(Align.CENTER, Align.MIN))
        extrude(amount=-g.slot_floor)

    # Fused OUTSIDE the builder, deliberately. `add()` places a shape relative
    # to the builder's CURRENT WORKPLANE, which is still Plane.XZ from the body
    # sketch — so the shelf was re-mapped, its vertical extent became a
    # horizontal slab, and the owl grew a 47 mm foot out of its feet. It built,
    # was watertight, and the front elevation showed nothing.
    return bp.part + _shelf(p, g)


def _shelf(p: P, g) -> Part:
    """Shelf, rim and gussets, as one solid reaching INTO the plate.

    Everything here starts at y = 0 — the plate's *front* face — rather than at
    `plate_t`, its back. A shelf that begins exactly where the plate ends merely
    touches it: coincident faces, no shared volume, and the union comes out as
    two separate solids that still render as a perfectly plausible owl. This
    repo has met that failure on pillars, decks, cone apexes and tower bands,
    and the fix has been the same every time — **interpenetrate, never touch**.

    Burying the front of the shelf inside the plate is free: at this height the
    owl's body is far wider than the shelf, and the nearest aperture is the beak
    several millimetres above.

    Built outside any open builder and returned, so it can only be added where
    the caller says. A primitive constructed inside `with BuildPart()` joins it
    at construction time and contributes twice.
    """
    w = PUCK.dia + 2 * p.lip_h + 4
    d = p.plate_t + p.shelf_d           # from the plate's front face, backwards

    floor = Box(w, d, p.shelf_t, align=(Align.CENTER, Align.MIN, Align.MIN))
    floor = floor.locate(Location((0, 0, g.shelf_z)))

    rim = Box(w, d, p.lip_h, align=(Align.CENTER, Align.MIN, Align.MIN))
    pocket = Box(w - 2 * p.lip_h, d - p.lip_h, p.lip_h + 2,
                 align=(Align.CENTER, Align.MIN, Align.MIN))
    rim = (rim - pocket.locate(Location((0, 0, -1)))).locate(
        Location((0, 0, g.shelf_z + p.shelf_t)))

    out = floor + rim
    for sx in (-1, 1):
        with BuildPart(mode=Mode.PRIVATE) as gus:
            with BuildSketch(Plane.YZ.offset(sx * (w / 2 - p.brace_w / 2))):
                with BuildLine():
                    Polyline((0, g.shelf_z),
                             (d, g.shelf_z),
                             (0, g.shelf_z - p.shelf_d * p.brace_drop),
                             close=True)
                make_face()
            extrude(amount=p.brace_w, both=True)
        out += gus.part
    return out


def _branch(p: P, g) -> Part:
    """The perch: the red outline extruded in depth, with a straight slot."""
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            add(_face(BRANCH, g.h))
        extrude(amount=p.branch_d, dir=(0, 1, 0))
        # A straight slot, however gnarled the branch around it.
        with BuildSketch(Plane.XY.offset(g.slot_floor)):
            with Locations((0, p.branch_d * p.slot_front)):
                Rectangle(g.tab_w + 2 * p.slot_clear,
                          p.plate_t + 2 * p.slot_clear)
        extrude(amount=p.tab_h + 2, mode=Mode.SUBTRACT)
        # Flatten the underside to a plane. Referencing the feet to the traced
        # curve's global minimum put them 0.13 mm proud at their own x, because
        # that minimum happens somewhere else entirely — the same mistake as
        # taking BRANCH_TOP for the branch's height under the owl.
        with BuildSketch(Plane.XY.offset(g.ground_z)):
            Rectangle(400, 400)
        extrude(amount=-40, mode=Mode.SUBTRACT)
    # Fused outside the builder — see the note in _plate about add() and the
    # current workplane.
    return bp.part + _feet(p, g)


def _feet(p: P, g) -> Part:
    """Two narrow bars reaching back from the branch, for the centre of gravity.

    The branch used to do this by being 46 mm deep, which made a slab heavier
    than the owl it holds. Stability does not want depth everywhere — it wants
    the support to reach past the rearmost mass at two points, which is all a
    tripod ever needs. These sit low and slim under the fork ends, where the
    branch is already thick, so they read as roots rather than as a bracket.
    """
    out = None
    y0 = g.branch_front + p.branch_d - 1.0          # start inside the branch
    for sx in (-1, 1):
        bar = Box(p.foot_w, g.foot_back - y0, p.foot_h,
                  align=(Align.CENTER, Align.MIN, Align.MIN))
        bar = bar.locate(Location((sx * g.foot_x, y0, g.ground_z)))
        out = bar if out is None else out + bar
    return out


def _sleeve(p: P, g) -> Part:
    """The puck's snoot: a square tube, lying on the shelf, aimed at the owl.

    Same construction as `tealight_sleeve` and for the same reasons — one
    primitive minus another, OUTSIDE any builder, cutter longer than the sleeve
    so its ends fall clear of the faces they cut.

    Modelled here in its USE pose: axis horizontal, running front to back, front
    end flush with the plate's rear face. `pieces()` stands it up for printing.
    Both ends stay open: the front is the aperture that lights the owl, and the
    back is what keeps the switch and the battery hatch reachable with the puck
    in place.
    """
    across = g.sleeve_across
    outer = Box(across, p.sleeve_len, across,
                align=(Align.CENTER, Align.MIN, Align.MIN))
    cutter = Box(p.sleeve_bore, p.sleeve_len + 2, p.sleeve_bore,
                 align=(Align.CENTER, Align.MIN, Align.MIN))
    tube = outer - cutter.locate(Location((0, -1, p.sleeve_wall)))
    return tube.move(Location((0, g.sleeve_front, g.floor_top)))


def build(p: P) -> Part:
    """The assembly: owl seated in its branch, as it will stand on a shelf.

    The plate is lifted by `seat_z`. The owl cannot descend until its tab bottom
    reaches the slot floor — it stops when its shoulders, where the body widens
    past the tab, meet the branch's top face. Modelling it sitting at z=0 shows
    an assembly that cannot exist, and does it in the one direction a front
    elevation cannot show.
    """
    g = geometry(p)
    plate = _plate(p, g).move(Location((0, 0, g.seat_z)))
    branch = _branch(p, g).move(Location((0, g.branch_front, 0)))
    # The sleeve is in the assembly because the cutaway is the only view that
    # can show it: from the front it is entirely hidden behind the owl, which
    # is a criterion rather than an accident.
    return plate + branch + _sleeve(p, g)


def pieces(p: P) -> dict:
    """What actually goes on the plate, each already in its print pose."""
    g = geometry(p)
    # The plate lies face-down. That is what makes the feathered outline free:
    # its plane goes horizontal, so no feather lobe is ever an overhang, and the
    # layers run along the plate rather than across its narrow places.
    # +90, not -90. Rotating about X maps +Y to +Z, which puts the SHELF up in
    # the air and the owl's face down on the bed. The other way lays it
    # shelf-down: the plate then rests on the shelf's rim and the entire owl
    # face — 9229 mm2 of it — becomes a flat overhang 47 mm above the plate.
    plate = _plate(p, g).rotate(Axis.X, 90)
    branch = _branch(p, g)
    # Stood on end, bore axis vertical — every face vertical or horizontal, no
    # supports. This is NOT the pose it is used in, and the two genuinely
    # differ: in use the axis is horizontal, which is the whole point of it.
    sleeve = _sleeve(p, g).rotate(Axis.X, 90)
    out = {}
    for name, shape in (("plate", plate), ("branch", branch), ("sleeve", sleeve)):
        bb = shape.bounding_box()
        # `.move()`, not `.locate()`. locate() sets an ABSOLUTE location and
        # discards whatever transform the shape already carried — so it threw
        # the rotate() above straight away, and the plate went to the plate
        # standing up, 140 mm tall, with 389 islands. It still built, still
        # passed validity, and still rendered as a perfectly good owl.
        out[name] = shape.move(Location((0, 0, -bb.min.Z)))
    return out


def check(part: Part, p: P) -> None:
    g = geometry(p)

    # --- the load-bearing one: does the light land where it should? --------
    # Asserted on coverage, not on shelf_z, because the number is meaningless
    # without the eyes it is supposed to be aligned with.
    eye_lo, eye_hi = _band(EYE_L, EYE_R, g.h)
    overlap = min(eye_hi, g.led_hi) - max(eye_lo, g.led_lo)
    covered = overlap / (eye_hi - eye_lo)
    assert covered >= 0.85, (
        f"the puck's LED band ({g.led_lo:.1f}-{g.led_hi:.1f} mm) covers only "
        f"{covered:.0%} of the eyes ({eye_lo:.1f}-{eye_hi:.1f} mm). shelf_z is "
        f"derived from EYE_CENTRE — if this fires, the trace and the puck "
        f"disagree, not the parameters."
    )

    if p.beak:
        beak_lo, beak_hi = _band(BEAK, BEAK, g.h)
        assert beak_hi <= g.opaque_hi + 0.5, (
            f"the beak reaches {beak_hi:.1f} mm but the puck's opaque base only "
            f"shadows to {g.opaque_hi:.1f} mm, so the beak would compete with "
            f"the eyes for brightness"
        )

    # --- the sleeve ---------------------------------------------------------
    # It shrouds the whole puck and no more. Both directions, because both are
    # real: short of the flame tip it leaks out of the side it was built to
    # block, and past it the sleeve is adding length the shelf has to find for
    # nothing. `tealight_sleeve` asserts the OPPOSITE bound for an upright puck
    # — that is not a contradiction to be tidied up, it is two parts wanting
    # opposite things, and the pair of assertions is what records that.
    assert p.sleeve_len >= PUCK.flame_top - 1e-9, (
        f"a {p.sleeve_len:.1f} mm sleeve stops {PUCK.flame_top - p.sleeve_len:.1f} "
        f"mm short of the {PUCK.flame_top:.1f} mm puck, so the flame tip sticks "
        f"out of the end and lights the side of the shelf it was meant to hide"
    )
    assert p.sleeve_len <= PUCK.flame_top + 1e-9, (
        f"a {p.sleeve_len:.1f} mm sleeve is longer than the {PUCK.flame_top:.1f} "
        f"mm puck — shroud past the flame tip blocks nothing and only eats shelf"
    )
    assert p.sleeve_bore > PUCK.dia, (
        f"a {p.sleeve_bore:.1f} mm bore cannot admit a {PUCK.dia:.1f} mm puck at "
        f"all — the arithmetic failing, long before the fit does"
    )

    # Raising the flame axis is the sleeve's one cost, and it is only affordable
    # while the axis stays inside the eyes. The bare puck rests on its own
    # cylinder at dia/2; sleeved, it rests on a wall and sits centred in a bore.
    assert eye_lo < g.sleeve_axis_z < eye_hi, (
        f"the sleeve lifts the flame axis to {g.sleeve_axis_z:.1f} mm, outside "
        f"the eyes at {eye_lo:.1f}-{eye_hi:.1f} mm — a bare puck sits at "
        f"{g.floor_top + PUCK.dia / 2:.1f}, so the sleeve, not the shelf, is what "
        f"moved"
    )

    # It must not peek out from behind the head. Lying down, the sleeve's
    # across-flats is its HEIGHT as well as its width, so it reaches far above
    # the shelf and far above the eyes — 14 mm above them at 140 mm — and
    # "the shelf is not visible from the front" stops being a statement about
    # the shelf. Checked against the traced silhouette at every height the
    # sleeve occupies, because the owl narrows towards the ear tufts and a
    # rescale changes where it stops being wide enough.
    z = g.floor_top
    while z <= g.sleeve_top_z + 1e-9:
        span = _body_span_at(z, g.h)
        assert span is not None and min(-span[0], span[1]) >= g.sleeve_across / 2, (
            f"at z={z:.1f} mm the owl is only {span and min(-span[0], span[1]):.1f} "
            f"mm to either side of centre but the sleeve needs "
            f"{g.sleeve_across / 2:.1f} — it would show past the silhouette"
        )
        z += 1.0

    # And it has to fit in the pocket the shelf's rim makes, which is the
    # tightest clearance on the part: 0.7 mm a side at 140 mm.
    pocket_w = PUCK.dia + 2 * p.lip_h + 4 - 2 * p.lip_h
    assert g.sleeve_across < pocket_w, (
        f"the sleeve is {g.sleeve_across:.1f} mm across and the rim's pocket is "
        f"{pocket_w:.1f} mm — it will not sit down inside the lip"
    )
    assert g.sleeve_back <= p.plate_t + p.shelf_d - p.lip_h, (
        f"the sleeve reaches {g.sleeve_back:.1f} mm back and the rim's inner "
        f"face is at {p.plate_t + p.shelf_d - p.lip_h:.1f} — it will not fit "
        f"between the plate and the back rim"
    )

    # --- the pieces are pieces --------------------------------------------
    for name, shape in pieces(p).items():
        n = len(shape.solids())
        assert n == 1, f"the {name} is {n} separate solids, not one"

    # --- the joint ---------------------------------------------------------
    assert p.slot_clear > 0, (
        "the slot needs clearance; an interference fit in PLA either will not "
        "assemble or splits the branch"
    )
    assert g.slot_top < 0, (
        "BRANCH_TOP_AT_SLOT is not negative — re-check the trace; the artwork "
        "has the bar sitting below the owl's base"
    )

    # --- it does not tip backwards ----------------------------------------
    # The rearmost significant mass is the puck, and what decides tipping is
    # where its mass ACTS, not where its far edge is. Its centre of mass sits
    # about half a diameter behind the plate; the plate's own mass acts on the
    # plate. So the support has to reach past the puck's centre, with margin for
    # a nudge — not past its back face, which was the first version of this
    # assertion and demanded a branch heavier than the owl it holds.
    want = g.puck_centre + p.tip_margin
    assert g.foot_back >= want, (
        f"the feet reach {g.foot_back:.1f} mm behind the owl; the puck's centre "
        f"of mass is at {g.puck_centre:.1f} mm and wants {p.tip_margin} mm of "
        f"margin behind it"
    )
    # The feet are flush with the branch's base — tested at their OWN x, not
    # against a global minimum that occurs somewhere else on the outline.
    branch_only = _branch(p, g)
    for sx in (-1, 1):
        sl = branch_only & Box(2, 400, 400).locate(Location((sx * g.foot_x, 0, 0)))
        assert abs(sl.bounding_box().min.Z - g.ground_z) < 0.02, (
            f"at x={sx * g.foot_x:.0f} the underside is at "
            f"{sl.bounding_box().min.Z:.2f} but the feet sit at {g.ground_z:.2f}; "
            f"they are not flush and the branch will rock"
        )

    # The feet sit inside the branch's ground-contact patch, with margin.
    outer = g.foot_x + p.foot_w / 2
    assert outer <= g.contact_half - p.foot_margin + 1e-6, (
        f"a foot reaches x={outer:.1f} but the branch only touches the ground "
        f"out to x={g.contact_half:.1f}; it would stick out past the branch's "
        f"own footprint"
    )

    # And they must actually be attached to the branch, not floating behind it.
    branch = _branch(p, g).move(Location((0, g.branch_front, 0)))
    assert len(branch.solids()) == 1, (
        f"the branch is {len(branch.solids())} solids — the feet are not "
        f"joined to it"
    )

    # --- the shelf is BEHIND the owl ---------------------------------------
    # Plane.XZ's normal is -Y, so a bare extrude() builds the plate backwards
    # and hangs the shelf off the owl's face. Every check passed while it did:
    # one valid solid, watertight, on the bed, no islands — and the front
    # elevation, which is the view anyone actually reads, looked perfect. The
    # castle learned the same thing about crenellations: a facade part hides
    # any mistake that lives in the depth direction.
    # Tested on the PLATE alone. The branch legitimately reaches in front of the
    # owl — 30% of its depth is forward of the slot — so the assembly's bounding
    # box says nothing about which way the plate was built.
    pbb = _plate(p, g).bounding_box()
    assert pbb.min.Y > -1e-6, (
        f"the plate reaches to y={pbb.min.Y:.1f}, in front of the owl's face at "
        f"y=0 — it has been extruded the wrong way and the shelf is on the front"
    )
    assert pbb.max.Y > p.plate_t + p.shelf_d * 0.5, (
        f"the plate reaches only {pbb.max.Y:.1f} mm back; the shelf is missing "
        f"or is on the wrong side"
    )

    # --- the tab is seated in the slot -------------------------------------
    # Two loose pieces are CORRECT here: the joint is a clearance fit, so the
    # assembly is legitimately two solids and must not fuse.
    # That makes a bounding box useless — a branch sitting 46 mm in front of the
    # owl gives exactly the same solid count as one it is seated in, and renders
    # identically from the front.
    #
    # So probe instead: the owl rests on the slot floor, therefore there must be
    # branch material directly beneath the tab, and clear air where the tab is.
    under = Box(8, p.plate_t, 1.5).locate(
        Location((0, p.plate_t / 2, g.slot_floor - 1.2)))
    assert (branch & under).volume > 1.0, (
        "there is no branch material under the owl's tab — the pieces are not "
        "engaged. Check the extrusion direction and slot_front before anything "
        "else; both look fine in a front elevation."
    )
    inside = Box(6, p.plate_t, p.tab_h * 0.6).locate(
        Location((0, p.plate_t / 2, g.slot_floor + p.tab_h / 2)))
    assert (branch & inside).volume < 0.5, (
        "the slot is blocked where the tab has to go — the owl cannot seat"
    )
    # Deliberately NOT asserting a solid count on the assembly. The tab bottoms
    # out on the slot floor — that contact is what locates the owl vertically —
    # so those faces are coincident and the kernel fuses them into one solid.
    # Both "1" and "2" are legitimate here, which makes the count meaningless.
    # The two probes above are the real invariant, and unlike a count they say
    # WHERE the pieces are relative to each other.

    # --- nothing thinner than the nozzle can draw --------------------------
    assert p.brace_w >= 3 * printer.NOZZLE, (
        f"gussets are {p.brace_w} mm, under three extrusion widths"
    )
    assert p.plate_t >= 3 * printer.NOZZLE, (
        f"plate is {p.plate_t} mm, under three extrusion widths"
    )


def _body_span_at(z: float, h: float) -> tuple | None:
    """Left and right extent of the owl's silhouette at height `z`, in mm."""
    zn = z / h
    xs = []
    for (x1, y1), (x2, y2) in zip(BODY, BODY[1:] + BODY[:1]):
        if (y1 - zn) * (y2 - zn) <= 0 and y1 != y2:
            xs.append((x1 + (x2 - x1) * (zn - y1) / (y2 - y1)) * h)
    return (min(xs), max(xs)) if xs else None


def _band(poly_a, poly_b, h) -> tuple:
    """Vertical extent, in mm, spanned by one or two traced outlines."""
    ys = [y for _, y in poly_a] + [y for _, y in poly_b]
    return min(ys) * h, max(ys) * h
