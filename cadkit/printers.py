"""Printer and material profiles, and the config that selects one.

Every machine assumption in this repo funnels through here. A part asks
`printer.MIN_WALL` or `printer.usable_bed()`; what those mean depends on the
machine in front of *you*, not the one this repo was written on.

The active configuration lives in `printer.toml` at the repo root. It is
git-ignored — it describes your bench, not the project — and is written by
`cad setup`. A checked-in `printer.toml.example` documents the format.

On the numbers below
--------------------
Bed sizes and nozzle diameters are **nominal**: manufacturer figures, not
measurements. This repo is fussy about that distinction everywhere else and it
applies to itself. A profile gets you close enough to start; if a part is going
to land within a few millimetres of the bed edge, measure your own machine and
put the real number in `printer.toml`.

`max_overhang_deg` is the softest value here. It depends on cooling, speed,
material and geometry as much as on the machine, and the defaults are
conservative starting points rather than characterised limits. Print a
test tower and set it from what you actually get.
"""
from __future__ import annotations

import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path

CONFIG_NAME = "printer.toml"


@dataclass(frozen=True)
class Printer:
    key: str
    name: str
    bed_x: float
    bed_y: float
    bed_z: float
    nozzle: float = 0.4
    layer_h: float = 0.2
    bed_margin: float = 5.0      # unusable border: wiper, clips, poor adhesion
    max_overhang_deg: float = 50.0


@dataclass(frozen=True)
class Material:
    key: str
    name: str
    density: float               # g/cm3, for the mass estimate
    clearance_snug: float        # per side, printed pocket accepting a rigid part
    clearance_free: float
    max_overhang_deg: float | None = None   # overrides the printer's, if set


# --- profile library -------------------------------------------------------
# Nominal figures. Add your machine here (or just write the numbers straight
# into printer.toml — a profile is only a convenience).
PRINTERS: dict[str, Printer] = {
    p.key: p for p in [
        Printer("a1mini", "Bambu Lab A1 mini", 180, 180, 180),
        Printer("a1", "Bambu Lab A1", 256, 256, 256),
        Printer("p1s", "Bambu Lab P1S", 256, 256, 256),
        Printer("x1c", "Bambu Lab X1 Carbon", 256, 256, 256),
        Printer("mk4", "Prusa MK4", 250, 210, 220),
        Printer("mini", "Prusa MINI+", 180, 180, 180),
        Printer("ender3", "Creality Ender 3", 220, 220, 250),
        Printer("generic", "Generic FDM", 200, 200, 200),
    ]
}

MATERIALS: dict[str, Material] = {
    m.key: m for m in [
        Material("pla", "PLA", 1.24, 0.2, 0.4),
        Material("petg", "PETG", 1.27, 0.25, 0.45, max_overhang_deg=45.0),
        Material("abs", "ABS", 1.04, 0.25, 0.45, max_overhang_deg=45.0),
        Material("asa", "ASA", 1.07, 0.25, 0.45, max_overhang_deg=45.0),
        Material("tpu", "TPU 95A", 1.21, 0.3, 0.5, max_overhang_deg=40.0),
    ]
}

# Used when nothing is configured, so an unconfigured clone still imports and
# every command can explain itself instead of crashing on a missing file.
FALLBACK_PRINTER = PRINTERS["generic"]
FALLBACK_MATERIAL = MATERIALS["pla"]


@dataclass(frozen=True)
class Config:
    printer: Printer
    material: Material
    configured: bool             # False means nothing on disk; these are guesses
    path: Path | None = None


def config_path(root: Path) -> Path:
    return root / CONFIG_NAME


def load(root: Path) -> Config:
    """Read printer.toml, or return the fallback with `configured=False`.

    Never raises on a missing file. An unconfigured repo must still import, so
    that `cad setup` — and the advice telling you to run it — can work at all.
    """
    path = config_path(root)
    if not path.is_file():
        return Config(FALLBACK_PRINTER, FALLBACK_MATERIAL, configured=False)

    with path.open("rb") as fh:
        raw = tomllib.load(fh)

    p_raw = dict(raw.get("printer", {}))
    base = PRINTERS.get(p_raw.pop("profile", ""), FALLBACK_PRINTER)
    # Any key present in the file overrides the profile, so a stock machine with
    # a 0.6 nozzle is `profile = "a1mini"` plus one line.
    printer = Printer(**{**asdict(base), **{k: v for k, v in p_raw.items()
                                            if k in base.__dataclass_fields__}})

    m_raw = dict(raw.get("material", {}))
    mbase = MATERIALS.get(m_raw.pop("profile", ""), FALLBACK_MATERIAL)
    material = Material(**{**asdict(mbase), **{k: v for k, v in m_raw.items()
                                               if k in mbase.__dataclass_fields__}})

    return Config(printer, material, configured=True, path=path)


def write(root: Path, printer_key: str, material_key: str) -> Path:
    if printer_key not in PRINTERS:
        raise SystemExit(f"unknown printer '{printer_key}'. "
                         f"one of: {', '.join(PRINTERS)}")
    if material_key not in MATERIALS:
        raise SystemExit(f"unknown material '{material_key}'. "
                         f"one of: {', '.join(MATERIALS)}")
    p, m = PRINTERS[printer_key], MATERIALS[material_key]
    path = config_path(root)
    path.write_text(f'''# cadforge — your machine and material.
#
# Git-ignored: this describes your bench, not the project. Written by
# `cad setup`; edit freely.
#
# Every value below comes from a named profile in cadkit/printers.py. Any key
# you set here overrides the profile, so a stock machine with a different
# nozzle is one extra line.
#
# These are NOMINAL — manufacturer figures, not measurements. This repo is
# fussy about that distinction and it applies to itself. Measure your own bed
# before trusting a part that lands near its edge.

[printer]
profile = "{p.key}"          # {p.name}
# bed_x  = {p.bed_x}
# bed_y  = {p.bed_y}
# bed_z  = {p.bed_z}
# nozzle = {p.nozzle}
# layer_h = {p.layer_h}
# bed_margin = {p.bed_margin}       # unusable border around the plate
# max_overhang_deg = {p.max_overhang_deg}  # softest value here — set it from a test tower

[material]
profile = "{m.key}"          # {m.name}
# density = {m.density}            # g/cm3, for the mass estimate
# clearance_snug = {m.clearance_snug}
# clearance_free = {m.clearance_free}
''')
    return path


def describe(cfg: Config) -> str:
    p, m = cfg.printer, cfg.material
    ux, uy, uz = (p.bed_x - 2 * p.bed_margin, p.bed_y - 2 * p.bed_margin, p.bed_z)
    lines = [
        f"  printer   {p.name}  ({p.bed_x:.0f} × {p.bed_y:.0f} × {p.bed_z:.0f} mm bed, "
        f"{ux:.0f} × {uy:.0f} × {uz:.0f} usable)",
        f"  nozzle    {p.nozzle} mm, {p.layer_h} mm layers  "
        f"→ min wall {2 * p.nozzle:.1f} mm",
        f"  material  {m.name}  ({m.density} g/cm3)",
        f"  overhang  {m.max_overhang_deg or p.max_overhang_deg:.0f}° from horizontal",
    ]
    if not cfg.configured:
        lines.append("\n  \033[33m!! not configured — these are generic guesses\033[0m")
    return "\n".join(lines)
