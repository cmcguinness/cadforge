"""Facts about the machine and the material — not about any one part.

This is the *only* module of shared constants, and it earns that status because
every value here is a property of the printer or the filament rather than a
design decision. Nothing part-specific belongs here; a part's numbers live in
its own `Params` dataclass. (The old repo's `dimensions.py` blurred that line
and grew into a junk drawer that every part star-imported.)

Millimeters, degrees, and grams per cubic centimeter.
"""

# --- Bambu Lab A1 mini -----------------------------------------------------
BED_X = 180.0
BED_Y = 180.0
BED_Z = 180.0

# Usable area is smaller than the bed: the wiper and the front lip eat into it,
# and parts right at the edge get poor first-layer adhesion.
BED_MARGIN = 5.0

NOZZLE = 0.4
LAYER_H = 0.2

# --- printability limits ---------------------------------------------------
# Steepest overhang the A1 mini bridges reliably without support, measured from
# vertical. A face whose normal tips more than this below horizontal needs
# support or a reorientation.
MAX_OVERHANG_DEG = 50.0

# Two-perimeter wall at a 0.4 nozzle. Thinner than this and the slicer either
# drops the wall to a single pass or gap-fills it, both of which are weak.
MIN_WALL = 2 * NOZZLE

# --- material --------------------------------------------------------------
PLA_DENSITY = 1.24  # g/cm^3

# --- fits ------------------------------------------------------------------
# Per-side clearance for a printed pocket to accept a nominal-size rigid part.
# A starting point, not a guarantee: it is the first number to adjust when
# something binds or rattles, and several parts have a documented reason to
# deviate. Check the part's notes.md before changing its local value.
CLEARANCE_SNUG = 0.2
CLEARANCE_FREE = 0.4


def usable_bed() -> tuple[float, float, float]:
    """Printable envelope after edge margins."""
    return (BED_X - 2 * BED_MARGIN, BED_Y - 2 * BED_MARGIN, BED_Z)
