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
    grams = vol / 1000.0 * printer.DENSITY
    return Result("volume", Severity.OK,
                  f"{vol / 1000:.1f} cm3 ≈ {grams:.0f} g {printer.MATERIAL_NAME} (solid)")


def check_bed(part) -> Result:
    """Does it fit the configured machine, in the orientation as modeled?"""
    bb = part.bounding_box()
    dims = (bb.size.X, bb.size.Y, bb.size.Z)
    ux, uy, uz = printer.usable_bed()
    fits = dims[0] <= ux and dims[1] <= uy and dims[2] <= uz
    rotated = dims[1] <= ux and dims[0] <= uy and dims[2] <= uz
    size = f"{dims[0]:.1f} × {dims[1]:.1f} × {dims[2]:.1f} mm"
    if fits:
        return Result("bed", Severity.OK,
                      f"{size} fits {ux:.0f} × {uy:.0f} × {uz:.0f} "
                      f"({printer.PRINTER_NAME})")
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


# check_islands is defined below; the tuple is assembled after it.


# --- floating islands ------------------------------------------------------
# The check this module most needed and did not have, added after a part passed
# everything here and then showed floating regions in the slicer.
#
# There are two different things a naive "unsupported material" measure lumps
# together, and only one of them is fatal:
#
#   overhang   material attached, on its own layer, to material that IS
#              supported. It leans out and droops. Usually survives.
#   ISLAND     a blob of material on a layer with no path, along that layer, to
#              anything supported. It is extruded into open air and falls.
#
# Measured as a percentage of material the two are indistinguishable: a part
# that printed clean scored 0.51% unsupported and a part that had to be
# cancelled scored 0.47%. Counting islands separated them completely — zero
# against ten. `check_overhangs` above does not catch this either: it looks for
# planar faces below the angle limit, and an island can be bounded entirely by
# curved or steep faces.
#
# This is NOT a prohibition, and the severity is WARN for that reason. Islands
# are printable — with supports. What the check exists to do is surface the
# DECISION early, while the shape can still be changed cheaply, rather than at
# the slicer once the modelling is done:
#
#   * enable supports, and accept the cleanup and whatever marks removal leaves
#     on surfaces you care about; or
#   * reshape so the feature is anchored, and print it clean.
#
# Which is right depends entirely on the part. A structural bracket does not
# care about support scars; a lantern whose inner wall is backlit through its
# own openings very much does.
#
# Method: ray-cast the tessellated mesh into a column occupancy grid, one row
# per print layer in z, then propagate support upward. Approximate by
# construction — the grid is coarser than the extrusion in x/y — so it names
# where to look rather than pretending to be the slicer.
_ISLAND_XY = 0.4          # grid pitch across the plate, mm
_ISLAND_MAX_COLUMNS = 400 # coarsen rather than crawl on a big part
_ISLAND_MAX_CELLS = 60_000_000


