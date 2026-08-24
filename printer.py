"""Your machine and material — the only module of shared constants.

Every value here is a property of the printer or the filament rather than a
design decision, which is what earns it global status. Nothing part-specific
belongs here; a part's numbers live in its own `Params` dataclass.

**These are configured, not hardcoded.** The values come from `printer.toml` at
the repo root, written by `cad setup` and git-ignored, because they describe
your bench rather than the project. A clone with no config falls back to a
generic FDM profile and says so on every build — `cad next` will tell you to
configure before anything else.

Parts use it exactly as before::

    import printer
    assert p.wall >= printer.MIN_WALL

Millimeters, degrees, and grams per cubic centimeter.
"""
from pathlib import Path

from cadkit import printers as _profiles

ROOT = Path(__file__).resolve().parent

CONFIG = _profiles.load(ROOT)
CONFIGURED = CONFIG.configured

_p = CONFIG.printer
_m = CONFIG.material

# --- the machine -----------------------------------------------------------
PRINTER_NAME = _p.name
BED_X = _p.bed_x
BED_Y = _p.bed_y
BED_Z = _p.bed_z

# Usable area is smaller than the bed: clips, the wiper and poor adhesion at the
# edges all eat into it.
BED_MARGIN = _p.bed_margin

NOZZLE = _p.nozzle
LAYER_H = _p.layer_h

# --- printability limits ---------------------------------------------------
# Steepest overhang that bridges reliably without support, measured from
# horizontal. A face tipping further than this needs support or a reorientation.
# The material can override the machine — PETG and ABS droop earlier than PLA.
MAX_OVERHANG_DEG = _m.max_overhang_deg or _p.max_overhang_deg

# Two-perimeter wall. Thinner than this and the slicer either drops to a single
# pass or gap-fills, both of which are weak.
MIN_WALL = 2 * NOZZLE

# --- material --------------------------------------------------------------
MATERIAL_NAME = _m.name
DENSITY = _m.density
PLA_DENSITY = DENSITY   # kept for parts written before materials were selectable

# --- fits ------------------------------------------------------------------
# Per-side clearance for a printed pocket to accept a nominal-size rigid part.
# A starting point, not a guarantee: the first number to adjust when something
# binds or rattles, and several parts have a documented reason to deviate. Check
# the part's notes.md before changing its local value.
CLEARANCE_SNUG = _m.clearance_snug
CLEARANCE_FREE = _m.clearance_free


def usable_bed() -> tuple[float, float, float]:
    """Printable envelope after edge margins."""
    return (BED_X - 2 * BED_MARGIN, BED_Y - 2 * BED_MARGIN, BED_Z)


def describe() -> str:
    return _profiles.describe(CONFIG)
