"""Trace the witch-head silhouette into a normalised outline.

Run standalone; writes `head_outline.py` next to it. Not imported by model.py —
the traced polygon is generated once and read as data, so a build never depends
on an image file outside the repo.

This motif is a **cutout**: the black of the reference becomes the hole, like
`raven_lantern` and unlike the abandoned moon-and-witch composition. It was
chosen because it reads entirely from its outer contour — see ARTWORK.md, and
notes.md for what happens when a motif does not.

See ARTWORK.md for the pipeline and why each step is there.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

SRC = Path(__file__).parent / "inspiration" / "witch-head.png"
"""Beside the part, in inspiration/. This pointed into a chat image cache, which is per-session —
`raven_lantern`'s source was already gone by the time anyone noticed, so that
outline can never be re-traced, only edited as coordinates. Source artwork is
part of the record."""

MERGE = 0.008
"""Closing radius, as a fraction of the silhouette's height.

Light on purpose. This artwork barely needs it — 98.4% of its area already
survives a 0.4 mm nozzle at 19 mm tall, unsimplified — so the job here is only
to tidy the finest hair tendrils rather than to rescue anything. The witch on a
broomstick needed 0.013 and was still marginal; the difference is what "reads
from its outer contour" buys you."""

RDP_EPS = 3.0


def remove_islands(hole, layer_px):
    """Grow the opening until no layer of the wall contains a floating island.

    **The failure this whole part turned on**, and the one that is invisible in
    every other check.

    Printing upright, each raster row is one layer. Material on a layer is fine
    if something below can hold it — directly, or within the lateral creep the
    overhang limit allows — or if it is part of a run that reaches such material
    sideways. What is NOT fine is a connected blob of material on a layer with
    **no** path to anything supported: it is laid into open air and falls.

    That is categorically different from an overhang, which leans out but stays
    attached, and lumping the two together is exactly how this got missed. The
    raven has **zero** islands and printed clean; this artwork had ten, with the
    worst 4 mm wide, and the slicer's preview showed them plainly.

    The cause here is the notch between the hat's curled tip and its crown: a
    wedge of wall pokes down into the opening, and its lowest point begins in
    mid-air with nothing beneath it.

    The fix is to make the island part of the hole. Merging it into the opening
    is what a paper-cut artist does when a shape will not hold — it costs a
    little detail and it is deterministic, where reshaping by hand is neither.
    Iterated, because filling one island can expose another above it.
    """
    hole = hole.copy()
    for sweep in range(12):
        mat = ~hole
        H, W = mat.shape
        sup = np.zeros_like(mat)
        sup[-1] = mat[-1]
        found = np.zeros_like(mat)
        for y in range(H - 2, -1, -1):
            below = sup[y + 1]
            reach = below.copy()
            for s in range(1, layer_px + 1):
                reach |= np.roll(below, s)
                reach |= np.roll(below, -s)
            s_now = mat[y] & reach
            lab, n = ndimage.label(mat[y])
            for i in range(1, n + 1):
                comp = lab == i
                if s_now[comp].any():
                    s_now |= comp          # anchored somewhere: the run rides along
                else:
                    found[y] |= comp       # nothing holds it — island
            sup[y] = s_now
        if not found.any():
            print(f"  no islands after {sweep} sweep(s)")
            return hole
        print(f"  sweep {sweep + 1}: filling {found.sum()} island px")
        hole |= found
    raise SystemExit("islands did not converge — the artwork needs reshaping")


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


def main():
    sys.setrecursionlimit(20000)
    src = Image.open(SRC)
    if src.mode in ("RGBA", "LA", "PA"):
        bg = Image.new("RGBA", src.size, (255,) * 4)
        src = Image.alpha_composite(bg, src.convert("RGBA"))
    ink = np.array(src.convert("L")) < 128

    lab, n = ndimage.label(ink)
    sizes = ndimage.sum(ink, lab, range(1, n + 1))
    m = ndimage.binary_fill_holes(lab == (np.argmax(sizes) + 1))
    ys, xs = np.nonzero(m)
    H = ys.max() - ys.min() + 1
    print(f"  {n} component(s); largest is {sizes.max() / sizes.sum():.1%} of the ink")

    if MERGE:
        r = int(MERGE * H)
        y, x = np.ogrid[-r:r + 1, -r:r + 1]
        m = ndimage.binary_fill_holes(
            ndimage.binary_closing(m, x * x + y * y <= r * r))

    # Island removal happens at LAYER resolution, because "is there material on
    # this layer with nothing under it" is a question about rows of layers. But
    # the fill is applied back at FULL resolution and the trace runs there —
    # tracing the coarse raster threw away all the detail (140 points became 26).
    import math
    import printer
    lay = printer.LAYER_H
    MOTIF_MM = 19.0                       # the size this is judged and printed at
    step_px = max(0, int(round(
        (lay / math.tan(math.radians(printer.MAX_OVERHANG_DEG))) / lay)))

    scale = MOTIF_MM / lay / H            # full-res px -> layer-res px
    sw, sh = max(4, int(m.shape[1] * scale)), max(4, int(m.shape[0] * scale))
    small = np.array(Image.fromarray((m * 255).astype(np.uint8))
                     .resize((sw, sh))) > 127
    pad = 24
    hole = np.zeros((sh + 2 * pad, sw + 2 * pad), bool)
    hole[pad:pad + sh, pad:pad + sw] = small
    fixed = remove_islands(hole, step_px)
    added = fixed[pad:pad + sh, pad:pad + sw] & ~small
    if added.any():
        up = np.array(Image.fromarray((added * 255).astype(np.uint8))
                      .resize((m.shape[1], m.shape[0]), Image.NEAREST)) > 127
        m = m | up
        m = ndimage.binary_fill_holes(m)
        print(f"  filled {added.sum()} island px at layer scale "
              f"-> {up.sum()} px at full scale")

    pts = rdp(trace(m), RDP_EPS)
    P = np.array(pts, float)
    P[:, 1] = -P[:, 1]                       # image y is down, model y is up
    P -= P.min(axis=0)
    P /= P[:, 1].max()                       # height 1.0
    P[:, 0] -= P[:, 0].mean()                # centred in x

    w = P[:, 0].max() - P[:, 0].min()
    print(f"  {len(P)} points, {w:.3f} wide x 1.000 tall")

    # The narrowest feature, measured off the simplified mask rather than
    # guessed. This is a CUTOUT, so it is the width of a slot: below one nozzle
    # the slicer fills it with gap-fill instead of opening it.
    d = ndimage.distance_transform_edt(m)
    q = np.percentile(2 * d[m] / H, 2)
    print(f"  2nd-percentile local width {q:.4f} of height "
          f"(= {q * 19:.2f} mm at a 19 mm motif)")

    out = ["# Generated by trace_head.py — do not hand-edit.",
           "# Normalised: height 1.0, centred in x. Multiply by the motif height.",
           f"WIDTH_PER_HEIGHT = {w:.4f}",
           f"NARROW_PER_HEIGHT = {q:.4f}   # 2nd-percentile local width",
           "OUTLINE = ["]
    for i in range(0, len(P), 4):
        out.append("    " + " ".join(f"({x:+.4f}, {y:+.4f})," for x, y in P[i:i + 4]))
    out.append("]")
    dst = Path(__file__).with_name("head_outline.py")
    dst.write_text("\n".join(out) + "\n")
    print(f"  wrote {dst.name}")


if __name__ == "__main__":
    main()
