"""Headless rendering: tessellate -> numpy z-buffer -> PNG.

Why this exists
---------------
The old repo reviewed parts through `ocp_vscode`, which pushes geometry over a
websocket to a browser tab. Geometry is never stored, so a part built with no
tab attached succeeds silently and displays nothing — and, more importantly, an
agent driving the repo can never see the result at all. Every "visual review"
was a human reading a screen.

This module makes review an artifact. It writes PNG files that anything can
open, including a model that can only read files.

Implementation note: the installed OCP wheel is `cadquery-ocp-novtk`, so there
is no VTK offscreen renderer and no OpenGL context available. Rather than add a
heavy graphics dependency, this is a small painter's-algorithm rasterizer over
the tessellated triangles: numpy and Pillow only, ~0.1 s for a typical part.
It produces shaded solids, not photographs. That is the right fidelity for
answering "is this the shape I meant?".
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import time

from PIL import Image, ImageDraw, ImageFont

# Tessellation tolerance in mm. Finer costs render time and buys nothing at
# these image sizes; 0.05 keeps a 20 mm circle visually smooth.
TESS_TOL = 0.05

BG = 246
INK = 40


@dataclass(frozen=True)
class View:
    """A named camera direction. `eye` is a direction, not a position — the
    camera is orthographic and framed to the part, so only the direction and
    the up-vector matter."""

    name: str
    eye: tuple[float, float, float]
    up: tuple[float, float, float] = (0.0, 0.0, 1.0)


# The standard set. Iso reads shape; front/right/top read proportion and catch
# the asymmetries an iso view hides.
STANDARD_VIEWS = (
    View("iso", (1.0, -1.0, 0.8)),
    View("front", (0.0, -1.0, 0.0)),
    View("right", (1.0, 0.0, 0.0)),
    View("top", (0.0, 0.0, 1.0), up=(0.0, 1.0, 0.0)),
)


def _basis(eye, up) -> np.ndarray:
    """Rows are the camera's right/up/backward axes in world space."""
    # `f` is the camera's *backward* axis: it points from the part toward the
    # eye, so a point's f-component increases as it gets nearer the viewer and
    # can be used directly as the depth value.
    f = np.asarray(eye, float)
    f /= np.linalg.norm(f)
    up = np.asarray(up, float)
    if abs(np.dot(f, up)) > 0.999:  # degenerate: looking straight along `up`
        up = np.array([0.0, 1.0, 0.0])
    r = np.cross(up, f)
    r /= np.linalg.norm(r)
    u = np.cross(f, r)
    return np.stack([r, u, f])


def _tessellate(shape) -> tuple[np.ndarray, np.ndarray]:
    verts, tris = shape.tessellate(TESS_TOL)
    V = np.array([[v.X, v.Y, v.Z] for v in verts], dtype=float)
    T = np.array(tris, dtype=np.int64)
    return V, T


