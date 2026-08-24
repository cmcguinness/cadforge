"""Trace the ghost artwork into the OPENINGS to cut. Writes `ghost_openings.py`.

**Inverted polarity** — the opposite of `raven_lantern` and `witch_lantern`.
Here the artwork is composed as the part is built:

    WHITE  = panel material.  The ghost IS white, and is continuous with the
             wall around the window, so it needs no bridges and no retaining.
    BLACK  = holes.  The window around the ghost, and the ghost's own eyes and
             mouth.

Lit, this reads as a dark ghost against a glowing window **with glowing eyes**.

Why this way round, when the other two parts are the other: **a ghost's
recognition lives in its face.** A raven or a witch in profile reads from its
outer contour, so it can be the hole. A faceless ghost is a blob — tried, and it
failed. Under the usual polarity the eyes would have to be chips of plastic
floating inside the hole; here they are simply holes in material, which costs
nothing. See ARTWORK.md and chatgpt-prompts/ghost-cutout.md for the three
attempts it took to work that out.

Islands ARE removed here, and in this polarity that means *growing the ghost*
very slightly — invisible at the sizes involved, where in the other polarity it
would have eaten the artwork.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

SRC = Path(__file__).parent / "inspiration" / "ghost.png"
"""Beside the part, in inspiration/.

An earlier version pointed into a chat image cache, which is per-session and
would have evaporated — a trace that cannot be re-run is a magic list of
coordinates. Source artwork belongs in `source-images/` and is part of the
record, exactly like `history.jsonl`."""
MOTIF_MM = 19.0
MIN_OPENING_W = 0.44     # widest inscribed circle; see witch_lantern history
RDP_EPS = 2.5


def trace(mask):
    pad = np.pad(mask, 1)
    ys, xs = np.nonzero(pad)
    y0 = int(ys.min())
    start = (y0, int(xs[ys == y0].min()))
    nbrs = [(0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1)]
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


def remove_islands(white, layer_px):
    """Grow the material until no layer holds a blob with nothing beneath it."""
    white = white.copy()
    for sweep in range(12):
        H, W = white.shape
        sup = np.zeros_like(white)
        sup[-1] = white[-1]
        found = np.zeros_like(white)
        for y in range(H - 2, -1, -1):
            below = sup[y + 1]
            reach = below.copy()
            for s in range(1, layer_px + 1):
                reach |= np.roll(below, s)
                reach |= np.roll(below, -s)
            s_now = white[y] & reach
            lab, n = ndimage.label(white[y])
            for i in range(1, n + 1):
                comp = lab == i
                if s_now[comp].any():
                    s_now |= comp
                else:
                    found[y] |= comp
            sup[y] = s_now
        if not found.any():
            print(f"  no islands after {sweep} sweep(s)")
            return white
        # An island is fixed by putting material UNDER it: extend each island
        # column straight down until it lands on something. In this polarity
        # that thickens the ghost slightly rather than eating the artwork.
        print(f"  sweep {sweep + 1}: anchoring {found.sum()} island px")
        col = np.zeros_like(white)
        ys, xs = np.nonzero(found)
        for y, x in zip(ys, xs):
            col[y:, x] = True
        white |= col & ~ndimage.binary_dilation(white, np.ones((1, 1), bool)) | found
        white = ndimage.binary_fill_holes(white)
    raise SystemExit("islands did not converge")


def main():
    sys.setrecursionlimit(20000)
    src = Image.open(SRC)
    if src.mode in ("RGBA", "LA", "PA"):
        bg = Image.new("RGBA", src.size, (255,) * 4)
        src = Image.alpha_composite(bg, src.convert("RGBA"))
    black = np.array(src.convert("L")) < 128
    ys, xs = np.nonzero(black)
    H = ys.max() - ys.min() + 1
    mmpp = MOTIF_MM / H
    print(f"  window {(xs.max() - xs.min() + 1) * mmpp:.1f} x {MOTIF_MM} mm")

    lab, n = ndimage.label(black)
    kept = []
    for i in range(1, n + 1):
        m = lab == i
        wide = 2 * ndimage.distance_transform_edt(m).max() * mmpp
        if wide < MIN_OPENING_W:
            print(f"  dropped an opening {wide:.2f} mm wide")
            continue
        kept.append((m.sum() * mmpp * mmpp, wide, rdp(trace(m), RDP_EPS)))
    kept.sort(key=lambda t: -t[0])
    print(f"  {len(kept)} openings: "
          + ", ".join(f"{a:.1f}mm2/{w:.2f}mm" for a, w, _ in kept))

    cx = (xs.min() + xs.max()) / 2
    y1 = ys.max()
    out = ["# Generated by trace_ghost.py — do not hand-edit.",
           "# INVERTED POLARITY: these are the holes. White is the ghost, and the",
           "# ghost is continuous with the wall, so nothing here needs retaining.",
           "# Normalised: motif height 1.0, centred in x, sitting on y=0.",
           "OPENINGS = ["]
    for area, wide, pts in kept:
        P = np.array(pts, float)
        P[:, 0] = (P[:, 0] - cx) / H
        P[:, 1] = (y1 - P[:, 1]) / H
        out.append(f"    # {area:.1f} mm2, narrowest {wide:.2f} mm, {len(P)} points")
        out.append("    [")
        for i in range(0, len(P), 4):
            out.append("        " + " ".join(f"({x:+.4f}, {y:+.4f})," for x, y in P[i:i + 4]))
        out.append("    ],")
    out.append("]")
    dst = Path(__file__).with_name("ghost_openings.py")
    dst.write_text("\n".join(out) + "\n")
    print(f"  wrote {dst.name}")


if __name__ == "__main__":
    main()
