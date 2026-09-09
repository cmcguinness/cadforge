"""Cutting templates for the paper diffusers, at true scale, as one PDF.

    .venv/bin/python <collection>/castle/paper_templates.py

Two sheets go into a castle — one behind the face, covering the mouth and both
eyes at once, and one behind the bat window. They are cut by hand. Cutting them
by eye works and wastes paper and light; this emits an outline to cut round.

**It emits for `mini_castle` from the same geometry.** That part is `castle`
scaled, so its openings are these openings times `scale`. Its storeys are
*inferred from the facade* rather than built — it has no internal slabs at all
— so "first floor" and "second floor" name the same two groups of openings in
both parts, and mean the elevation rather than anything you could stand on.

WHAT DECIDES THE OUTLINE — NOT THE OPENINGS
-------------------------------------------
The paper has to land on **material at the glue plane**, which is the back face
of that tier's front wall, and that plane carries more than the openings: the
chamber floor cuts across the foot of the face, and setbacks close in at the
sides. So each edge is grown outward on its own and stopped where it would
leave material, and the result is *proved* by boolean rather than trusted from
the search.

Growing each edge separately rather than insetting uniformly is the whole
trick. The face's sheet is bounded hard below by the chamber floor and has room
to spare above it; a uniform margin gives away the top to protect the bottom.

A sheet that overhangs does not fail loudly. It lifts at one corner, *behind*
the facade where nobody can see it, and the light leaks round the edge instead
of being diffused — at exactly the opening it was cut for.

PRINTING
--------
The PDF is drawn in real millimetres on a Letter page. **It carries a 50 mm bar
because a true-scale drawing you cannot check is worse than no drawing**: if
the bar does not measure 50 mm the print was scaled and every template on the
page is wrong.
"""
import os, sys, time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from build123d import *                                          # noqa: E402
from cadkit.part import load                                     # noqa: E402
from reportlab.pdfgen import canvas as pdfcanvas                 # noqa: E402
from reportlab.lib.pagesizes import letter                       # noqa: E402
from reportlab.lib.units import mm                               # noqa: E402

# How far an edge may grow, full size. **This is glue land, not a scissor
# allowance**, and that is why it is 12 rather than the 4 it started at: the
# paper is pressed onto the wall either side of every opening, and a 4 mm strip
# is not something you can get a finger onto. Every edge is still capped by the
# wall — the first floor takes about 2 mm at top and bottom whatever this says,
# because the chamber floor is below it and the tier setback above, so in
# practice the whole of the glue land is at the sides.
#
# The wall would allow far more (29 mm left, 26 right on the face). Chosen at 12
# rather than filling the facade because the sheet goes in by hand through the
# open back, and a 103 mm sheet in a 136 mm chamber is a fight.
GLUE_MARGIN = 12.0

# The SIDES are not a margin and must not be tuned like one. Set high so the
# search runs them out to whatever stops them.
#
# **The walls are partially translucent** — `castle/prints.md` records that in
# purple at wall = 2.4 the facade transmits and reads as lit stone. So a paper
# edge that stops part-way across a lit wall is backlit, and shows from the
# front as a line across the masonry. Observed on a finished castle; no render
# and no assertion in this repo could have found it.
#
# Running the sheet to the full width of the flat wall puts its edge in the
# corner, where the geometry changes anyway and there is nothing to see. This
# is a lighting requirement, not a gluing one, and it OVERRIDES the "keep it
# small enough to handle" reasoning that picked 12 mm — that was a convenience,
# this is the object looking wrong.
#
# It is conditional on the filament: in an opaque black the walls do not
# transmit and none of this applies. It stays at full width regardless, because
# a sheet that is too wide costs nothing and one that is too narrow is visible.
SIDE_MARGIN = 40.0
CORNER_R = 2.0