def render(shape, view: View, size: int = 520, margin: float = 1.12) -> Image.Image:
    """Orthographic shaded render of `shape` from `view`, framed to fill."""
    V, T = _tessellate(shape)
    if len(T) == 0:
        return Image.new("L", (size, size), BG)

    R = _basis(view.eye, view.up)
    C = V @ R.T                     # camera space; +Z is toward the eye

    lo, hi = C[:, :2].min(0), C[:, :2].max(0)
    span = max((hi - lo).max(), 1e-9) * margin
    ctr = (hi + lo) / 2
    px = (C[:, 0] - ctr[0]) / span * size + size / 2
    py = size / 2 - (C[:, 1] - ctr[1]) / span * size

    P = np.stack([px, py, C[:, 2]], axis=1)[T]
    a, b, c = P[:, 0], P[:, 1], P[:, 2]
    area = (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (c[:, 0] - a[:, 0]) * (b[:, 1] - a[:, 1])

    # Flat shading from a headlight plus a soft fill from above-left. Facet
    # normals are used with abs(), so triangle winding cannot invert a face —
    # the z-buffer already decides what is visible.
    n = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    n = np.divide(n, ln, out=np.zeros_like(n), where=ln > 0)
    nc = n @ R.T
    lit = np.abs(nc[:, 2]) * 0.62 + np.clip(nc[:, 1], 0, 1) * 0.18 \
        + np.clip(-nc[:, 0], 0, 1) * 0.08 + 0.16
    shade = np.clip(lit, 0.0, 1.0) * 232.0

    img = np.full((size, size), float(BG))
    # Nearer means larger camera-space z, so the buffer starts at -inf.
    zbuf = np.full((size, size), -np.inf)
    # Per-pixel facet normal, kept so edges can be found afterwards. Flat
    # shading alone cannot distinguish a hole from a flat face when both catch
    # the light equally — the `top` view of an open box reads as a solid
    # square. Creases and silhouettes are what make a render reviewable.
    nbuf = np.zeros((size, size, 3))

    for i in range(len(T)):
        if area[i] == 0.0:
            continue
        sgn = 1.0 if area[i] > 0 else -1.0
        tri = P[i]
        x0 = max(int(tri[:, 0].min()), 0)
        x1 = min(int(tri[:, 0].max()) + 2, size)
        y0 = max(int(tri[:, 1].min()), 0)
        y1 = min(int(tri[:, 1].max()) + 2, size)
        if x0 >= x1 or y0 >= y1:
            continue

        gx, gy = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        (ax, ay), (bx, by), (cx, cy) = tri[0, :2], tri[1, :2], tri[2, :2]
        w0 = (bx - ax) * (gy - ay) - (by - ay) * (gx - ax)
        w1 = (cx - bx) * (gy - by) - (cy - by) * (gx - bx)
        w2 = (ax - cx) * (gy - cy) - (ay - cy) * (gx - cx)
        inside = (w0 * sgn >= 0) & (w1 * sgn >= 0) & (w2 * sgn >= 0)
        if not inside.any():
            continue

        z = (w1 * tri[0, 2] + w2 * tri[1, 2] + w0 * tri[2, 2]) / area[i]
        zsub = zbuf[y0:y1, x0:x1]
        win = inside & (z > zsub)
        zsub[win] = z[win]
        img[y0:y1, x0:x1][win] = shade[i]
        nbuf[y0:y1, x0:x1][win] = nc[i]

    img = _draw_edges(img, zbuf, nbuf, span / size)
    return Image.fromarray(img.astype(np.uint8), mode="L")


def _draw_edges(img, zbuf, nbuf, mm_per_px: float, crease_deg: float = 22.0):
    """Darken depth discontinuities and creases.

    Two kinds of line, found by comparing each pixel with its right and lower
    neighbour:

      * a **depth jump** — a silhouette, or the lip of a hole. The threshold is
        in millimetres of model space, so it does not change meaning when the
        image size or the part size changes.
      * a **crease** — neighbouring pixels on faces that meet at an angle. This
        is what draws the corner between two flat faces that happen to be lit
        almost identically.

    Background pixels have -inf depth, so the object's outer silhouette falls
    out of the depth test for free.
    """
    solid = np.isfinite(zbuf)
    z = np.where(solid, zbuf, np.nan)
    jump = max(mm_per_px * 3.0, 1e-6)

    edge = np.zeros(zbuf.shape, dtype=bool)
    for ax in (0, 1):
        dz = np.abs(np.diff(z, axis=ax))
        big = np.nan_to_num(dz, nan=0.0) > jump
        # a solid/background boundary is a silhouette
        sil = np.diff(solid.astype(np.int8), axis=ax) != 0
        m = big | sil

        dn = np.sum(np.take(nbuf, np.arange(nbuf.shape[ax] - 1), axis=ax)
                    * np.take(nbuf, np.arange(1, nbuf.shape[ax]), axis=ax), axis=2)
        both = np.take(solid, np.arange(solid.shape[ax] - 1), axis=ax) & \
            np.take(solid, np.arange(1, solid.shape[ax]), axis=ax)
        crease = both & (dn < np.cos(np.radians(crease_deg)))

        m = m | crease
        pad = [(0, 0), (0, 0)]
        pad[ax] = (0, 1)
        edge |= np.pad(m, pad)
        pad[ax] = (1, 0)
        edge |= np.pad(m, pad)

    out = img.copy()
    out[edge] = np.minimum(out[edge], INK + 45)
    return out


def section(shape, plane_normal: str = "x"):
    """Half the solid, cut away so the interior is visible.

    Internal geometry is exactly what a shaded exterior render cannot show, and
    exactly where the expensive mistakes live — a pocket that is too shallow, a
    well whose floor is in the wrong place. Returns None if the cut fails.
    """
    from build123d import Plane, Keep, split

    planes = {"x": Plane.YZ, "y": Plane.XZ, "z": Plane.XY}
    try:
        return split(shape, bisect_by=planes[plane_normal], keep=Keep.BOTTOM)
    except Exception:
        return None


GRID_N = 8          # cells across and down
GRID_INK = 150      # light enough to read the model through


def _font(size: int):
    try:
        return ImageFont.load_default(size)
    except TypeError:      # Pillow < 10 has no size argument
        return ImageFont.load_default()


def _grid(img: Image.Image, n: int = GRID_N) -> None:
    """Overlay a lettered/numbered reference grid, in place.

    So a review can say "the flat face at C6" instead of describing where it is
    in prose. Reviewing is the step that costs a human their attention, and a
    sentence spent locating something is a sentence not spent judging it.

    Columns are letters left to right, rows are numbers top to bottom — reading
    order, so nobody has to work out the convention. Drawn in mid-grey rather
    than black: it must be legible over both the background and the shaded
    solid, without competing with the silhouette lines that carry the shape.
    """
    d = ImageDraw.Draw(img)
    w, h = img.size
    step_x, step_y = w / n, h / n
    font = _font(12)
    for i in range(1, n):
        x, y = round(i * step_x), round(i * step_y)
        d.line([(x, 0), (x, h)], fill=GRID_INK)
        d.line([(0, y), (w, y)], fill=GRID_INK)
    for i in range(n):
        d.text((i * step_x + 3, h - 14), chr(ord("A") + i), fill=GRID_INK, font=font)
        d.text((3, i * step_y + 3), str(i + 1), fill=GRID_INK, font=font)


def _label(img: Image.Image, text: str) -> Image.Image:
    out = img.convert("L")
    _grid(out)
    d = ImageDraw.Draw(out)
    d.text((20, 6), text, fill=INK, font=_font(16))   # clear of the row labels
    return out


def contact_sheet(shape, views=STANDARD_VIEWS, size: int = 520,
                  section_normal: str | None = "x") -> tuple[Image.Image, dict]:
    """One image with every standard view, plus a cutaway. Returns the sheet
    and the individual frames so callers can write both."""
    frames: dict[str, Image.Image] = {v.name: render(shape, v, size) for v in views}

    if section_normal:
        half = section(shape, section_normal)
        if half is not None:
            frames["section"] = render(half, View("section", (1.0, -1.0, 0.35)), size)

    names = list(frames)
    cols = min(3, len(names))
    rows = (len(names) + cols - 1) // cols

    # A banner across the top carrying the time this sheet was made.
    #
    # Every generated image gets one. A render is the artifact a review is read
    # against, and an undated one is indistinguishable from a stale one — which
    # is not hypothetical: a sheet from before a change has already been read as
    # though it showed the change. The cost is 22 pixels.
    band = 22
    sheet = Image.new("L", (cols * size, rows * size + band), BG)
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.load_default(15)
    except TypeError:
        font = ImageFont.load_default()
    d.text((10, 4), time.strftime("%Y-%m-%d %H:%M:%S"), fill=INK, font=font)

    # Label and grid once, then use the same images for the sheet and for the
    # individual files — otherwise front.png has no grid and a review that
    # opened it could not use the coordinates the sheet taught them.
    marked = {name: _label(img, name) for name, img in frames.items()}
    for i, name in enumerate(names):
        sheet.paste(marked[name], ((i % cols) * size, band + (i // cols) * size))
    return sheet, marked


def write_views(shape, outdir: Path, size: int = 520,
                section_normal: str | None = "x") -> list[Path]:
    """Render the standard set into `outdir`. Returns the paths written, sheet
    first — that is the one worth opening."""
    outdir.mkdir(parents=True, exist_ok=True)
    sheet, frames = contact_sheet(shape, size=size, section_normal=section_normal)

    written = [outdir / "sheet.png"]
    sheet.save(written[0])
    for name, img in frames.items():
        p = outdir / f"{name}.png"
        img.save(p)
        written.append(p)
    return written
