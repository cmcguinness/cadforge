"""The contract shared by the Halloween tea light lanterns.

A set of lanterns that sit on the same table wants to *be* a set: same
footprint, same height, same standoff, so they read as siblings and any one of
them can hold any puck. Only the motif cut through the wall differs.

So the envelope lives here rather than in each part, and each part takes it as
an argument::

    from projects.halloween_lantern import shared as body
    ...
    def build(p): ...   # reads body.PUCK, body.ENVELOPE

Not star-imported — a part that does not belong to this set must not be able to
pick a name out of here by accident.

Millimetres.

THE FACT THIS SET TURNS ON
--------------------------
A flame-style LED tea light is not a glowing disc. It is an **opaque base** with
a narrow **translucent flame** standing on top of it, and the LED sits inside
the lower part of that flame. So the light comes from a short, thin column
partway up the puck — not from the puck's top face, and not from the puck at
all below the flame.

That gives the motif band a lower bound *and an upper bound*, which is the part
that is easy to miss::

      z
      |
   30 +   ▲   flame tip — lit from below, no LED inside
      |  ▲▲
   25 +  ███  ← LED sits in here.  THE LIT WINDOW
      |  ███
   15 +--███--------------------------  top of the opaque base
      |█████████████████████████████
      |███  opaque: battery + electronics
    0 +█████████████████████████████

An opening below `opaque_h` is a dark hole with grey plastic behind it. An
opening far above `flame_top` has nothing in line of sight either. Both fail
the same way — silently, and only once it is printed and lit.

The paper liner is what widens that window (see `Envelope.liner_t`).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Puck:
    """A flame-style battery LED tea light.

    All heights are measured from the surface the puck stands on — i.e. **this
    describes an UPRIGHT puck**, and that is an assumption rather than a fact
    about the object.

    A puck laid on its side is a different light source entirely: the flame
    becomes a roughly point source on the cylinder axis, about `dia / 2` above
    the surface, radiating *sideways* at whatever it faces. `opaque_h` then
    blocks almost nothing, because the base is beside the flame rather than
    under it, and every height below is measuring the wrong axis.

    For a lantern in this set the upright assumption is correct: the bodies are
    barely taller than the puck and want light all round. It stops being
    correct for anything much taller than its light source, where laying the
    puck down aims all of the light at one face instead of spreading it over
    storeys nobody is looking at. `parts/mini_castle` found this by accident —
    its first lit print had the puck on its side and produced a brilliant face
    and two dark upper storeys, which no reasoning from these numbers predicts.

    So: if a part is much taller than a puck, **decide the orientation
    deliberately and say so in its spec.** Do not inherit it from here.
    """

    dia: float
    """Widest point of the opaque base. MEASURED 2026-08-04."""

    opaque_h: float
    """Height of the opaque base — battery and electronics. Nothing below this
    is ever lit; an opening here is a dark hole. MEASURED 2026-08-04."""

    led_h: float
    """Height above `opaque_h` of the LED itself, i.e. the top of the genuinely
    emitting part of the flame. MEASURED 2026-08-04."""

    flame_h: float
    """Full height of the flame above `opaque_h`, including the moulded tip
    above the LED which is lit from below rather than emitting.
    MEASURED 2026-08-04."""

    flame_dia: float
    """Widest point of the flame. Small — this is close to a line source, not a
    disc, which is why the diffuser matters. MEASURED 2026-08-04."""

    @property
    def emit_bottom(self) -> float:
        """Lowest height with any light behind it."""
        return self.opaque_h

    @property
    def emit_top(self) -> float:
        """Top of the directly-emitting LED. Above this the flame is lit but
        not emitting, and line of sight to the source is gone."""
        return self.opaque_h + self.led_h

    @property
    def flame_top(self) -> float:
        """Overall height of the puck."""
        return self.opaque_h + self.flame_h


# Measured with calipers, 2026-08-04. These replace the never-measured nominal
# figures carried by `tealight_holder`, whose notes flagged them as the
# highest-risk numbers in that design. They were also the wrong SHAPE of fact:
# that part assumed a flat emitting top face, and this puck has a raised flame.
PUCK = Puck(
    dia=35.0,
    opaque_h=15.0,
    led_h=10.0,
    flame_h=15.0,
    flame_dia=10.0,
)


@dataclass(frozen=True)
class Envelope:
    """The shared body of a lantern in this set. Expected to move under review."""

    fit: float
    """Radial clearance between puck and inner wall.

    **Measured in the hand, 2026-08-04, not calculated.** 0.6 mm was modelled
    and printed and the puck would not go in; raised to 1.6 mm, a 2 mm increase
    in bore diameter. Which of three causes it was has not been established —
    an unmeasured lip on the puck, printed bores coming out undersize, or 0.6
    simply being optimistic for something you drop in by feel. See
    `raven_lantern/prints.md`; the second would be a fact about the machine
    rather than about lanterns.

    Partly spoken for by the paper liner, which is a design element and not an
    accessory. Do NOT tighten this to cure a rattle; the liner is what takes up
    the slack, and a rattle is much cheaper than a puck that will not fit."""

    liner_t: float
    """Thickness of the rolled paper diffuser. An UPPER BOUND rather than a
    measurement (2026-08-04: "assume under 0.2"), which is the right form for
    this number — it is consumed out of `fit`, so what the clearance needs to
    survive is the worst case, not the typical one.

    The liner does more than soften a hot spot. A 10 mm flame is nearly a line
    source; the paper intercepts it and re-emits over its whole surface, which
    turns the source into a lit column. That is what makes a motif band taller
    than the LED itself viable at all — see `lit_window`."""

    height: float
    """Overall height of EVERY lantern in the set. Fixed, 2026-08-04.

    This inverts how the geometry is derived, and that is the whole point. It
    used to be an output — motif height plus margins — so a lantern with a
    bigger motif came out taller, and a shelf of them stepped up and down for
    reasons that were about the artwork rather than about the set.

    Now it is an input. The rim is the datum, the motif hangs from it, and a
    motif that will not fit in the lit space below is a **build failure** rather
    than a silently taller lantern. That is the correct trade: a set that does
    not match is a fault you cannot fix later without reprinting everything,
    where a motif that does not fit is a fault you find in seconds."""

    wall: float
    """Outer wall. Thin is safe here only because an LED produces no heat."""

    floor_t: float

    motif_bottom_margin: float
    """Clear air between the top of the puck's opaque base and the BOTTOM of
    the motif band. Small on purpose: the lit window is only as tall as the
    flame, so every millimetre spent here is canvas lost."""

    top_margin: float
    """Solid rim above the motif band, so the top does not read as a row of
    broken arches — and, since `height` is fixed, the datum the whole motif
    hangs from. Every lantern in the set puts the top of its cutouts exactly
    this far below the rim, so the motifs line up across the shelf even when
    they are different shapes and different heights."""


ENVELOPE = Envelope(
    fit=1.6,
    liner_t=0.2,
    height=40.0,
    wall=2.4,
    floor_t=2.0,
    motif_bottom_margin=0.0,
    top_margin=4.0,
)


def inner_r(e: Envelope = ENVELOPE, puck: Puck = PUCK) -> float:
    """Radius of the well the puck and its paper liner drop into."""
    return puck.dia / 2 + e.fit


def outer_r(e: Envelope = ENVELOPE, puck: Puck = PUCK) -> float:
    return inner_r(e, puck) + e.wall


def motif_top(e: Envelope = ENVELOPE) -> float:
    """The z every lantern's cutouts stop at. The datum for the whole set.

    Measured DOWN from the rim rather than up from the floor, because the rim is
    what a person looking at a shelf of these actually sees. Motifs of different
    heights then share a top line instead of sharing a bottom line and staggering
    at the top, which is the more visible of the two.
    """
    return e.height - e.top_margin


def lit_window(e: Envelope = ENVELOPE, puck: Puck = PUCK) -> tuple[float, float]:
    """The band of outside-z within which an opening is actually lit.

    The floor lifts the puck, so every puck height is offset by `floor_t`. The
    bottom is hard: below it is opaque plastic and no design choice recovers
    it. The top is soft — it is the flame tip rather than the LED, because the
    tip glows and the paper liner spreads light past both.
    """
    return (
        e.floor_t + puck.emit_bottom + e.motif_bottom_margin,
        e.floor_t + puck.flame_top,
    )


def lit_window_height(e: Envelope = ENVELOPE, puck: Puck = PUCK) -> float:
    """Total canvas available to a motif. This is the scarce dimension."""
    lo, hi = lit_window(e, puck)
    return hi - lo
