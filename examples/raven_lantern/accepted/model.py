r"""raven_lantern — ravens and the word *Nevermore* cut through a black cylinder.

    top rim ----  _________________
                 |   ~<^     ~<^   |   ravens, pierced one wall at a time
                 |  NEVERMORE      |   stencilled; bridges hold the counters
    lit window   |_________________|
                 |                 |   blank wall: the paper liner wraps here
    floor -------|_________________|

The number that is not free is WHERE the openings sit. This is a flame-style
LED tea light: an opaque base with a narrow translucent flame on top and the
LED inside the lower part of that flame. Below the top of that base there is
nothing but grey plastic, so an opening down there is a dark hole rather than a
lit raven. The lit window is therefore short — see the halloween_lantern project
— and it is the scarce dimension in this design.

Two things differ from `tealight_holder`, and both matter:

- **Cutters are extruded ONE way, not both.** That part pierced near and far
  wall with a single bidirectional extrude, which is exact for a heart because
  a heart is left-right symmetric. A letter is not. Doing it here would print
  `eromreveN` on the back.
- **The counters are held from the inside.** Cutting `Nevermore` out of a wall
  leaves the middles of the e's and the o as loose chips. Rather than notching
  the letters — a stencil bridge, which costs legibility — a thin web is added
  back across each counter in the innermost sliver of the wall only. The letter
  is whole from outside; the leash is visible only looking down into the
  lantern. That the whole part is ONE solid is asserted, not assumed.
"""
from dataclasses import dataclass
from math import asin, degrees, pi
from types import SimpleNamespace

from build123d import *

import printer
from projects.halloween_lantern import shared as body
from cadkit import Params


@dataclass(frozen=True)
class P(Params):
    # Puck and envelope come from the halloween_lantern project so the whole
    # collection moves together. Only what is specific to THIS motif is here.

    # --- composition -------------------------------------------------------
    layout: str = "ring"
    """One of:
      ring     ravens around the top of the lit window, word wrapping below
      front    one large raven on the front, word beneath it, plain elsewhere
      shared   word on the front arc, ravens filling the rest of the SAME band
               — spends the scarce lit height only once
    """

    # --- the ravens --------------------------------------------------------
    n_ravens: int = 6
    raven_h: float = 14.0        # silhouette height; the width follows the outline
    raven_h_front: float = 18.0  # the single big bird in the `front` layout

    feet: str = "full"
    """How much of the bird's underside survives. These are OPENINGS, so a
    feature narrower than the nozzle is not a fine detail, it is gap-fill.

      full   toes and all, thickened to printability per `toe_w_nozzles`. The
             default, because a bird with legs and no feet reads as a mistake.
             Unthickened it would need an ~80 mm raven.
      legs   toes cropped, leg shafts kept. Viable from roughly 12 mm up.
      body   cropped above the ankles; the bird stands on a flat edge.

    Asserted against the nozzle in check(), so asking for detail the machine
    cannot resolve fails at build time rather than on the plate."""

    toe_w_nozzles: float = 1.0
    """Finished toe width, in nozzle diameters — a TARGET, not an amount added.

    Specifying the thickening directly (it used to be `toe_thicken`, in mm) is
    how the feet came out disproportionately fat: a fixed 0.3 mm per side turned
    a 0.07 mm toe into 0.67 mm, thicker than the 0.46 mm leg it hangs off. The
    dilation needed is a function of the bird's size, so it is derived rather
    than dialled, and the feet-thinner-than-legs relationship is asserted.

    In nozzle diameters rather than mm so it survives a change of machine."""

    # --- the word ----------------------------------------------------------
    text: str = ""
    """Empty: the lettering was DROPPED after the first print.

    It was not a modelling failure. The letters cut cleanly and read well; the
    0.5 mm retaining webs holding the counters of `R` and `O` tore apart when
    the support material was pulled out of the letter openings. The webs were
    sized against the nozzle — can the machine lay this down — and never against
    the forces of post-processing, which is where they actually died.

    Thickening them is not a fix worth having: they would have to grow enough to
    take a thumbnail's worth of prying, by which point they are visible from
    outside and the letters read badly again, which is where this whole thread
    started. See prints.md.

    The machinery is all still here and works. Set this to a word to bring it
    back, ideally one whose letters have no counters at all."""

    font: str = "Arial Black"
    """Chunkier than Impact on purpose. The retaining bar has a fixed minimum
    width set by the nozzle, so the heavier the stroke, the smaller a fraction
    of the letter that bar occupies. Weight buys legibility here in a way font
    size alone does not."""

    font_size: float = 5.5
    letter_gap: float = 0.35     # extra arc between glyphs. Cutting per-glyph
                                 # is what keeps each letter square to its own
                                 # bit of wall, and it loses kerning.
    bridge_w: float = 0.5        # width of the bar retaining each counter
    web_t: float = 0.8           # how deep into the wall the retaining bars go,
                                 # measured from the bore. The letter is cut
                                 # clean through; only this innermost sliver
                                 # carries a bar, so from outside the glyph is
                                 # whole. Two perimeters at a 0.4 nozzle.

    # --- spacing -----------------------------------------------------------
    band_gap: float = 1.6        # clear wall between the raven band and the word
    min_rib: float = 2.0         # least material between adjacent openings

    # --- how open the wall may get -----------------------------------------
    # A lantern, not a colander. Too little removed and it does not light; too
    # much and a black object stops having a silhouette. Neither end is caught
    # by any wall-thickness check, so both are asserted.
    # Fractions of the WHOLE outer wall, not of the motif band — see check().
    open_frac_min: float = 0.04
    open_frac_max: float = 0.28

    chamfer_top: float = 0.8
    chamfer_bottom: float = 0.6


