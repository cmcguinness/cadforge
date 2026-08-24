r"""pumpkin_lantern — a jack-o'-lantern that drops over a tea light.

                    ,--.         stem
                  .'    '.
                 /  ^  ^  \      the face: two eyes, a nose, and two rows of
                |   \__/   |     triangular teeth meeting at a solid waist
                 \__,--,__/
                    ----         an annular floor: rests on the table with the
                                 tea light standing in its hole

**One piece, open at the bottom.** It was two — a base holding the puck and a
lid carrying the face — until a print showed the base was not earning its
place: setting the top straight over the tea light worked better than
assembling it. Dropping it removed the seam, the lip, a fit tolerance, a split
operation, and about half the failure modes this part had accumulated.

What the base actually did was stop the pumpkin wandering off the puck, and an
**annular floor** does that for nothing.

Because the puck now stands on the TABLE rather than on a floor, every "must
clear the puck" height drops by the floor's old thickness — so dropping the base
GAINED 2 mm of usable wall rather than costing any.

**The wall is an optical component.** Orange PLA at 1.1 mm glows: confirmed in
the hand, which is what the first print was for. That is why thickness has to be
constant everywhere — any variation is variation in brightness. The ribs are an
undulation of the whole wall, inner and outer surfaces carrying the same wave,
NOT grooves cut into it: a groove in a 1.1 mm wall is a bright stripe.

Body proportions and the puck's dimensions come from the `halloween_lantern`
project. The set's fixed 40 mm height deliberately does not apply — see spec.md.
"""
from dataclasses import dataclass
from math import cos, hypot, pi, radians, sin, tan
from types import SimpleNamespace

from build123d import *

import printer
from cadkit import Params
from projects.halloween_lantern import shared as body


