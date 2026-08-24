---
project: halloween_lantern
stage: done
---

# pumpkin_lantern

A jack-o'-lantern that **drops over** a battery tea light. One piece, orange PLA, open at the bottom, lightly ribbed, with a carved face and a stem.

Body proportions are its own; the puck's dimensions come from the `halloween_lantern` project.

*(This spec was rewritten after the first print. It previously described a two-piece design — a base holding the puck, a lid carrying the face, a lip joining them. The print showed the base was not earning its place. See prints.md; the old criteria are in the history.)*

## What it is for

The same job as the rest of the set — a battery LED tea light on a table through October — but it is the one that **glows** rather than silhouettes.

Lit, it should read as a jack-o'-lantern from across a room: a bright face on a body glowing softly orange. Unlit, in daylight, it should read as a pumpkin — squat, ribbed, stemmed — and not as a lamp.

## One piece, and why that was not obvious

It began as two. Dropping the base removed the seam, the lip, a fit tolerance, a split operation and about half this part's failure modes.

The base was doing one thing worth keeping — stopping the pumpkin wandering off the puck — and an **annular floor** does that for nothing: the skirt rests on the table with the tea light standing in the ring's hole.

There was a hidden gain too. With no floor under it, the puck now stands on the **table**, so every "must clear the opaque body" height dropped by 2 mm. Removing the base made more wall available, not less.

## Constraints

**Fixed by the world**

- **The puck is opaque for its lower 15 mm**, measured from whatever it stands on — here, the table. Nothing below that is ever lit.
- **Orange PLA is translucent at 1.1 mm.** Measured, not assumed: the first print settled it and the glow is right. This is the only part in the set where wall thickness is an *optical* parameter.
- No paper liner. The wall is meant to glow; a liner would block it.

**Fixed by the process**

- Prints upright on its own skirt, no supports.
- **Constant wall thickness everywhere.** With a translucent wall, thickness variation IS brightness variation, so the ribs must undulate the whole wall — inner and outer surfaces together — rather than being grooves cut into it.
- **A hollow shell cannot change radius faster than its wall is thick.** Each layer is a ring; if the radius shifts more than the wall between layers, the rings do not overlap and the shell arrives as loose hoops.
- **The profile must be tangent-continuous.** Equal radius where two curves meet is not enough — a slope discontinuity reads as a machined step right around the pumpkin.
- Teeth must not hang. Material starting in mid-air is an island.

**Fixed by taste**

- Squat and ribbed. A pumpkin, not an apple and not a sphere.
- The face carved, not printed on: openings, with the body glowing behind.

## Acceptance criteria

### Does it do its job?

- [x] **It reads as a jack-o'-lantern**, unlit and in daylight, to someone not told what it is.
- [x] **The face is the brightest thing, with the body glowing behind it.** Both halves matter: face alone is the other three lanterns, glow alone is a lamp.
- [x] **It drops over the tea light and stays centred on it**, without the puck needing to be forced into the ring.
- [x] **The whole face sits above the puck's opaque body.** Asserted.
- [x] **The wall is one thickness everywhere**, so the glow is even.
- [x] **It shares the set's puck**, though deliberately not its height.
- [x] **The ribs read as ribs** at this size — suggested, not corrugated.

### Is it built correctly?

- [x] **One connected solid.** Asserted — the assertion this part lacked while a free-floating lip survived several builds, several renders and a print.
- [x] **No floating islands.**
- [x] **The shell is continuous layer to layer** — the radius never shifts faster than the wall is thick, with enough margin that rings weld rather than touch. Asserted.
- [x] **The centring ring is wide enough to be a locator**, and its hole clears the puck. Asserted.
- [x] Every face opening exceeds the nozzle; the two rows of teeth keep a solid waist between them. Asserted.
- [x] Fits the configured bed. `PRINT_ROTATION` stated.

### Only a print can settle these

- [x] **Whether 1.1 mm is strong enough as a CLOSED shell.** A partial print felt marginal in the hand, but that piece had neither the dome closing over it nor the floor ring — both stiffen it out of proportion to their thickness.
- [x] Whether the shoulder is properly welded now, or still bridges marginally. The direct test of tightening the ring-overlap factor from 0.7 to 0.45.
- [x] Whether the annular ring actually centres it, and whether 0.9 mm per side is the right looseness.
- [x] Whether the stem survives being picked up by.

All four settled by that print — see `prints.md`. That print also raised a criterion nobody had written: **the grin must read as teeth.** It is recorded there rather than added here, because the part is done and adding a criterion now would move the target it has already met.

## Open questions

- **How much of the top could be bought back with internal buttressing.** Glow at the top does not matter — the sides are what is seen — so material there is nearly free, and thickening the rib crests inside would let the shoulder be rounder than the global slope limit allows. `buttress` exists and is 0.
- Whether the face wants to be larger now the body has grown.
