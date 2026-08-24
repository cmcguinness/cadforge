"""Trace the owl and its branch into normalised outlines.

Run standalone; writes `owl_outline.py` next to it. Not imported by model.py —
the traced polygons are generated once and read as data, so a build never
depends on an image file.

The artwork carries two subjects in two colours: the owl in **black**, the
branch in **red**. Both are the *object* here, not a hole — this is a flat
standee cut to its own outline, so black is material and white is air. The
three enclosed white regions inside the owl (two eyes and the beak) are
apertures.

Unlike the lantern motifs, nothing here is fighting the nozzle: 99.6% of the
owl survives three extrusion widths at every size from 100 mm up. So there is
no `MERGE` step — no closing radius, no rescuing of thin features. The
feathered outline is traced as drawn, because a flat-printed plate has no layer
that a spike could fail on.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

SRC = Path(__file__).parent / "inspiration" / "owl.png"

RDP_EPS = 1.5
"""Douglas-Peucker tolerance, in source pixels.

Tighter than the lanterns' 3.0 because this outline is the whole object rather
than a small motif, and its character is in the feather lobes. At 1254 px for a
140 mm owl that is about 0.17 mm on the finished part — well under what the
nozzle draws, so nothing is lost that could have been printed.
"""

MIN_REGION = 50
"""Ignore enclosed white regions smaller than this, in pixels.