@dataclass(frozen=True)
class P(Params):
    # --- the pumpkin ------------------------------------------------------
    height: float = 66.0
    """Overall, to the top of the stem. NOT the set's fixed 40 mm — see spec.md.

    A pumpkin is **wider than it is tall**: 58 mm across against 38 mm of body
    is about right. The first attempt came out a beehive because the face was
    laid out first and the body grew to fit it. The face is the thing that gives
    — a real jack-o'-lantern's face occupies the middle of the fruit, not all of
    it."""

    r_equator: float = 35.0
    r_bottom: float = 21.0
    """Where it stands. Must leave the puck room: the bore has to clear
    `projects.halloween_lantern.inner_r()` all the way up the base."""

    z_equator: float = 27.0
    r_stem: float = 3.4
    stem_h: float = 6.0

    wall: float = 1.1
    """**An optical parameter, not just a structural one.** Chosen so orange PLA
    glows. Nobody has printed this filament thin and lit it, so it is a guess in
    an unmeasured direction — see spec.md's open questions."""

    n_lobes: int = 10
    lobe_amp: float = 1.3
    """Rib depth at the equator, in millimetres of radius.

    **The ribs are an undulation of the whole wall, not grooves cut into it.**
    Inner and outer surfaces carry the same wave, so the wall stays 1.1 mm
    everywhere. Cutting grooves instead would leave 0.6 mm at the bottom of each
    one and 1.1 mm between, and with a translucent wall that is not a texture —
    it is a set of bright stripes.

    Set to 0 for a smooth gourd, which is what the first working version was."""

    floor_t: float = 2.0
    centring_clear: float = 0.9
    """Per side, between the centring ring's hole and the puck. Loose: the ring
    only has to stop the pumpkin wandering, and a tea light that has to be
    forced into its own lantern is a worse object than one that rattles."""

    floor_bite: float = 0.4
    """How far the annular floor reaches OUT into the wall, so the union
    actually catches it all the way around the ribbing."""

    buttress: float = 0.0
    """Extra wall thickness added inside, at the rib crests, over the shoulder.

    Not needed at the current shoulder slope, and off by default. It exists
    because **glow at the top does not matter** — the sides are what is seen —
    so material up there is nearly free, and internal ribs at the lobe crests
    would give each layer ten places to land properly even where the overall
    ring overlap is thin. That is a support designed into the model rather than
    printed and snapped off.

    The lever it buys: `max_dr_dz` scales with wall thickness, so a locally
    thicker crest permits a rounder shoulder than the global limit allows."""
    """Thicker than the wall. The puck rests here and it is the face that meets
    the bed, so it wants stiffness more than it wants glow."""


    # --- the face ---------------------------------------------------------
    face_bottom: float = 17.5
    """**The face's total height is the binding constraint on this part**, and
    it is worth understanding before changing any feature size.

    The grin cannot start below the puck's opaque top, and the eyes cannot climb
    past the shoulder without wrapping over the curve and becoming visible from
    directly above. That leaves roughly 17.5 to 45 mm — about 27 mm — for the
    whole stack, on a body only 46 mm tall.

    So every millimetre given to one feature is taken from another — or the
    pumpkin grows. Growing it is legitimate, but **grow the width with the
    height** or it becomes a sphere with a face on it: the first attempt at this
    part came out a beehive precisely because the body was stretched to fit a
    face and nothing else moved."""
    """Bottom of the grin, and **the face is built upward from here**, not
    downward from the eyes.

    Note this part relaxes a rule the other lanterns hold to. There, an opening
    had to sit in line of sight of the LED, because an open-topped cylinder lets
    light straight out and anything above the flame is unlit. A **closed**
    pumpkin is a diffusing chamber: light bounces off the inside of the dome and
    the translucent walls, so the face reads well above the flame tip. Only the
    lower bound still binds, and it binds hard — below the puck's opaque body
    there is grey plastic in the way and no amount of bouncing helps.

    That is the direction the constraint runs: everything must clear the puck's
    opaque body, so the mouth's lower edge is the binding dimension and the eyes
    land wherever the stack puts them. Placing the eyes first and letting the
    mouth fall where it may is how the first attempt ended up with a grin 12 mm
    below the lit zone."""

    mouth_w: float = 36.0
    mouth_h: float = 11.0
    n_teeth: int = 4
    """Triangles along the BOTTOM row. The top row gets one fewer and sits over
    the gaps between them — both share one period, so 4 up and 3 down,
    interleaved.

    Equal counts aligned vertically was the first attempt, and it fails in a way
    that is obvious in the hand and invisible in a render: each top/bottom pair
    fuses into a **diamond**, and the mouth reads as a row of diamonds rather
    than as teeth. Interleaving breaks the pairing."""

    tooth_row_h: float = 7.2
    """How far each row bites into the mouth band.

    Twice this deliberately EXCEEDS `mouth_h`, so the rows overlap and the
    material between them becomes a continuous zigzag. The previous version left
    a solid horizontal waist between two separated rows, which is what let the
    eye pair them into diamonds."""

    tooth_land: float = 1.4
    """Flat material between adjacent triangles in a row.

    Not cosmetic: let the top row's triangles touch at the corners, as they do
    in a drawing, and its holes merge into one full-width opening whose ceiling
    has nothing to land on. The lands break that into short bridges."""

    gap_mouth: float = 6.0
    """Clear wall between the top of the grin and the nose. Generous on purpose:
    a nose sitting close to the teeth reads as a snout."""

    gap_nose: float = 1.5
    """Between the nose and the eyes. Tighter than `gap_mouth`, which is what
    makes the face read as a face rather than as three evenly spaced bands."""
    nose_w: float = 9.3
    nose_h: float = 6.7
    eye_w: float = 14.6
    eye_h: float = 8.0


PARAMS = P()

SECTION = "y"
PRINT_ROTATION = (0, 0, 0)