PARAMS = P()

# Cut across Y so the section passes through the front wall, where the word is.
# The word is exactly what a shaded exterior renders least legibly.
SECTION = "y"

# Upright on its base, as modelled. Every opening is in a vertical wall, so each
# bridges across its own top the way a circular hole does. There is no pose in
# which this prints better and several in which it prints worse.
PRINT_ROTATION = (0, 0, 0)


# --- the raven silhouette --------------------------------------------------
# Traced from the reference artwork supplied, not drawn by hand: the
# hand-drawn predecessor was a lumpy approximation and looked it. The trace is
# a Moore-neighbour boundary walk over the alpha-composited bitmap, simplified
# with Douglas-Peucker at 4 px, giving 86 points for a 1048 px-tall source.
#
# Normalised to height 1.0 and centred in x, so `raven_h` remains the only size
# knob and editing a point changes the shape but never the size. Facing +X.
#
# A perched bird, which is both the one in the poem and the printable one:
# spread wings would put a wide near-horizontal overhang above each opening.
#
# RE-TRACING: keep the normalisation. The `_RAVEN_FEATURE` figures below are
# measured off THIS outline and are what the printability assertion leans on.
_RAVEN_OUTLINE = [
    (+0.2714, 1.0000), (+0.3163, 0.9990), (+0.3745, 0.9838), (+0.4748, 0.9771),
    (+0.4729, 0.9733), (+0.5178, 0.9542), (+0.5312, 0.9322), (+0.4051, 0.9102),
    (+0.3860, 0.9016), (+0.3812, 0.8863), (+0.3736, 0.8854), (+0.3650, 0.8739),
    (+0.3497, 0.8405), (+0.3459, 0.8071), (+0.3487, 0.6657), (+0.3421, 0.6323),
    (+0.3277, 0.6017), (+0.2838, 0.5205), (+0.2169, 0.4164), (+0.1596, 0.3553),
    (+0.0402, 0.2607), (+0.0087, 0.1958), (+0.0030, 0.1595), (+0.0068, 0.1452),
    (+0.0813, 0.0573), (+0.1310, 0.0449), (+0.1768, 0.0468), (+0.2093, 0.0267),
    (+0.2208, 0.0086), (+0.2179, 0.0048), (+0.1940, 0.0248), (+0.1759, 0.0105),
    (+0.1444, 0.0277), (+0.1491, 0.0124), (+0.1453, 0.0019), (+0.1348, 0.0220),
    (+0.1253, 0.0067), (+0.0966, 0.0267), (+0.0479, 0.0353), (+0.0317, 0.0248),
    (+0.0020, 0.0267), (-0.0113, 0.0134), (-0.0266, 0.0162), (-0.0295, 0.0248),
    (-0.0362, 0.0258), (-0.0600, 0.0000), (-0.0619, 0.0191), (-0.0428, 0.0392),
    (-0.0190, 0.0497), (+0.0154, 0.0478), (+0.0374, 0.0573), (-0.0467, 0.1700),
    (-0.0495, 0.1929), (-0.0390, 0.2311), (-0.0419, 0.2397), (-0.0877, 0.2340),
    (-0.1011, 0.2455), (-0.1345, 0.2512), (-0.2119, 0.2273), (-0.2406, 0.2330),
    (-0.2797, 0.2206), (-0.2931, 0.2302), (-0.3103, 0.2283), (-0.3924, 0.2111),
    (-0.5156, 0.1519), (-0.5834, 0.1289), (-0.6646, 0.1299), (-0.6637, 0.1414),
    (-0.6379, 0.1595), (-0.4726, 0.2531), (-0.7047, 0.2168), (-0.7296, 0.2197),
    (-0.7181, 0.2378), (-0.5424, 0.3114), (-0.4077, 0.3820), (-0.4001, 0.4126),
    (-0.3857, 0.4327), (-0.3332, 0.4709), (-0.2167, 0.5406), (-0.1116, 0.6313),
    (+0.0603, 0.7564), (+0.1033, 0.8042), (+0.1377, 0.8892), (+0.1797, 0.9675),
    (+0.2112, 0.9885),
]

