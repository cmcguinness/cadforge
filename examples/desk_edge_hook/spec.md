---
stage: review
---

# desk_edge_hook

The worked example for this repo. Small enough to read in one sitting, real
enough to contain a trap that costs a print.

## What it is for

A clip that grips the front edge of a desk by spring force alone — no screws, no
adhesive — with a prong hanging below it to hook headphones, a cable loom, or a
bag strap. It gets pushed on and pulled off by hand, occasionally, and otherwise
lives there.

## Constraints

**Fixed by the world**

- `desk_t`, the edge thickness, is `measured`. Everything else is sized around
  it, so a nominal here would poison the whole part. Measure the actual desk;
  edges are rarely the round number the furniture listing claims.
- The desk edge is assumed flat and parallel-sided for at least `throat` inward.
  A bullnose or a lipped edge breaks that and needs a different profile.

**Fixed by the process**

- PLA on an A1 mini, no supports.
- The part is a prism, so it prints without a single overhang **in the right
  orientation**. The orientation is not a free choice — see notes.md. This is
  the whole reason the example exists.
- PLA has very little elastic range. The grip has to come from a small
  interference across a long arm, not a large interference across a short one.

**Fixed by taste**

- It should be pushed on with the thumb, not hammered.

## Acceptance criteria

- [ ] The mouth is narrower than the desk by `grip`, so the clip is in
      interference when fitted (asserted).
- [ ] `grip` stays within the elastic range PLA can actually return from
      (asserted as a fraction of `desk_t`).
- [ ] The arm is long enough relative to its thickness to bend rather than
      crack (asserted).
- [ ] The three internal corners — both mouth roots and the prong root — are
      filleted, and no other corner is (asserted by edge count).
- [ ] The part is one solid of the declared width (asserted).
- [ ] It prints with no planar overhang in the declared orientation.

### Only a print can settle these

- [ ] Whether `grip` gives a hold that survives being knocked, without needing
      two hands to fit.
- [ ] Whether the arm springs back after a dozen fittings or takes a set.
- [ ] Whether the prong carries a real load without the root yielding.

## Open questions

- **Never printed.** Every number here is reasoned, none is validated. `grip` is
  the one most likely to be wrong, and it is the one that decides whether the
  part works at all.
- The prong has no upturn at its tip, so anything hung on it can slide off if
  the desk is bumped. Deliberate for now — an upturn adds an overhang and would
  cost the clean prism.