def max_dr_dz(p: P) -> float:
    """How fast the radius may change with height, for a HOLLOW shell.

    The constraint that produced a disconnected ring at the top of the first
    print, and it is peculiar to a shell rather than a solid.

    Each printed layer of a hollow body is a ring of wall thickness. If the
    radius shifts by more than that thickness between one layer and the next,
    the new ring lands entirely INSIDE the one below and touches nothing. The
    surface can be perfectly smooth and every face perfectly valid; it simply
    arrives as a stack of loose hoops.

    So: |dr/dz| * layer_height < wall. The factor is how much of the ring must
    overlap the one below.

    **0.7 was too generous and the print proved it.** It allows a 0.77 mm step
    against a 1.1 mm wall — only 30% overlap — and the shoulder came out as
    visibly marginal concentric bridging that "almost fell apart". 0.45 leaves
    ~55% overlap, which is a weld rather than a touch. The cost is a steeper,
    less round shoulder; see `buttress` for buying some of it back.

    The generic `islands` check does NOT catch this. Its grid is 0.4 mm where
    the real tolerance here is 0.168 mm, coarse enough to conclude the rings
    touch when they do not.
    """
    return 0.45 * p.wall / printer.LAYER_H


def _thin(pts, min_dz: float) -> list[tuple[float, float]]:
    """Drop sections closer together than `min_dz`, always keeping the last.

    **Loft cost is what makes this part slow**, and it scales with the number of
    sections. An earlier version sampled the shoulder densely on the theory that
    the curve needed it, produced 51 sections some 0.2 mm apart, and ground for
    fifteen minutes before it was killed. The clamp is what makes the shoulder
    printable; the extra sections only made it expensive.
    """
    out = [pts[0]]
    for r, z in pts[1:-1]:
        if z - out[-1][1] >= min_dz:
            out.append((r, z))
    out.append(pts[-1])
    return out


def _clamp_slope(pts, limit: float) -> list[tuple[float, float]]:
    """Walk up the profile, refusing any step that collapses the radius faster
    than `limit`. A too-steep shoulder becomes a cone at the steepest legal
    angle rather than a shelf."""
    out = [pts[0]]
    for r, z in pts[1:]:
        r0, z0 = out[-1]
        dz = z - z0
        if dz <= 0:
            continue
        drop = r0 - r
        if drop > limit * dz:
            r = r0 - limit * dz
        out.append((r, z))
    return out


def _profile(p: P) -> list[tuple[float, float]]:
    """The pumpkin's outer half-section, as (radius, z) from base to stem.

    A squat ellipse below the equator and a converging shoulder above it, so the
    dome **tapers into** the stem rather than flattening under it. A hemisphere
    with a stem stuck on top has a shallow shoulder, and a shallow shoulder is
    where a dome's overhang problem lives.
    """
    # Below the equator. The form matters: this curve must arrive at the equator
    # with ZERO slope, because the equator IS the widest point and the tangent
    # at a maximum is vertical. An earlier version used r ~ t**0.62, which is
    # still widening when it gets there — so it met the upper curve (which
    # starts flat) at a slope discontinuity, and left a crease ring visible all
    # the way round the pumpkin at exactly that height. Continuous radius is not
    # enough; the slope has to be continuous too.
    pts = [(p.r_bottom, 0.0)]
    n = 14
    for i in range(1, n + 1):
        tt = i / n
        z = p.z_equator * tt
        r = p.r_equator - (p.r_equator - p.r_bottom) * (1 - tt) ** 1.8
        pts.append((r, z))

    # The shoulder, sampled densely toward the top where it curves hardest, then
    # SLOPE-CLAMPED. The analytic form has a vertical tangent in r as it reaches
    # the stem — mathematically a smooth dome, physically a horizontal shelf —
    # and no amount of extra sampling fixes that. Clamping turns the last of it
    # into a cone at the steepest angle a hollow wall can actually be printed.
    shoulder_top = p.height - p.stem_h
    for i in range(1, n + 1):
        tt = (i / n) ** 1.25          # a little denser near the top
        z = p.z_equator + (shoulder_top - p.z_equator) * tt
        r = p.r_stem + (p.r_equator - p.r_stem) * ((1 - tt ** 3.0) ** 0.42)
        pts.append((r, z))

    pts = _clamp_slope(pts, max_dr_dz(p))
    pts = _thin(pts, 1.2)

    # Whatever radius the clamp left us at, run a cone down to the stem at the
    # same legal slope, then the stem itself.
    r_last, z_last = pts[-1]
    if r_last > p.r_stem:
        pts.append((p.r_stem, z_last + (r_last - p.r_stem) / max_dr_dz(p)))
    pts.append((p.r_stem, max(p.height, pts[-1][1] + 1.0)))
    return pts