# Narrowest features in the outline, as a fraction of the bird's height,
# measured off the source bitmap rather than estimated:
#
#     toes        0.005 – 0.012      leg shafts   0.033      body   >0.13
#
# These are OPENINGS, so each is a slot of that width in the wall. Multiply by
# `raven_h` and compare against the nozzle: at 12 mm the legs are a 0.40 mm slot
# — one extrusion wide — and the toes are 0.10 mm, which is not a slot at all.
# A feature below the nozzle does not vanish cleanly; the slicer fills it with
# ragged gap-fill, so the bird gets blobby ankles rather than no ankles.
#
# Hence `feet`: the bird is cropped at a height that keeps only what can
# actually print at the size in use.
_RAVEN_FEATURE = {"toes": 0.005, "legs": 0.033, "body": 0.13}

# Where to cut, per `feet` setting, as (x_from, x_to, y_below) in normalised
# units. A rectangle, NOT a full-width horizontal line.
#
# The distinction matters and the first version got it wrong. The legs hang
# under the body at x in [+0.05, +0.33], but the TAIL sweeps down behind to
# y≈0.13 — lower than the belly. A horizontal cut at the belly line therefore
# takes the tip off the tail as well, which is what "the bottom of the ravens is
# cut off improperly" was: a bird with a squared-off tail.
#
# Limiting the cut in x removes the legs and leaves the tail whole. Values are
# read off a column-by-column scan of the source bitmap, not estimated.
# The x limits are needed for `body` and WRONG for `legs`, which is the second
# way to get this cut wrong. The foot spreads either side of the leg — a rear
# toe at x≈-0.06 as well as the front ones out to x≈+0.22. Trimming toes over
# the leg's x-range only takes the FRONT of the foot off and leaves the back
# claw, which is worse than either keeping or removing the whole foot.
#
# At the toe line there is nothing else to protect — the tail bottoms out at
# y≈0.129, well above 0.055 — so `legs` cuts full width and `body`, which cuts
# high enough to reach the tail, does not.
_RAVEN_CROP = {
    "full": None,
    "legs": (-1.0, +1.0, 0.055),     # toes off, leg shafts kept; full width
    "body": (+0.04, +0.34, 0.235),   # legs off at the belly, tail preserved
}

# The narrowest feature that SURVIVES each crop, again as a fraction of height.
# This is what the printability assertion multiplies by `raven_h`.
_RAVEN_MIN_FEATURE = {"full": 0.005, "legs": 0.033, "body": 0.13}

# How far up the bird the "foot zone" reaches, in normalised units. Everything
# below this is fair game for thickening; everything above is the bird as traced.
_FOOT_ZONE = 0.075


def toe_thicken(p) -> float:
    """How much to add per side to reach the target toe width.

    Derived from the bird's size, not chosen: the traced toe scales with
    `raven_h`, so a fixed millimetre figure over-fattens a small bird and
    under-fattens a large one. Returns 0 when the toes already clear the target.
    """
    raven_h = p.raven_h_front if p.layout == "front" else p.raven_h
    raw = _RAVEN_MIN_FEATURE["full"] * raven_h
    return max(0.0, (p.toe_w_nozzles * printer.NOZZLE - raw) / 2)


