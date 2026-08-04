"""Automatic printability checks.

Scope, stated up front because a check report that looks exhaustive is worse
than none: these are the cheap, general checks that apply to every part. They
catch the errors that are embarrassing to discover at the printer — a model
that does not fit the bed, a solid that is not manifold, a face that will droop.

What is deliberately NOT checked here:

  * **True minimum wall thickness.** Measuring the thinnest section of an
    arbitrary solid is expensive and unreliable. Thickness invariants belong in
    the part's own `check()` as an assertion against the numbers that produced
    them. A part that knows its wall is a ring between N openings can assert the
    rib width it computed; a generic check cannot, and would give false
    confidence in exchange for saying nothing useful.
  * **Whether the shape is the shape you meant.** That is what the renders are
    for. No geometric predicate substitutes for looking.

Every result carries a severity. FAIL means do not print. WARN means look at it
and decide — several are legitimate for a given part, which is why they do not
block.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import printer


class Severity(str, Enum):
    OK = "ok"
    WARN = "warn"
    FAIL = "fail"


@dataclass(frozen=True)
class Result:
    name: str
    severity: Severity
    detail: str

    def __str__(self) -> str:
        mark = {Severity.OK: "  ok ", Severity.WARN: "WARN ", Severity.FAIL: "FAIL "}
        return f"{mark[self.severity]} {self.name:<18} {self.detail}"


def check_valid(part) -> Result:
    """Is this a well-formed solid at all? A boolean that went wrong can leave
    a shape that renders plausibly and slices into garbage."""
    try:
        # build123d exposes this as a property; older/other versions as a
        # method. Accept either rather than pinning to one spelling.
        ok = part.is_valid
        if callable(ok):
            ok = ok()
    except Exception as exc:
        return Result("validity", Severity.FAIL, f"validity check raised: {exc}")
    if not ok:
        return Result("validity", Severity.FAIL, "shape is not a valid solid")
    return Result("validity", Severity.OK, "valid solid")


def check_volume(part) -> Result:
    vol = part.volume
    if vol <= 0:
        return Result("volume", Severity.FAIL, "zero or negative volume — nothing to print")
    grams = vol / 1000.0 * printer.PLA_DENSITY
    return Result("volume", Severity.OK, f"{vol / 1000:.1f} cm3 ≈ {grams:.0f} g PLA (solid)")


def check_bed(part) -> Result:
    """Does it fit the A1 mini, in the orientation as modeled?"""
    bb = part.bounding_box()
    dims = (bb.size.X, bb.size.Y, bb.size.Z)
    ux, uy, uz = printer.usable_bed()
    fits = dims[0] <= ux and dims[1] <= uy and dims[2] <= uz
    rotated = dims[1] <= ux and dims[0] <= uy and dims[2] <= uz
    size = f"{dims[0]:.1f} × {dims[1]:.1f} × {dims[2]:.1f} mm"
    if fits:
        return Result("bed", Severity.OK, f"{size} fits {ux:.0f} × {uy:.0f} × {uz:.0f}")
    if rotated:
        return Result("bed", Severity.WARN, f"{size} fits only rotated 90° on the plate")
    return Result("bed", Severity.FAIL, f"{size} exceeds usable bed {ux:.0f} × {uy:.0f} × {uz:.0f}")


def check_overhangs(part, min_area: float = 4.0) -> Result:
    """Flag downward-facing planar faces steeper than the printer bridges.

    Only planar faces are judged. A cylindrical hole's underside is a curved
    face that self-supports progressively and is normally fine, so including
    curved faces produces noise on every part with a hole in it. The floor
    itself (the face resting on the plate) is excluded — it is not an overhang.
    """
    from build123d import Plane

    bb = part.bounding_box()
    zmin = bb.min.Z
    limit = -abs(printer.MAX_OVERHANG_DEG)

    bad: list[tuple[float, float]] = []
    for face in part.faces():
        try:
            if not isinstance(face.geom_type, type(None)) and face.geom_type.name != "PLANE":
                continue
        except AttributeError:
            if str(getattr(face, "geom_type", "")).upper().find("PLANE") < 0:
                continue
        try:
            nz = face.normal_at().Z
            area = face.area
            fz = face.center().Z
        except Exception:
            continue
        if area < min_area:
            continue
        if abs(fz - zmin) < 1e-6 and nz < 0:
            continue                      # the build-plate face
        if nz >= 0:
            continue                      # faces up; not an overhang
        import math
        angle = math.degrees(math.asin(max(-1.0, min(1.0, nz))))
        if angle <= limit:
            bad.append((angle, area))

    if not bad:
        return Result("overhangs", Severity.OK,
                      f"no planar overhang steeper than {printer.MAX_OVERHANG_DEG:.0f}°")
    bad.sort()
    worst, area = bad[0]
    return Result("overhangs", Severity.WARN,
                  f"{len(bad)} planar overhang face(s); worst {abs(worst):.0f}° "
                  f"below horizontal, {area:.0f} mm2 — supports or reorient")


def check_thin_proxy(part) -> Result:
    """A *proxy* for bulk thinness, not a min-wall check. See module docstring.

    2·volume/area is the average thickness of a slab of the same volume and
    surface area. It says nothing about the thinnest point, and it is reported
    as information rather than as a pass or a fail.
    """
    try:
        avg = 2.0 * part.volume / part.area
    except Exception:
        return Result("thickness", Severity.OK, "not computed")
    return Result("thickness", Severity.OK,
                  f"mean section ≈ {avg:.1f} mm (proxy only; min wall is NOT checked)")


ALL_CHECKS = (check_valid, check_volume, check_bed, check_overhangs, check_thin_proxy)


def run(part) -> list[Result]:
    out: list[Result] = []
    for fn in ALL_CHECKS:
        try:
            out.append(fn(part))
        except Exception as exc:
            out.append(Result(fn.__name__, Severity.WARN, f"check errored: {exc}"))
    return out


def worst(results: list[Result]) -> Severity:
    if any(r.severity is Severity.FAIL for r in results):
        return Severity.FAIL
    if any(r.severity is Severity.WARN for r in results):
        return Severity.WARN
    return Severity.OK