def _inset(pts, d: float) -> list[tuple[float, float]]:
    """The same contour moved `d` inward along its own normal.

    A true offset rather than a scale, because constant WALL THICKNESS is what
    keeps the glow even. Scaling the profile would thin the wall wherever the
    surface is steep.
    """
    out = []
    for i, (r, z) in enumerate(pts):
        r0, z0 = pts[max(0, i - 1)]
        r1, z1 = pts[min(len(pts) - 1, i + 1)]
        dr, dz = r1 - r0, z1 - z0
        L = hypot(dr, dz) or 1.0
        nr, nz = dz / L, -dr / L          # outward normal of an upward contour
        out.append((max(0.2, r - nr * d), z - nz * d))
    # The offset lifts the bottom point as well as pulling it in, leaving the
    # cavity starting above the table. Bring it back down: the pumpkin is open
    # at the bottom and the inside has to reach the plate.
    if out[0][1] > 0:
        out[0] = (out[0][0], 0.0)
    return out


def _r_on(profile, z: float) -> float:
    """Radius of a profile at height `z`, linearly between its points.

    CLAMPS outside the profile's range. The first version fell through to the
    last point, so a query below the base silently answered with the stem's
    radius — a wrong number two orders of magnitude off, arriving as a confident
    2.3 mm where 20 was expected. A lookup that cannot answer should say the
    nearest thing it knows, not the furthest.
    """
    if z <= profile[0][1]:
        return profile[0][0]
    if z >= profile[-1][1]:
        return profile[-1][0]
    for (r0, z0), (r1, z1) in zip(profile, profile[1:]):
        if z0 <= z <= z1:
            f = 0.0 if z1 == z0 else (z - z0) / (z1 - z0)
            return r0 + (r1 - r0) * f
    return profile[-1][0]


def geometry(p: P) -> SimpleNamespace:
    """Everything derived, in one place, read by both build() and check()."""
    prof = _profile(p)
    inner = _inset(prof, p.wall)
    puck = body.PUCK
    return SimpleNamespace(
        profile=prof,
        inner_profile=inner,
        # The puck now stands on the TABLE, not on a floor, so every "must
        # clear the puck" height drops by the floor's thickness. Dropping the
        # base gained 2 mm of usable wall rather than costing anything.
        opaque_top=puck.opaque_h,
        flame_top=puck.flame_top,
        bore_needed=puck.dia / 2 + body.ENVELOPE.fit,
        centring_r=puck.dia / 2 + p.centring_clear,
        r_cavity_at_puck=min(_r_on(inner, z) - lobe_at(p, _r_on(inner, z))
                             for z in (0.5, 8.0, 15.0)),
        height=p.height,
    )


def lobe_at(p: P, r: float) -> float:
    """Rib depth at a section of radius `r`.

    Scaled by the radius so the ribs are deepest at the equator and fade to
    nothing in the stem, the way a real pumpkin's do. A constant amplitude
    would leave the stem fluted like a column.
    """
    if p.lobe_amp <= 0:
        return 0.0
    # Fades to EXACTLY zero at the stem's radius, not asymptotically. Scaling by
    # r/r_equator leaves a fraction of a millimetre of wave on a 3.4 mm stem,
    # which is invisible in a number and reads as a star when you look down on
    # it. Anchoring the fade to the stem radius removes it by construction.
    span = max(0.1, p.r_equator - p.r_stem)
    f = min(1.0, max(0.0, (r - p.r_stem) / span))
    return p.lobe_amp * f ** 0.8