# How far OUTSIDE the fitted outline to draw the line you actually cut.
#
# The two errors are not symmetric: paper left on is trimmed with scissors in
# five seconds, paper missing means cutting the sheet again. So the cut line is
# deliberately generous and the fitted line is drawn inside it as the limit to
# trim back to — and only where the sheet actually fouls something, which on
# these two sheets is the top and bottom edges and nowhere else.
TRIM = 4.0
BAND = 0.2               # thickness of the test slice, inside the wall

# Which openings share a sheet, stated rather than derived. `lit_by` groups by
# which puck lights an opening, which is nearly this question and not quite:
# the mouth and the eyes are lit by different stations yet take ONE sheet,
# because the spec's criterion is that the back of the face is flat enough to
# glue over both at once.
SHEETS = (("first floor", "behind the face — mouth and both eyes", 0,
           ("mouth", "eye_l", "eye_r")),
          ("second floor", "behind the bat window", 1, ("win_bat",)))

TARGETS = (("castle", 1.0), ("mini_castle", 0.5))


def band(tier, m, p):
    """The y range just inside the back face of a tier's front wall."""
    yb = m.TIER_Y[tier] + p.wall
    return yb - BAND - 0.05, yb - 0.05


def slab(y0, y1, w=500.0):
    return Pos(0, (y0 + y1) / 2, 0) * Box(w, y1 - y0, w)


def overhang(rect_xz, holes, wall, y0, y1) -> float:
    """mm3 of sheet that would hang over open air. Zero is a fit.

    Done as a 3D boolean against the wall rather than as a 2D projection: this
    plane IS a face of the wall, and a planar section landing on a coincident
    face is exactly where sectioning returns empty or doubled results.
    """
    # `dir` is explicit and `Pos` places it, because Plane.XZ's normal is −Y:
    # a bare extrude here builds backwards, and the paper lands BEHIND the wall
    # where nothing supports it, so every candidate reads as a total overhang.
    paper = Pos(0, y0, 0) * extrude(Plane.XZ * rect_xz, amount=(y1 - y0),
                                    dir=(0, 1, 0))
    landing = paper - holes            # the paper that must take glue
    if landing is None:
        return 0.0
    left = landing - wall
    return 0.0 if left is None else max(0.0, left.volume)


def grow(openings, holes, wall, y0, y1, margin):
    """Largest rectangle round the openings whose paper still lands on wall."""
    x0 = min(o.x - o.w / 2 for o in openings)
    x1 = max(o.x + o.w / 2 for o in openings)
    z0 = min(o.z0 for o in openings)
    z1 = max(o.z1 for o in openings)
    d = {"left": 0.0, "right": 0.0, "bottom": 0.0, "top": 0.0}

    def rect(dd, rounded=False):
        w = (x1 - x0) + dd["left"] + dd["right"]
        h = (z1 - z0) + dd["bottom"] + dd["top"]
        cx = (x0 + x1) / 2 - dd["left"] / 2 + dd["right"] / 2
        cz = (z0 + z1) / 2 - dd["bottom"] / 2 + dd["top"] / 2
        shape = RectangleRounded(w, h, min(CORNER_R, w / 4, h / 4)) if rounded \
            else Rectangle(w, h)
        return Pos(cx, cz) * shape, dict(w=w, h=h, cx=cx, cz=cz)

    for edge in ("bottom", "top", "left", "right"):
        lo, hi = 0.0, (SIDE_MARGIN if edge in ("left", "right") else margin)
        for _ in range(9):                       # ~0.08 mm on a 40 mm side sweep
            mid = (lo + hi) / 2
            trial = dict(d, **{edge: mid})
            r, _ = rect(trial)
            if overhang(r, holes, wall, y0, y1) <= 1e-6:
                lo = mid
            else:
                hi = mid
        d[edge] = lo
    r, info = rect(d, rounded=True)
    info.update(d)
    return r, info


def polylines(sk, chord=0.25):
    """Flatten a sketch to point lists, for drawing. Sketch XY = castle x, z."""
    out = []
    for f in sk.faces():
        for w in [f.outer_wire(), *f.inner_wires()]:
            for e in w.edges():
                n = max(2, int(e.length / chord) + 1)
                out.append([(e @ (i / (n - 1))) for i in range(n)])
    return out