def check_islands(part) -> Result:
    import numpy as np

    from .render import _tessellate

    V, T = _tessellate(part)
    if len(T) == 0:
        return Result("islands", Severity.OK, "no geometry")

    lo, hi = V.min(0), V.max(0)
    span = hi - lo
    pitch = max(_ISLAND_XY,
                float(max(span[0], span[1])) / _ISLAND_MAX_COLUMNS)
    layer = printer.LAYER_H
    nx = max(2, int(span[0] / pitch) + 2)
    ny = max(2, int(span[1] / pitch) + 2)
    nz = max(2, int(span[2] / layer) + 2)
    # Coarsen across the plate until the grid fits, rather than declining to
    # look. Skipping was the old behaviour and it is the wrong answer to a big
    # part: this castle grew past the limit mid-design and quietly stopped being
    # checked for a dozen builds, over exactly the run in which its towers were
    # being moved around — which is when islands appear. A coarse answer names
    # where to look; no answer reads as nothing to find.
    #
    # Only x and y coarsen. The z pitch is the layer height and an island is a
    # per-layer fact, so coarsening z would change what is being asked.
    while nx * ny * nz > _ISLAND_MAX_CELLS:
        pitch *= 1.25
        nx = max(2, int(span[0] / pitch) + 2)
        ny = max(2, int(span[1] / pitch) + 2)

    # Column centres, offset half a cell so a ray never grazes a vertex.
    gx = lo[0] + (np.arange(nx) + 0.5) * pitch
    gy = lo[1] + (np.arange(ny) + 0.5) * pitch

    A, B, C = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    occ = np.zeros((nz, ny, nx), dtype=bool)

    # Ray-cast straight up each column: every triangle the ray crosses gives a
    # z, and sorted crossings pair up into inside-intervals (even-odd rule).
    # Done per triangle rather than per ray so it stays vectorised.
    x0 = np.minimum(np.minimum(A[:, 0], B[:, 0]), C[:, 0])
    x1 = np.maximum(np.maximum(A[:, 0], B[:, 0]), C[:, 0])
    y0 = np.minimum(np.minimum(A[:, 1], B[:, 1]), C[:, 1])
    y1 = np.maximum(np.maximum(A[:, 1], B[:, 1]), C[:, 1])

    crossings = [[[] for _ in range(nx)] for _ in range(ny)]
    for t in range(len(T)):
        ia0 = max(0, int((x0[t] - lo[0]) / pitch) - 1)
        ia1 = min(nx - 1, int((x1[t] - lo[0]) / pitch) + 1)
        ib0 = max(0, int((y0[t] - lo[1]) / pitch) - 1)
        ib1 = min(ny - 1, int((y1[t] - lo[1]) / pitch) + 1)
        if ia1 < ia0 or ib1 < ib0:
            continue
        a, b, c = A[t], B[t], C[t]
        # barycentric test for the sub-grid of columns over this triangle
        px, py = np.meshgrid(gx[ia0:ia1 + 1], gy[ib0:ib1 + 1])
        d = ((b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1]))
        if abs(d) < 1e-12:
            continue
        w0 = ((b[1] - c[1]) * (px - c[0]) + (c[0] - b[0]) * (py - c[1])) / d
        w1 = ((c[1] - a[1]) * (px - c[0]) + (a[0] - c[0]) * (py - c[1])) / d
        w2 = 1.0 - w0 - w1
        inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        if not inside.any():
            continue
        z = w0 * a[2] + w1 * b[2] + w2 * c[2]
        for jj, ii in zip(*np.nonzero(inside)):
            crossings[ib0 + jj][ia0 + ii].append(float(z[jj, ii]))

    zk = lo[2] + (np.arange(nz) + 0.5) * layer
    for j in range(ny):
        for i in range(nx):
            zs = crossings[j][i]
            if len(zs) < 2:
                continue
            zs.sort()
            for k in range(0, len(zs) - 1, 2):
                occ[(zk >= zs[k]) & (zk <= zs[k + 1]), j, i] = True

    if not occ.any():
        return Result("islands", Severity.OK, "no geometry")

    # Support propagation, bottom up. A cell is supported if something below it
    # is, within the lateral creep the overhang limit allows; then any connected
    # component on that layer touching a supported cell is carried along, since
    # material reaches sideways to its anchors.
    from scipy import ndimage

    import math
    creep = layer / math.tan(math.radians(printer.MAX_OVERHANG_DEG))
    k = max(1, int(round(creep / pitch)))
    struct = np.ones((3, 3), bool)
    dil = np.ones((2 * k + 1, 2 * k + 1), bool)

    islands = 0
    worst_area = 0.0
    worst_z = 0.0
    sup = occ[0].copy()
    for z in range(1, nz):
        reach = ndimage.binary_dilation(sup, dil)
        s_now = occ[z] & reach
        lab, n = ndimage.label(occ[z], structure=struct)
        if n:
            hit = np.zeros(n + 1, bool)
            ids = lab[s_now]
            hit[ids[ids > 0]] = True
            for idx in range(1, n + 1):
                if hit[idx]:
                    s_now |= lab == idx
                else:
                    islands += 1
                    a = float((lab == idx).sum()) * pitch * pitch
                    if a > worst_area:
                        worst_area, worst_z = a, lo[2] + z * layer
        sup = s_now

    if islands == 0:
        return Result("islands", Severity.OK,
                      f"no floating islands (nothing starts in mid-air), "
                      f"at {pitch:.2f} mm grid")
    return Result(
        "islands", Severity.WARN,
        f"{islands} floating island(s), largest {worst_area:.1f} mm2 at "
        f"z={worst_z:.1f} — material starting in mid-air with nothing under it "
        f"and no path sideways to an anchor. NOT an overhang: it cannot droop "
        f"into place. This part needs supports, or reshaping so the feature is "
        f"anchored. Decide which — see the surface finish note in the docs."
    )


ALL_CHECKS = (check_valid, check_volume, check_bed, check_overhangs,
              check_thin_proxy, check_islands)


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