def _lobed_solid(p: P, pts, seg: int = 64) -> Part:
    """Loft a stack of lobed cross-sections into a solid.

    A revolve cannot do this — every section is a different closed curve. The
    same wave is applied to the outer and inner profiles, which is what keeps
    the wall constant.
    """
    if p.lobe_amp <= 0:
        with BuildPart() as bp:
            with BuildSketch(Plane.XZ):
                with BuildLine():
                    Polyline(*[(r, z) for r, z in pts])
                    Line(pts[-1], (0, pts[-1][1]))
                    Line((0, pts[-1][1]), (0, 0))
                    Line((0, 0), pts[0])
                make_face()
            revolve(axis=Axis.Z)
        return bp.part

    with BuildPart() as bp:
        for r, z in pts:
            a = lobe_at(p, r)
            ring = []
            for i in range(seg):
                th = 2 * pi * i / seg
                rr = max(0.15, r + a * cos(p.n_lobes * th))
                ring.append((rr * cos(th), rr * sin(th)))
            with BuildSketch(Plane(origin=(0, 0, z))):
                with BuildLine():
                    Polyline(*ring, close=True)
                make_face()
        loft()
    return bp.part


def _revolve_profile(pts) -> Part:      # kept for the smooth path
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ) as sk:
            with BuildLine():
                Polyline(*[(r, z) for r, z in pts])
                Line(pts[-1], (0, pts[-1][1]))
                Line((0, pts[-1][1]), (0, 0))
                Line((0, 0), pts[0])
            make_face()
        revolve(axis=Axis.Z)
    return bp.part


def _shell(p: P, g) -> Part:
    """Outer solid minus its true inward offset — a sealed hollow body."""
    return _lobed_solid(p, g.profile) - _lobed_solid(p, g.inner_profile)


def face_levels(p: P) -> SimpleNamespace:
    """Where each feature sits, stacked upward from `face_bottom`."""
    mouth_lo = p.face_bottom
    mouth_hi = mouth_lo + p.mouth_h
    nose_lo = mouth_hi + p.gap_mouth
    nose_hi = nose_lo + p.nose_h
    eye_lo = nose_hi + p.gap_nose
    return SimpleNamespace(
        mouth_lo=mouth_lo, mouth_hi=mouth_hi,
        nose_lo=nose_lo, nose_hi=nose_hi,
        eye_lo=eye_lo, eye_hi=eye_lo + p.eye_h,
        eye_cz=eye_lo + p.eye_h / 2,
    )