def draw(c, polys, ox, oy, s, rgb, lw, dash=None):
    c.setStrokeColorRGB(*rgb)
    c.setLineWidth(lw)
    c.setDash(dash or [])
    for pts in polys:
        pth = c.beginPath()
        pth.moveTo(ox + pts[0].X * s * mm, oy + pts[0].Y * s * mm)
        for q in pts[1:]:
            pth.lineTo(ox + q.X * s * mm, oy + q.Y * s * mm)
        c.drawPath(pth)
    c.setDash([])


def main():
    t0 = time.time()
    lp = load("castle")
    m, p = lp.module, lp.params
    cache = Path(os.environ.get("CASTLE_BREP_CACHE", "")) if os.environ.get(
        "CASTLE_BREP_CACHE") else None
    if cache and cache.exists():
        part = import_brep(str(cache))
        print(f"castle loaded from cache in {time.time() - t0:.0f}s")
    else:
        part = m.build(p)
        print(f"castle built in {time.time() - t0:.0f}s")
        if cache:
            export_brep(part, str(cache))
    by_name = {o.name: o for o in m.OPENINGS}

    sheets = []
    for label, sub, tier, names in SHEETS:
        y0, y1 = band(tier, m, p)
        wall = part & slab(y0, y1)
        os_ = [by_name[n] for n in names]
        holes = Compound(children=[
            m._through(m._opening_sketch(o, p), *m._opening_y(o, p)) for o in os_])
        holes = holes & slab(y0, y1)
        art = Sketch() + [m._opening_sketch(o, p) for o in os_]
        base, _ = grow(os_, holes, wall, y0, y1, 0.0)
        base_over = overhang(base, holes, wall, y0, y1)
        assert base_over <= 1e-6, (
            f"{label}: the openings' own bounding box already hangs "
            f"{base_over:.1f} mm3 over open air — no margin exists to grow from, "
            f"and the sheet has to be cut to a shape rather than a rectangle")
        rect, info = grow(os_, holes, wall, y0, y1, GLUE_MARGIN)
        left = overhang(rect, holes, wall, y0, y1)
        assert left <= 1e-6, f"{label}: {left:.2f} mm3 of sheet over open air"
        sheets.append((label, sub, rect, art, info))
        print(f"  {label}: {info['w']:.1f} x {info['h']:.1f} mm  grown "
              f"L{info['left']:.1f} R{info['right']:.1f} "
              f"B{info['bottom']:.1f} T{info['top']:.1f}"
              f"   cut at {info['w'] + 2 * TRIM:.1f} x {info['h'] + 2 * TRIM:.1f}")

    # Beside this script rather than under a hardcoded collection: the same
    # file is published into examples/, where "parts/castle/..." names a
    # directory a fresh clone does not have.
    out = HERE / "templates"
    out.mkdir(exist_ok=True)
    path = out / "paper-diffuser-templates.pdf"
    c = pdfcanvas.Canvas(str(path), pagesize=letter)
    W, H = letter
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    c.setFont("Helvetica-Bold", 11)
    c.drawString(15 * mm, H - 15 * mm, "Castle paper diffusers — cutting templates")
    c.setFont("Helvetica", 8)
    c.drawString(15 * mm, H - 20 * mm,
                 "PRINT AT 100%, NO PAGE SCALING. Check the 50 mm bar at the "
                 "bottom before cutting anything.")
    c.drawString(15 * mm, H - 24.5 * mm,
                 "SOLID = cut this.  It is deliberately 4 mm oversize all round: "
                 "trimming paper is easy, adding it is not.")
    c.drawString(15 * mm, H - 29 * mm,
                 "DASHED = the largest that still lands on wall. Trim back to it "
                 "only where the sheet fouls.  DOTTED grey = the openings, for "
                 "alignment only.")
    c.drawString(15 * mm, H - 33.5 * mm, f"Generated {stamp}")

    y = H - 48 * mm
    for part_name, s in TARGETS:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(15 * mm, y, f"{part_name}  (scale {s:g}x)")
        y -= 6 * mm
        x = 15 * mm
        row_h = 0.0
        for label, sub, rect, art, info in sheets:
            # Wrap rather than trusting the templates to fit side by side. At
            # full width the first-floor sheet is 111 mm of a 216 mm page, and
            # a template that runs off the edge is not a small cosmetic fault:
            # it is a cutting line that silently is not there.
            need = (rect.bounding_box().size.X + 2 * TRIM) * s * mm
            if x > 15 * mm and x + need > W - 12 * mm:
                y -= row_h + 8 * mm
                x, row_h = 15 * mm, 0.0
            rr = min(CORNER_R, info["w"] / 4, info["h"] / 4) + TRIM
            rough = Pos(info["cx"], info["cz"]) * RectangleRounded(
                info["w"] + 2 * TRIM, info["h"] + 2 * TRIM, rr)
            bb = rough.bounding_box()
            w, h = bb.size.X * s, bb.size.Y * s
            ox, oy = x - bb.min.X * s * mm, y - h * mm - bb.min.Y * s * mm
            draw(c, polylines(art), ox, oy, s, (0.62, 0.62, 0.62), 0.4, [1.4, 1.4])
            draw(c, polylines(rect), ox, oy, s, (0.35, 0.35, 0.35), 0.5, [3, 2])
            draw(c, polylines(rough), ox, oy, s, (0, 0, 0), 1.0)
            # THIS SHEET HAS A RIGHT WAY ROUND. The face is built about the
            # gate at x = +2, not about the castle's centreline — the castle is
            # asymmetric on purpose — so the first-floor sheet has ~4 mm more
            # wall on its left than its right. Reversed, it overhangs one side
            # by that much and leaves a gap of it on the other, and the gap is
            # a backlit paper edge: the exact fault the full width exists to
            # remove. Cheap to mark, invisible to check once it is glued.
            off = abs(info["left"] - info["right"])
            c.setFillColorRGB(0.45, 0.45, 0.45)
            c.setFont("Helvetica-Bold", 6)
            c.drawCentredString(ox + info["cx"] * s * mm,
                                oy + (info["cz"] + info["h"] / 2) * s * mm
                                - 3.2 * mm, "TOP")
            if off > 0.5:
                c.setFont("Helvetica", 5)
                c.drawString(ox + (info["cx"] - info["w"] / 2) * s * mm + 1 * mm,
                             oy + info["cz"] * s * mm, "LEFT")
                c.drawRightString(
                    ox + (info["cx"] + info["w"] / 2) * s * mm - 1 * mm,
                    oy + info["cz"] * s * mm, "RIGHT")
            c.setFont("Helvetica", 7)
            c.setFillColorRGB(0, 0, 0)
            c.drawString(x, y - h * mm - 5 * mm,
                         f"{label} — cut {w:.1f} x {h:.1f} mm"
                         + (f"  · NOT symmetric ({off:.1f} mm)" if off > 0.5 else ""))
            c.setFont("Helvetica", 6)
            c.drawString(x, y - h * mm - 9 * mm, sub)
            x += w * mm + 12 * mm
            row_h = max(row_h, h * mm + 14 * mm)
        y -= row_h + 10 * mm

    by = 22 * mm
    c.setLineWidth(1.0)
    c.setStrokeColorRGB(0, 0, 0)
    c.line(20 * mm, by, 70 * mm, by)
    for i in range(6):
        c.line(20 * mm + i * 10 * mm, by, 20 * mm + i * 10 * mm, by + 3 * mm)
    c.setFont("Helvetica", 7)
    c.drawString(20 * mm, by - 5 * mm,
                 "This bar is 50 mm. If it measures anything else, the page was "
                 "scaled and every template above is the wrong size.")
    c.showPage()
    c.save()
    print(f"\nwrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