def _raven_face(height: float, feet: str = "full",
                toe_thicken: float = 0.0) -> Sketch:
    """The silhouette, cropped per `feet` and scaled so its height is `height`.

    Cropping happens in normalised space and BEFORE scaling, so `raven_h` always
    means the height of the bird you actually get. Cropping after would make the
    same `raven_h` mean three different sizes depending on `feet`, and a set of
    lanterns would stop matching.

    Normalised to sit on y=0 and be centred in x, exactly like a glyph, so both
    kinds of opening are positioned by their bottom edge.
    """
    cut = _RAVEN_CROP[feet]
    with BuildSketch() as sk:
        with BuildLine():
            Polyline(*_RAVEN_OUTLINE, close=True)
        make_face()
        if cut is not None:
            x_from, x_to, y_below = cut
            # A rectangle over the LEG ZONE only. Cutting full width would take
            # the tail tip with it, because the tail hangs lower than the belly.
            with Locations(((x_from + x_to) / 2, y_below)):
                Rectangle(x_to - x_from, 4,
                          align=(Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)

    bb = sk.sketch.bounding_box()
    face = scale(sk.sketch, by=height / bb.size.Y)

    if feet == "full" and toe_thicken > 0:
        face = _thicken_feet(face, height, toe_thicken)
        # Re-scale: fattening the foot grew the silhouette downward, and
        # `raven_h` has to keep meaning the height of the bird you get.
        face = scale(face, by=height / face.bounding_box().size.Y)

    bb = face.bounding_box()
    return face.translate((-bb.center().X, -bb.min.Y, 0))


def _thicken_feet(face: Sketch, height: float, amount: float) -> Sketch:
    """Fatten the toes so they can be printed at all, leaving the bird alone.

    The traced toes are 0.5–1.2% of the bird's height. At any lantern-sized bird
    that is a fraction of a nozzle width — printable only on an ~80 mm raven —
    and the previous answer was to crop them off. Cropping is worse: a bird with
    legs and no feet reads as a mistake, where a bird with slightly chunky feet
    reads as a bird.

    So the foot zone alone is dilated. This is what an illustrator does adapting
    artwork for a cutout, and it is deliberately NOT a uniform offset of the
    whole silhouette: that would bloat the beak, round off the tail notch, and
    change every proportion in order to fix one region.

    The toes DO merge into a paddle, because the gaps between them are the same
    order as the toes themselves and close at the same time. That is the honest
    cost, and a solid foot is still a foot.
    """
    bb = face.bounding_box()
    zone_top = bb.min.Y + _FOOT_ZONE * height

    with BuildSketch() as zone:
        add(face)
        with Locations((bb.center().X, zone_top)):
            Rectangle(bb.size.X * 3, height * 3,
                      align=(Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    if not zone.sketch.faces():
        return face

    fat = offset(zone.sketch, amount=amount, kind=Kind.INTERSECTION)
    with BuildSketch() as combined:
        add(face)
        add(fat)
    return combined.sketch


# --- the word --------------------------------------------------------------
def _glyph_face(ch: str, p: P) -> Sketch:
    """One character, exactly as the typeface draws it. Counters left intact.

    Align.MIN on Y puts y=0 at the bottom of the glyph, which for a word with no
    descenders is the baseline. Letting each glyph centre itself instead would
    set `N` and `e` on different lines — they have different heights, so a
    centred lowercase floats.
    """
    with BuildSketch() as sk:
        Text(ch, font_size=p.font_size, font=p.font,
             align=(Align.CENTER, Align.MIN))
    return sk.sketch


def _glyph_webs(ch: str, p: P):
    """Retaining bars for a glyph's counters, and how many counters there were.

    Cutting a glyph out of a wall turns each of its counters — the middle of an
    `o`, the eye of an `e` — into an island of plastic with nothing holding it.
    It falls out of the print, and nothing about the model announces that: the
    build succeeds and the render shows a perfectly good letter.

    The obvious fix is a stencil bridge: a gap cut *through* the letter, so the
    counter hangs off the surrounding wall. It works, it is what a stencil
    typeface does, and it costs legibility — a bar through the top of an `e`
    removes the top of the bowl and the letter drifts toward reading as an `o`.
    That was the first attempt here and the renders showed it plainly.

    So the bar is not cut through the letter at all. It is added back as a thin
    web spanning the counter, occupying only the innermost sliver of the wall
    (`web_t`). From outside the letter is whole, exactly as the typeface drew
    it. The web is flush with the bore, so the rolled paper liner still lies
    flat against the wall rather than being held off it by the bars.

    The bar runs the FULL height of the glyph, from below the baseline to above
    the cap, rather than from the counter up. That sounds like more material and
    is less: a bar anchored in solid wall at both ends can be much thinner than
    one cantilevered off a single end, and thin is what makes it disappear. A
    short stub also reads as a blob interrupting the letter, where a full-height
    hairline reads as a seam and the eye ignores it.
    """
    face = _glyph_face(ch, p)
    inner = [w for f in face.faces() for w in f.inner_wires()]
    if not inner:
        return None, 0

    top = face.bounding_box().max.Y
    with BuildSketch() as webs:
        for wire in inner:
            # The counter's BOUNDING BOX centre, not `wire.center()`. The latter
            # is not the centroid: for the `O` counter it returns the right-hand
            # EDGE, so every bar landed against the side of the hole it was
            # supposed to be crossing. Asserted in check() now.
            cx = wire.bounding_box().center().X
            with Locations((cx, -0.5)):
                Rectangle(p.bridge_w, top + 1.0, align=(Align.CENTER, Align.MIN))
    return webs.sketch, len(inner)


def _word(p: P) -> list[tuple[Sketch, Sketch | None, float]]:
    """The word as (glyph, retaining webs, angular offset in radians) triples.

    Each glyph is cut on its own radial plane rather than the whole word being
    cut as one flat prism. A flat prism spanning this much arc would smear the
    end letters into obliquity, and the word would read only from dead-on. Per
    glyph, every letter is square to its own bit of wall and the word curves.
    """
    if not p.text:
        return []
    r = body.outer_r()
    glyphs = [_glyph_face(ch, p) for ch in p.text]
    webs = [_glyph_webs(ch, p)[0] for ch in p.text]
    widths = [g.bounding_box().size.X for g in glyphs]
    total = sum(widths) + p.letter_gap * (len(glyphs) - 1)

    out, cursor = [], -total / 2
    for g, wb, w in zip(glyphs, webs, widths):
        out.append((g, wb, (cursor + w / 2) / r))   # arc length → radians
        cursor += w + p.letter_gap
    return out


# --- layout ----------------------------------------------------------------
def geometry(p: P) -> SimpleNamespace:
    """Everything derived, in one place, read by both build() and check()."""
    e, puck = body.ENVELOPE, body.PUCK
    inner_r, outer_r = body.inner_r(), body.outer_r()
    lit_lo, lit_hi = body.lit_window()

    word_h = p.font_size if p.text else 0.0
    raven_h = p.raven_h_front if p.layout == "front" else p.raven_h

    # The motif HANGS FROM THE RIM. Height is fixed for the whole set, so the
    # top of the cutouts is a shared datum and everything else is measured down
    # from it. Every lantern's motif therefore starts on the same line, however
    # tall the artwork is — which is the alignment a shelf of them actually
    # shows. Building up from the floor instead would share a bottom line and
    # stagger at the top, where it is far more visible.
    band_hi = body.motif_top()

    if not p.text:
        raven_lo = word_lo = band_hi - raven_h
    elif p.layout == "shared":
        # One band carrying both: word and ravens at the same height on
        # different arcs, so the scarce lit height is spent once.
        raven_lo = band_hi - raven_h
        word_lo = band_hi - word_h
    else:
        # ring and front both stack the word under the birds. They differ in
        # how many birds there are and how big, not in the vertical order.
        raven_lo = band_hi - raven_h
        word_lo = raven_lo - p.band_gap - word_h

    return SimpleNamespace(
        inner_r=inner_r,
        outer_r=outer_r,
        floor_t=e.floor_t,
        opaque_top=e.floor_t + puck.opaque_h,
        lit_lo=lit_lo,
        lit_hi=lit_hi,
        raven_h=raven_h,
        raven_lo=raven_lo,
        raven_cz=raven_lo + raven_h / 2,
        word_h=word_h,
        word_lo=word_lo,
        word_cz=word_lo + word_h / 2,
        band_lo=min(raven_lo, word_lo),
        band_hi=band_hi,
        holder_h=e.height,
    )


def _radial_cutter(face: Sketch, cz: float, angle_deg: float, g) -> Part:
    """Punch `face` through ONE wall, square to the wall at `angle_deg`.

    Extruded a single direction only. `tealight_holder` extrudes both ways to
    pierce near and far wall at once, which is exact for a symmetric heart and
    would mirror a raven and reverse the word.
    """
    with BuildPart() as cutter:
        with BuildSketch(Plane.XZ):
            with Locations((0, cz)):
                add(face)
        extrude(amount=g.outer_r + 1.0)
    return cutter.part.rotate(Axis.Z, angle_deg)


def _raven_angles(p: P, word) -> list[float]:
    """Where the ravens go — the whole difference between the layouts."""
    if p.layout == "front":
        # Directly above the word, on the same face. The point of this layout is
        # that bird and word are one composition read in a single glance; putting
        # the bird on the back would just be two lonely halves.
        return [0.0]
    if p.layout == "shared" and word:
        # The word owns its arc; the ravens fill what is left of the same band.
        span = degrees(max(t for *_, t in word) - min(t for *_, t in word)) + 25.0
        free = 360.0 - span
        n = max(1, p.n_ravens // 2)
        return [180.0 - free / 2 + free * (i + 0.5) / n for i in range(n)]
    return [i * 360.0 / p.n_ravens for i in range(p.n_ravens)]   # ring


def build(p: P) -> Part:
    g = geometry(p)
    raven = _raven_face(g.raven_h, p.feet, toe_thicken(p))
    word = _word(p)
    # Built OUTSIDE the builder on purpose. A primitive constructed inside a
    # BuildPart context is added to the part there and then, so calling this
    # helper from inside silently unions two cylinders into the model and
    # backfills the bore — which it did, and every check still passed except
    # the volume.
    shell = _web_shell(p, g)

    with BuildPart() as bp:
        Cylinder(g.outer_r, g.holder_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, g.floor_t)):
            Cylinder(g.inner_r, g.holder_h - g.floor_t,
                     align=(Align.CENTER, Align.CENTER, Align.MIN),
                     mode=Mode.SUBTRACT)

        # Chamfer BEFORE the openings, not after. `tealight_holder` does it last
        # so the rim selection cannot catch a heart edge — but every opening
        # here reaches the outer surface and splits the cylindrical face, which
        # splits the rim circle into arcs along with it. Selecting a whole
        # unbroken rim is only possible while the shell is still a plain tube.
        chamfer(bp.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[-1], p.chamfer_top)
        chamfer(bp.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[0], p.chamfer_bottom)

        # The word sits on the front arc — the direction Plane.XZ extrudes
        # toward — so it is the face the front elevation of the sheet shows.
        for face, _webs, theta in word:
            add(_radial_cutter(face, g.word_lo, degrees(theta), g),
                mode=Mode.SUBTRACT)

        for angle in _raven_angles(p, word):
            add(_radial_cutter(raven, g.raven_lo, angle, g), mode=Mode.SUBTRACT)

        # Put the counters back on their leashes. Last, so nothing subtracted
        # afterwards can quietly remove a web again.
        for _face, webs, theta in word:
            if webs is None:
                continue
            bar = _radial_cutter(webs, g.word_lo, degrees(theta), g)
            add(bar & shell, mode=Mode.ADD)

    return bp.part


def _web_shell(p: P, g) -> Part:
    """The innermost sliver of wall, where retaining webs are allowed to live.

    Intersecting a bar with this is what keeps the web off the outside face: the
    letter stays whole as drawn, and the web is only visible looking down into
    the lantern. Its inner surface is flush with the bore, so the rolled paper
    liner still lies flat.
    """
    h = g.holder_h - g.floor_t
    kw = dict(align=(Align.CENTER, Align.CENTER, Align.MIN))
    ring = Cylinder(g.inner_r + p.web_t, h, **kw) - Cylinder(g.inner_r, h, **kw)
    return ring.translate((0, 0, g.floor_t))


def check(part: Part, p: P) -> None:
    g = geometry(p)
    word = _word(p)
    raven_bb = _raven_face(g.raven_h, p.feet, toe_thicken(p)).bounding_box()

    # --- the load-bearing one ---------------------------------------------
    # The puck is opaque for its whole lower half. Any opening below that is a
    # dark hole with grey plastic behind it, and no wall thickness, font size
    # or raven count recovers it. A hard floor, unlike the ceiling.
    assert g.band_lo >= g.opaque_top - 1e-9, (
        f"the motif does not fit. It hangs from z={g.band_hi:.1f} (the shared "
        f"rim datum) down to z={g.band_lo:.1f}, but the puck is opaque up to "
        f"z={g.opaque_top:.1f}, so the bottom of it would stay dark. "
        f"{g.band_hi - g.opaque_top:.1f} mm of lit wall is available; the motif "
        f"wants {g.band_hi - g.band_lo:.1f} mm. Shrink the motif, or raise "
        f"ENVELOPE.height for the WHOLE SET."
    )

    # The ceiling is soft, and softer than the first draft assumed. The liner
    # re-emits over its whole surface, and the stated preference is explicit:
    # too tall is not the failure mode, too short is. A cramped motif is a
    # design that failed; a lantern taller than strictly lit is just a lantern.
    # So this is a backstop against absurdity, not a design constraint.
    assert g.band_hi <= g.lit_hi + 20.0, (
        f"motif reaches z={g.band_hi:.1f}, more than 20 mm above the flame tip "
        f"at z={g.lit_hi:.1f}; that is past what even the liner can spread"
    )

    # --- the counters are actually held ------------------------------------
    # This is the assertion that matters most, and it is checked on the finished
    # solid rather than on the recipe. A counter with no web is a chip of
    # plastic floating inside a hole: the build succeeds, the render shows a
    # perfect letter, and it falls out of the print. As a separate lump it is
    # also a separate SOLID, so counting solids catches it definitively —
    # including any failure mode nobody anticipated.
    solids = len(part.solids())
    assert solids == 1, (
        f"the part is {solids} separate solids, not one; a glyph counter or a "
        f"raven is floating loose and would fall out of the print"
    )

    # And the recipe side, so a font swap that adds a counter cannot go unnoticed
    # even if the solids happen to fuse for some unrelated reason.
    for ch in sorted(set(p.text)):
        webs, n = _glyph_webs(ch, p)
        assert n == 0 or webs is not None, f"glyph {ch!r} has {n} counters and no webs"

        # Each bar must sit INSIDE the counter it is crossing, clear of both
        # sides. A bar hard against one edge still connects the island, still
        # builds, still passes the one-solid check — and looks wrong, which is
        # the only symptom. `wire.center()` returns the counter's right edge
        # rather than its centroid, and that is exactly how this happened.
        for face in [_glyph_face(ch, p)]:
            for fc in face.faces():
                for wire in fc.inner_wires():
                    box = wire.bounding_box()
                    cx = box.center().X
                    room = (box.max.X - box.min.X) / 2 - p.bridge_w / 2
                    assert room >= 0, (
                        f"glyph {ch!r}: counter is {box.max.X - box.min.X:.2f} mm "
                        f"wide, narrower than the {p.bridge_w} mm bar crossing it"
                    )
                    assert box.min.X < cx - p.bridge_w / 2 + 1e-9 and \
                           cx + p.bridge_w / 2 < box.max.X + 1e-9, (
                        f"glyph {ch!r}: retaining bar at x={cx:.2f} is not "
                        f"contained in its counter [{box.min.X:.2f}, "
                        f"{box.max.X:.2f}]; it would sit against the edge"
                    )

    # Floored against the NOZZLE rather than the two-perimeter minimum wall.
    # Deliberate: this bar is a leash, not structure. It is anchored in solid
    # wall at both ends over its whole height and carries nothing but a chip of
    # plastic, so a single-extrusion rib is the right answer — and every tenth
    # of a millimetre here is legibility.
    assert p.bridge_w >= printer.NOZZLE, (
        f"retaining bar {p.bridge_w} mm is narrower than the "
        f"{printer.NOZZLE} mm nozzle; the slicer would not lay it down at all "
        f"and the counter would drop out"
    )
    assert p.web_t >= printer.MIN_WALL, (
        f"web depth {p.web_t} mm is below the {printer.MIN_WALL} mm minimum "
        f"wall; the leash would be thinner than the machine can lay down"
    )
    assert p.web_t < body.ENVELOPE.wall, (
        f"web depth {p.web_t} mm is the whole {body.ENVELOPE.wall} mm wall; the "
        f"bar would show on the outside face and this is just a stencil bridge"
    )

    # --- the raven is still a raven ---------------------------------------
    # A silhouette built from a mangled outline is still a closed shape and
    # still renders as *something*. Aspect ratio is the cheapest thing that
    # notices: a perched raven is markedly wider than it is tall.
    # Measured on the RAW outline — uncropped, unthickened. Cropping the legs and
    # fattening the toes are deliberate operations that legitimately move the
    # aspect ratio, so testing the derived shape makes this assertion a tripwire
    # on the design rather than on the artwork. What it is for is catching an
    # outline that has been edited into something that is no longer a raven.
    raw = _raven_face(1.0, "full", 0.0).bounding_box()
    aspect = raw.size.X / raw.size.Y
    assert 1.2 <= aspect <= 1.9, (
        f"raven silhouette is {aspect:.2f} wide-to-tall; a perched raven should "
        f"be 1.2–1.9. The outline has been edited into something else."
    )

    # --- the bird's detail has to survive the nozzle -----------------------
    # The narrowest surviving feature is a SLOT of that width in the wall, not a
    # fine line of plastic. Below one nozzle diameter the slicer does not omit
    # it cleanly — it fills it with gap-fill, so the bird gets ragged ankles
    # rather than no ankles, which is worse than cropping them deliberately.
    feature = _RAVEN_MIN_FEATURE[p.feet] * g.raven_h
    if p.feet == "full":
        feature += 2 * toe_thicken(p)

        # The proportionality constraint, and the one a render shows instantly
        # while no printability check ever would: a toe must not end up FATTER
        # than the leg it hangs off. Dilating to a fixed millimetre figure broke
        # this, and the only symptom was that the feet looked wrong.
        leg = _RAVEN_MIN_FEATURE["legs"] * g.raven_h
        assert feature <= leg, (
            f"toes finish at {feature:.2f} mm but the legs are only "
            f"{leg:.2f} mm; the feet would be thicker than the legs. Raise "
            f"raven_h to {p.toe_w_nozzles * printer.NOZZLE / _RAVEN_MIN_FEATURE['legs']:.1f} mm "
            f"or lower toe_w_nozzles."
        )
    assert feature >= printer.NOZZLE, (
        f"with feet={p.feet!r} the narrowest opening is {feature:.2f} mm at "
        f"raven_h={g.raven_h}, under the {printer.NOZZLE} mm nozzle. Either "
        f"raise raven_h to {printer.NOZZLE / _RAVEN_MIN_FEATURE[p.feet]:.1f} mm "
        f"or crop higher (feet='body')."
    )

    # A raven wider than the cavity cannot be punched clean through — its edges
    # run past the inner wall and leave a ragged lip instead of a bird.
    assert raven_bb.size.X / 2 < g.inner_r, (
        f"raven is {raven_bb.size.X:.1f} mm wide but the cavity is only "
        f"{2 * g.inner_r:.1f} mm across; reduce raven_h"
    )

    # --- ribs --------------------------------------------------------------
    # Measured as arc on the OUTER surface, where the material is thinnest and
    # where it shows. A floor, not a validated strength number — see notes.md.
    angles = sorted(_raven_angles(p, word))
    if len(angles) > 1:
        raven_arc = 2 * degrees(asin(min(raven_bb.size.X, 1.98 * g.outer_r)
                                     / 2 / g.outer_r))
        gap_deg = min((b - a) for a, b in zip(angles, angles[1:]))
        rib = (gap_deg - raven_arc) / 360 * 2 * pi * g.outer_r
        assert rib >= p.min_rib, (
            f"only {rib:.2f} mm of wall between ravens (min {p.min_rib}); "
            f"reduce n_ravens or raven_h"
        )

    # --- lantern, not colander --------------------------------------------
    # Measured over the WHOLE outer wall, not over the motif band.
    #
    # It was the band originally, and that was wrong in a way only visible when
    # the lettering was dropped. The band shrank from 21 mm to 14 mm because the
    # word's height left with it, so the identical ring of ravens went from 31%
    # to 42% open and tripped the ceiling — while over the whole wall it barely
    # moved, 15.6% to 16.8%. Nothing about the object had changed.
    #
    # A denominator that moves when the design is re-laid-out measures the
    # layout, not the property. What "reads as a black object rather than a
    # colander" actually depends on is how much of the SURFACE is missing, so
    # that is what is measured. Bounds re-derived against the printed part,
    # which was judged good on exactly this axis.
    band_area = 2 * pi * g.outer_r * g.holder_h
    # 0.55 fill factor: a perched raven occupies a bit over half its own box.
    cut = len(angles) * raven_bb.size.X * raven_bb.size.Y * 0.55
    cut += sum(f.area for face, _w, _t in word for f in face.faces())
    frac = cut / band_area
    assert p.open_frac_min <= frac <= p.open_frac_max, (
        f"{frac:.0%} of the motif band is open (want {p.open_frac_min:.0%}–"
        f"{p.open_frac_max:.0%}); "
        + ("too little to light it"
           if frac < p.open_frac_min else "it stops reading as a black object")
    )

    # --- the puck can still be got out ------------------------------------
    # Retrieval is: reach in, pinch the flame, pull. So the number that matters
    # is how far the flame tip is recessed below the rim — not how deep the
    # well is, and not where the openings are. tealight_holder lost its own
    # retrieval to a taller band and nothing in the model complained.
    recess = g.holder_h - (g.floor_t + body.PUCK.flame_top)
    assert recess <= 15.0, (
        f"the flame tip is {recess:.1f} mm down inside the rim; at that depth "
        f"you are fishing for it rather than pinching it"
    )
    # And the bore has to admit the fingers doing the pinching, not just the
    # flame. Two fingertips either side of a {body.PUCK.flame_dia} mm flame.
    assert 2 * g.inner_r - body.PUCK.flame_dia >= 20.0, (
        f"only {2 * g.inner_r - body.PUCK.flame_dia:.1f} mm of bore around the "
        f"flame; there is no room to get a grip on it"
    )