def _face_cutters(p: P, g) -> list[Part]:
    """Eyes, nose and a toothy grin, cut through the lid from the front.

    Constructed rather than traced: a jack-o'-lantern is triangles and a grin,
    which is deterministic geometry. Tracing would borrow an organic shape's
    difficulties for no benefit — and constructing it is what lets the teeth be
    guaranteed to rise rather than hang.
    """
    out = []
    f = face_levels(p)
    depth = p.r_equator + 4

    def punch(pts):
        with BuildPart() as c:
            with BuildSketch(Plane.XZ):
                with BuildLine():
                    Polyline(*pts, close=True)
                make_face()
            extrude(amount=depth)
        out.append(c.part)

    for sx in (-1, 1):
        cx = sx * (p.eye_w * 0.68)
        punch([(cx - p.eye_w / 2, f.eye_lo), (cx + p.eye_w / 2, f.eye_lo),
               (cx, f.eye_hi)])
    punch([(-p.nose_w / 2, f.nose_lo), (p.nose_w / 2, f.nose_lo),
           (0.0, f.nose_hi)])

    # The grin: two rows of triangular holes, apex-down along the top and
    # apex-up along the bottom, offset half a period. Cut as individual
    # triangles rather than as a mouth-minus-teeth, because in this scheme the
    # triangles ARE the openings and everything else is pumpkin.
    #
    # Both rows are self-supporting, for different reasons:
    #   top    holes widen upward, so each ceiling is a short bridge landing on
    #          the lands either side of it
    #   bottom holes narrow upward, so there is no ceiling to bridge at all, and
    #          the material between them tapers down onto solid wall
    #
    # **Both rows are FLAT** — every triangle in a row begins and ends on the
    # same z, so it begins and ends on the same filament row. An earlier version
    # curved the rows into a smile, which put each tooth's base on a different
    # layer: the ceilings then bridge at four different heights and the row
    # loses the shared anchor that makes them all short spans. Flat is a
    # printing decision that happens to look tidier.
    w, n = p.mouth_w, p.n_teeth
    period = w / n
    half = (period - p.tooth_land) / 2

    for k in range(n):                       # bottom row: apex up
        cx = -w / 2 + period * (k + 0.5)
        punch([(cx - half, f.mouth_lo), (cx + half, f.mouth_lo),
               (cx, f.mouth_lo + p.tooth_row_h)])

    for k in range(1, n):                    # top row: apex down, in the gaps
        cx = -w / 2 + period * k
        punch([(cx - half, f.mouth_hi), (cx + half, f.mouth_hi),
               (cx, f.mouth_hi - p.tooth_row_h)])
    return out


_BUILD_CACHE: dict = {}