The supplied artwork carries four single-pixel antialias flecks and one
one-pixel enclosed region. Left in, each becomes a pinhole through the plate or
a detached speck of geometry. They are noise from the generator, not design.
"""


def masks(path):
    """Split the artwork into (owl, branch) boolean masks."""
    a = np.array(Image.open(path).convert("RGBA")).astype(int)
    r, g, b, alpha = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    opaque = alpha > 128
    owl = opaque & (r < 100) & (g < 100) & (b < 100)
    branch = opaque & (r > 150) & (g < 100) & (b < 100)
    return owl, branch


def largest_piece(mask):
    """Keep only the biggest connected component, dropping antialias flecks."""
    lbl, n = ndimage.label(mask)
    if n <= 1:
        return mask, 0
    sizes = ndimage.sum(mask, lbl, range(1, n + 1))
    keep = int(np.argmax(sizes)) + 1
    return lbl == keep, n - 1


def apertures(mask):
    """Enclosed white regions inside `mask`, largest first."""
    holes, n = ndimage.label(~mask)
    edge = set(holes[0, :]) | set(holes[-1, :]) | set(holes[:, 0]) | set(holes[:, -1])
    out = []
    for k in range(1, n + 1):
        if k in edge:
            continue
        size = int(ndimage.sum(~mask, holes, k))
        if size < MIN_REGION:
            continue
        out.append((size, holes == k))
    out.sort(key=lambda t: -t[0])
    return out


def trace(mask):
    """Moore-neighbour boundary walk, clockwise, with an explicit backtrack."""
    pad = np.pad(mask, 1)
    ys, xs = np.nonzero(pad)
    y0 = int(ys.min())
    start = (y0, int(xs[ys == y0].min()))
    nbrs = [(0, -1), (-1, -1), (-1, 0), (-1, 1),
            (0, 1), (1, 1), (1, 0), (1, -1)]
    out, c, b = [start], start, 0
    for _ in range(8 * int(pad.sum()) + 1000):
        for k in range(1, 9):
            d = (b + k) % 8
            ny, nx = c[0] + nbrs[d][0], c[1] + nbrs[d][1]
            if pad[ny, nx]:
                b, c = (d + 4) % 8, (ny, nx)
                out.append(c)
                break
        else:
            break
        if c == start:
            break
    return [(x - 1, y - 1) for y, x in out]


def rdp(points, eps):
    if len(points) < 3:
        return points
    p0, p1 = np.array(points[0], float), np.array(points[-1], float)
    seg = p1 - p0
    L = np.hypot(*seg)
    P = np.array(points, float)
    V = P - p0
    d = (np.hypot(*V.T) if L == 0
         else np.abs(seg[0] * V[:, 1] - seg[1] * V[:, 0]) / L)
    i = int(np.argmax(d))
    if d[i] > eps:
        return rdp(points[:i + 1], eps)[:-1] + rdp(points[i:], eps)
    return [points[0], points[-1]]


def normalise(poly, y0, y1, cx):
    """Source pixels -> outline units: height 1.0, y up, centred on the owl."""
    h = y1 - y0
    return [(round((x - cx) / h, 4), round((y1 - y) / h, 4)) for x, y in poly]


def main() -> int:
    if not SRC.is_file():
        print(f"missing artwork: {SRC}")
        return 1
    owl, branch = masks(SRC)
    owl, dropped = largest_piece(owl)
    branch, bdropped = largest_piece(branch)
    print(f"owl: dropped {dropped} fleck(s); branch: dropped {bdropped}")

    ys, xs = np.nonzero(owl)
    y0, y1 = int(ys.min()), int(ys.max())
    cx = (int(xs.min()) + int(xs.max())) / 2
    H = y1 - y0

    body = rdp(trace(owl), RDP_EPS)
    holes = apertures(owl)
    print(f"owl {xs.max()-xs.min()+1} x {H+1} px, outline {len(body)} points, "
          f"{len(holes)} aperture(s)")

    # Eyes are the two largest and sit side by side; the beak is the third and
    # sits below them. Sorting by area then splitting on x gives left/right
    # deterministically, which matters because the model asks for them by name.
    eyes = sorted(holes[:2], key=lambda t: np.nonzero(t[1])[1].mean())
    beak = holes[2] if len(holes) > 2 else None

    def poly(mask_):
        return normalise(rdp(trace(mask_), RDP_EPS), y0, y1, cx)

    parts = {
        "BODY": poly(owl),
        "EYE_L": poly(eyes[0][1]),
        "EYE_R": poly(eyes[1][1]),
    }
    if beak is not None:
        parts["BEAK"] = poly(beak[1])

    bys, bxs = np.nonzero(branch)
    parts["BRANCH"] = normalise(rdp(trace(branch), RDP_EPS), y0, y1, cx)

    def centroid_y(m):
        return (y1 - np.nonzero(m)[0].mean()) / H

    lines = [
        '"""Generated by trace_owl.py — do not hand-edit.',
        "",
        "Normalised to the OWL's height: 1.0 from its lowest point to its",
        "highest, y up, x centred on the owl's bounding box. The branch is in",
        "the same frame, so its position relative to the owl is preserved and",
        "the two pieces assemble without a second alignment number.",
        '"""',
        f"OWL_ASPECT = {(xs.max()-xs.min()+1)/(H+1):.4f}   # width / height",
        f"EYE_CENTRE = {(centroid_y(eyes[0][1]) + centroid_y(eyes[1][1]))/2:.4f}"
        "   # fraction of owl height, from its base",
    ]
    if beak is not None:
        lines.append(f"BEAK_CENTRE = {centroid_y(beak[1]):.4f}")
    # The branch's top WHERE THE SLOT GOES, not its global maximum. Those are
    # different numbers here by 14 mm: the global maximum is a raised fork tip
    # at the far end, while the bar under the owl is LOWER than the owl's own
    # base — the artwork draws the owl floating, with the forks flanking it.
    # Using the global maximum puts the slot in thin air and the owl does not
    # engage at all, which nothing in a front elevation would show.
    tab_half = max(abs(x) for x, y in parts["BODY"]
                   if y < min(yy for _, yy in parts["BODY"]) + 0.004)
    lo = int(cx - tab_half * H)
    hi = int(cx + tab_half * H)
    band = branch[:, lo:hi]
    lines.append(f"BRANCH_TOP = {(y1 - bys.min())/H:.4f}"
                 "   # branch's highest point overall")
    lines.append(f"BRANCH_TOP_AT_SLOT = {(y1 - np.where(band.any(axis=1))[0].min())/H:.4f}"
                 "   # its top under the owl — NEGATIVE: below the owl's base")
    lines.append(f"TAB_HALF = {tab_half:.4f}   # half-width of the owl's tab")
    lines.append("")
    for name, pts in parts.items():
        lines.append(f"{name} = [")
        for i in range(0, len(pts), 4):
            row = ", ".join(f"({x:+.4f}, {y:+.4f})" for x, y in pts[i:i+4])
            lines.append(f"    {row},")
        lines.append("]")
        lines.append("")
    out = Path(__file__).parent / "owl_outline.py"
    out.write_text("\n".join(lines))
    print(f"wrote {out.name}: " +
          ", ".join(f"{k} {len(v)} pts" for k, v in parts.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
