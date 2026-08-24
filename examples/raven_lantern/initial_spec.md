# initial_spec — what was actually asked for

Kept deliberately, unedited in substance, as the *before* half of a worked example. `spec.md` is what this turned into after one round of questions and one set of caliper measurements; the gap between the two files is the point.

Nothing reads this file. It is not staged, not hashed, and does not constrain a build. Do not update it as the design moves — that is `spec.md`'s job, and a before-picture that gets retouched stops being evidence of anything.

---

## The brief, as given

> I want to build some tea light holders from scratch. I know we did a nice one with hearts, but I want to create a specification "from scratch" to have a complete example of doing so.
>
> I want to create some for Halloween. I have various colored filaments (black, purple, green, pumpkin colored, etc.) and want to create a small collection.
>
> One might be in black and have cutouts of ravens and even have "Nevermore" stenciled into it too. Another could be in pumpkin color and have a jack-o-lantern face on the sides.
>
> One thing I tend to do is put a strip of white printer paper on the inside of the candle to serve as a diffuser so you can see the shape more clearly and not just look through it to the led inside.
>
> I think I want the specification to have the dimensions of the LED tea light as a best practice, and then settle on the basic dimensions of the holder as we iterate.

## What that already contained

Worth naming, because it is easy to read the brief above as vague and it is not. It fixes four things:

- **A collection, not a part.** Several holders that belong together, differing by motif and filament colour. That is what put the shared envelope in `assemblies/halloween_lantern.py` rather than in any one part.
- **The paper diffuser is standing practice**, described as something the user already does. Which makes it a design input, not an accessory — it shares the puck's fit clearance and it is what evens out the light.
- **The tea light's dimensions are the durable part.** Asked for explicitly, and as "best practice" — i.e. belonging to the process, not to one holder.
- **The holder's own dimensions are expected to move.** Stated up front as something to settle by iterating, which is a licence to start wide.

## What it did not contain, and had to be asked

- Round or flat-faced. (Answered: round.)
- How the lettering survives being cut out. (Answered: pierced, stencilled.)
- Size and posture. (Answered: same footprint as before, taller.)
- How ravens and word compose on the wall. (Deliberately left open — the first renders decide it.)

## What only calipers could settle

The brief asked for the tea light's dimensions to be recorded. It could not supply them, and the previous holder had been built on published figures that were never checked. Measuring produced the one genuine surprise of the session:

**The puck is not a glowing disc with a flat emitting top face**, which is what `tealight_holder` assumed. It is an opaque base with a narrow flame standing on it and the LED inside the lower part of that flame. So the light comes from a short thin column partway up, the bottom half of the holder can never be lit, and the canvas is much shorter than it looks.

That fact is why `spec.md` reads the way it does, and it did not exist at the time the brief was written.