def build(p: P) -> Part:
    """Assembled pumpkin. Cached, because lofting the lobes is expensive.

    `pieces()` needs the same solid that `build()` returned — it splits it — and
    the harness calls both on every run. Without the cache the lofts run twice
    for no reason, which on this part is most of a minute. Keyed on the params,
    so a sweep or a watch loop still rebuilds when anything changes.
    """
    key = p.digest()
    if key in _BUILD_CACHE:
        return _BUILD_CACHE[key]
    g = geometry(p)
    part = _shell(p, g)

    # An ANNULAR floor: a ring that sits on the table with the tea light
    # standing in its hole. It is not structural — it is what stops the pumpkin
    # wandering off the puck, which is the only thing the discarded base was
    # really doing.
    #
    # Lobed, like the lip before it, and for the same reason: the rib amplitude
    # is comparable to the wall thickness, so a plain circular disc big enough
    # to meet the wall at the lobe crests bursts through it at the valleys.
    r0 = _r_on(g.inner_profile, 0.0) + p.floor_bite
    r1 = _r_on(g.inner_profile, p.floor_t) + p.floor_bite
    ring = _lobed_solid(p, [(r0, 0.0), (r1, p.floor_t)])
    with BuildPart() as hole:
        Cylinder(g.centring_r, p.floor_t * 3,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
    part += ring - hole.part

    # ONE boolean, not eight. Each subtraction re-evaluates the whole lobed
    # shell; fusing the cutters first means the expensive surface only gets
    # intersected once. Measured: 3.1s of sequential subtractions became 0.6s.
    cutters = _face_cutters(p, g)
    fused = cutters[0]
    for c in cutters[1:]:
        fused += c
    part -= fused
    _BUILD_CACHE[key] = part
    return part




_PIECES_CACHE: dict = {}



def check(part: Part, p: P) -> None:
    g = geometry(p)
    f = face_levels(p)

    # --- one piece, and it must BE one piece --------------------------------
    # The assertion the other lanterns carry and this part did not, which is how
    # a free-floating lip survived several builds, several renders and a print.
    n = len(part.solids())
    assert n == 1, (
        f"the pumpkin is {n} separate solids, not one — something is detached "
        f"and would print as a loose fragment on the plate"
    )

    # --- it has to drop over the tea light ----------------------------------
    assert g.r_cavity_at_puck >= g.bore_needed, (
        f"the cavity is only {g.r_cavity_at_puck:.1f} mm in radius where the "
        f"puck sits and the puck needs {g.bore_needed:.1f}. Widen r_bottom."
    )
    assert g.centring_r < g.r_cavity_at_puck, (
        f"the centring ring's hole ({g.centring_r:.1f} mm) is wider than the "
        f"cavity around it; there would be no ring left to centre anything"
    )
    ring_w = g.r_cavity_at_puck - g.centring_r
    assert ring_w >= printer.NOZZLE * 3, (
        f"the centring ring is only {ring_w:.2f} mm wide — under three "
        f"extrusions it is a whisker, not a locator"
    )

    # --- the face has to be lit and has to be on the pumpkin ----------------
    assert f.mouth_lo >= g.opaque_top, (
        f"the grin's lower edge is at z={f.mouth_lo:.1f} but the puck is opaque "
        f"to z={g.opaque_top:.1f}; it would be a dark hole. Raise face_bottom."
    )
    assert f.eye_hi <= p.height - p.stem_h - 1, (
        f"the eyes reach z={f.eye_hi:.1f}, into the shoulder below the stem at "
        f"z={p.height - p.stem_h:.1f}; the face would wrap over the curve."
    )

    # --- the zigzag between the teeth --------------------------------------
    # The rows overlap now, so there is no waist to measure. What matters is the
    # narrowest diagonal strut between a top triangle and the bottom triangle
    # beside it — the thing actually holding the grin together.
    period = p.mouth_w / p.n_teeth
    half = (period - p.tooth_land) / 2
    lo, hi = f.mouth_lo, f.mouth_hi
    top_apex, bot_apex = hi - p.tooth_row_h, lo + p.tooth_row_h
    # Only where BOTH rows are present: a top triangle and the bottom triangle
    # beside it are half a period apart, and the strut is what is left between
    # them. Measuring outside that band compares a triangle against a phantom
    # neighbour that is not there, which is what the first version did.
    zs = [top_apex + (bot_apex - top_apex) * i / 40 for i in range(41)]
    narrowest = min(
        period / 2
        - half * min(1.0, max(0.0, (z - top_apex) / p.tooth_row_h))
        - half * min(1.0, max(0.0, (bot_apex - z) / p.tooth_row_h))
        for z in zs
    ) if bot_apex > top_apex else period - 2 * half
    assert narrowest >= printer.NOZZLE * 2, (
        f"the zigzag between the teeth narrows to {narrowest:.2f} mm, under two "
        f"extrusions — reduce tooth_row_h or widen tooth_land"
    )
    assert 2 * p.tooth_row_h > p.mouth_h, (
        f"the rows do not overlap ({2 * p.tooth_row_h:.1f} mm of bite into a "
        f"{p.mouth_h} mm mouth), so a solid waist runs between them and each "
        f"pair reads as a diamond rather than as teeth"
    )
    assert p.tooth_land >= printer.NOZZLE * 3, (
        f"the land between triangles is {p.tooth_land} mm; the top row's "
        f"bridges need somewhere to land"
    )

    # --- the shell must be continuous layer to layer ------------------------
    lim = max_dr_dz(p)
    for (r0, z0), (r1, z1) in zip(g.profile, g.profile[1:]):
        if z1 <= z0:
            continue
        rate = abs(r1 - r0) / (z1 - z0)
        assert rate <= lim + 1e-6, (
            f"the profile's radius changes at {rate:.2f} mm per mm of height "
            f"between z={z0:.1f} and z={z1:.1f}, over the {lim:.2f} a "
            f"{p.wall} mm wall can follow. Each printed ring would land inside "
            f"the one below with too little overlap — the shoulder arrives as "
            f"marginal concentric bridging. This is NOT what islands checks."
        )

    assert p.wall >= printer.NOZZLE * 2, (
        f"wall {p.wall} mm is under two extrusions; it will not be watertight"
    )
