# desk_edge_hook — notes

**Read before editing the model. Update when you learn something.**

## Design intent

Two parameters do almost all the work, and they are not the two you would guess.

- **`grip` is the entire holding force.** The clip is a spring in interference:
  its relaxed mouth is `grip` narrower than the desk, so fitting it spreads the
  arms by exactly that much and the arms push back. Nothing else holds it on.
- **`throat` is the compliance knob, not `arm_t`.** This is the one people get
  backwards. See below.

`desk_t` drives the mouth, the mouth drives the overall height, and the height
is otherwise not a design choice at all. Changing `desk_t` alone is safe;
changing `grip` alone is safe; changing `arm_t` alone quietly changes how hard
the clip is to fit, by a *cube*.

## Print orientation is load-bearing, and the intuitive choice snaps

The trap, and the reason this part is the worked example.

The clip is a prism: one closed profile extruded along its width. That means it
can be printed in more than one orientation with no supports either way, and
both look identical coming off the bed. They are not equivalent.

- **The intuitive orientation** — standing the way it hangs on the desk, so it
  looks right on the plate — stacks layers along the model's Z. The upper arm is
  a cantilever bending about the width axis, so the tensile stress at its root
  runs *across* those layers, straight through the interlayer bond. That is the
  weakest direction FDM has. The arm delaminates at the root, usually the first
  or second time the clip is opened.
- **The correct orientation** lays the profile flat on the bed and puts the
  width along the printer's Z. Every layer is then a complete copy of the
  profile, the bending stress runs *within* a layer, and the bed contact is the
  full profile outline, which is generous.

`PRINT_ROTATION = (-90, 0, 0)` encodes this, so `cad build --stl` exports the
mesh already in that pose. **The rotation is not cosmetic and must not be
"tidied up" to make the STL look upright in the slicer.**

Nothing in the geometry can catch this. Both poses are valid solids, both slice
without a warning, both pass every check in `cadkit/check.py`. It is only
visible as a decision, which is why it is written here and encoded there.

## Compliance goes as the cube of the arm's length

The instinct when a clip is too stiff is to thin the arm. That is the expensive
way round.

For a cantilever, tip deflection under a given load goes as `L³/t³`. Doubling
the arm's reach buys eight times the give and **keeps** the section. Halving the
thickness buys the same eight times and throws away the strength — the arm now
bends easily and also breaks easily, which is the worst of both.

So: if it is too hard to fit, increase `throat` before touching `arm_t`. The
assertion in `check()` enforces the floor of this (`arm_reach >= 4 * arm_t`),
because below that ratio the arm does not really bend at all — the deflection
localises at the root and it splits instead.

## Rounding every corner does not work

The first version filleted every vertex of the sketch, which is the obvious
move. It fails outright: the arm tip's two vertices are `arm_t` apart, so two
fillets of radius `r` need `2r < arm_t`, and at the default values they do not
fit. build123d raises rather than silently producing something wrong, which is
the good case.

Only three corners actually need rounding, and all three are internal, where the
fillet adds material rather than removing it: the two mouth roots, which are
where the arm bends and where a sharp corner would start a crack, and the prong
root, which carries everything hung on it. They are selected by position after
the extrude, and the selection asserts its own count — if the profile ever
changes shape, that assertion fires instead of the fillet silently landing on
the wrong edges.

There is a second, subtler lesson in that failure: `check()` runs *after*
`build()`, so a parameter that breaks the build never reaches the assertion that
would have explained it. An assertion is a guard against a bad *design*, not
against a crash.

## Open threads

- **Never printed.** Everything above about layer orientation is sound
  engineering but the specific numbers — `grip` above all — are unvalidated.
- **`grip = 0.8` on a 25 mm desk is a guess** at the low end, on the theory that
  a clip that is slightly loose is annoying while one that is too tight is
  broken. Untested in either direction.
- **The elastic-range assertion (`grip <= 8% of desk_t`) is a rule of thumb**,
  not a computed limit. It has no test behind it. If a print takes a set well
  below that fraction, the number should come down and this note should say so.
- The prong has no upturn, so a knock can shed the load. Adding one costs the
  clean prism and introduces the first real overhang.
