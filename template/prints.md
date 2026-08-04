# _template — print log

One entry per physical print. This closes the outer loop: the renders and the
checks can only judge geometry, and everything else is discovered here.

Record a print even when it succeeds. A design that works and nobody wrote down
*why* it works is one refinement away from losing the property by accident.

## Template for an entry

### YYYY-MM-DD — iteration #N (`<params digest>`)

- **Settings:** material, layer height, supports, orientation on the plate.
- **Result:** what came out.
- **Measured vs. modeled:** the numbers that differed, and by how much. This is
  what turns a `nominal` constraint in spec.md into a `measured` one.
- **Verdict:** and then run `cad accept <part> good|bad|mixed "<why>"` so the
  iteration history carries it too.
