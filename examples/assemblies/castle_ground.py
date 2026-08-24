"""The contract between `castle` and `castle_base`: where the castle meets the ground.

The castle is a printed, published, 178 mm object. The base has to seat it, and a
seat that is wrong by a millimetre is a seat that does not accept the part — with
no way to find out except by spending eight hours of printer time twice.

So the castle's ground plan lives here as **numbers both parts read**, rather than
being measured off the solid by whichever part needs it. `castle.check()` asserts
its own footprint against these values, so the two cannot drift apart silently:
change the castle's plan and the castle's own build fails, naming this file.

Why not derive the footprint from the castle solid directly? Because building the
castle takes eighty seconds — the mortar grooves are thousands of boolean cuts —
and a base whose every iteration costs eighty seconds is a base nobody iterates.
The assertion buys the same guarantee for the price of a build that was happening
anyway.

Coordinates are the castle's own: **x across, 0 = the curtain wall's centre; y back
from the front face; z up from the castle's underside.** The base adopts them
unchanged, which is why nothing here needs a transform.
"""

# --- the ground plan -------------------------------------------------------
#
#            y
#            ^        +-----------------------------+   y = 82  (back, open)
#            |        |                             |
#            |        |          C A S T L E        |
#            |        |                             |
#            |    ____+--------+       +------------+   y = 0.35
#            |   (    |  gate  |       |   ...       )  <- turret discs, r 9
#            |    ‾‾‾‾+--------+‾‾‾‾‾‾‾+‾‾‾‾‾‾‾‾‾‾‾‾    y = 0 / -9 at the bulge
#            +--------------------------------------> x
#                  -63.65      -15   19        63.65

WALL_HALF_W = 63.65
"""Half the curtain wall, which is the castle's widest square-cut mass."""

WALL_Y0 = 0.35
WALL_Y1 = 82.0
"""Front and back of the main mass. The back is open — the castle is a facade with
chambers behind it — but its footprint is closed, so the base sees a rectangle."""

SURROUND_HALF = (-15.0, 19.0)
SURROUND_Y0 = 0.0
"""The gate's plain-stone surround stands 0.35 mm proud of the curtain wall. It is
a third of a millimetre and it is still in the contract, because a seat cut to the
wall line alone would foul it and hold the castle off its floor by that much."""

TURRET_X = 58.0
TURRET_R = 9.0
"""The two front corner turrets, as full discs centred ON the wall's front line.
225° of each disc stands proud, which is what puts the castle's extreme corners at
x = ±67 and its front edge at y = -9 — neither of which is a face of anything, so
both are easy to miss when reading the elevation."""

EXTENT_HALF_W = TURRET_X + TURRET_R          # 67.0
EXTENT_Y0 = -TURRET_R                        # -9.0
EXTENT_Y1 = WALL_Y1                          # 82.0

FLOOR_T = 2.4
"""The castle's base slab. **The gate threshold sits on top of it**, so a bridge
that lands level with the ground outside lands 2.4 mm below the floor the gate
opens onto — unless the seat is sunk to take the difference out. That is the whole
reason `seat_depth` exists in the base and why it is not a free choice."""

# --- the gate --------------------------------------------------------------

GATE_X = 2.0
GATE_W = 28.0
"""**The gate is not on the castle's centreline.** The whole face — eyes, mouth and
all — is built about x = +2, because the castle is haunted and owes nothing a
mirror. A drawbridge centred on the base would sit two millimetres off its own
doorway, which is exactly the kind of error that looks like a rendering artefact
until the object is in your hand."""

GATE_Z0 = FLOOR_T
GATE_Z1 = 35.0
"""The opening's sill and head, above the castle's underside."""

# --- the scale -------------------------------------------------------------

FOOT = 164.0 / 120.0
"""Millimetres to the foot. The castle is 164 mm to the tip of its spire and
reads as a keep of about 120 feet.

It belongs in the contract because **the ground has to be at the castle's
scale or the castle stops being big.** A moat sized by eye against the nozzle
comes out as a gutter around a model; the same trench converted from feet comes
out as water. This is the same argument that put a foot in the castle in the
first place — every architectural size there had been picked against the nozzle
until it existed, which is how the parapets ended up as tall as a two-storey
building."""
