"""What to do next — the decision procedure.

The premise this whole repo rests on
------------------------------------
Designing a part is a search, and **you are the objective function.** Nothing
else can say whether a shape is the shape you wanted. Generating a candidate is
cheap and getting cheaper; evaluating one costs a human judgment call and does
not get cheaper at all. Your attention is the scarce resource, and everything
here exists to spend less of it:

  * **Criteria** make each evaluation cheap and repeatable — you answer a
    question instead of forming an opinion from scratch.
  * **Assertions** are the fraction of the objective function that got compiled
    into code, so it can be evaluated without spending you at all.
  * **Renders** let a reviewer who cannot open a viewer evaluate at all.
  * **History** stops the search re-entering a basin it already left, which is
    the only way successive approximation degenerates into a random walk.
  * **This module** removes the last tax: deciding what to do next.

Never make the human work out what the next move is. There is always exactly
one, it is derivable from what is on disk, and it should be printed without
being asked for.

The rules below are ordered. The first that matches wins, because the earlier
ones are blocking: there is no point reviewing renders of a part whose criteria
cannot settle anything.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import history, part as partlib
from .part import CONSTRUCTION, FUNCTION, PRINT, UNCLASSIFIED, collection_of

# How many JUDGED-AND-REJECTED iterations in one generation before the search is
# called stalled. Past this, the productive move is almost never another
# parameter tweak — it is admitting the criteria do not capture what you want.
#
# Was 5, and 5 was too eager even counting only judged laps. A part whose shape
# is genuinely being discovered — where each render answers a question nobody
# had asked yet — spends a lot of rejections making real progress, and being
# told the target is wrong is bad advice at that point. This wants to catch
# circling, and circling is what the oscillation guard already detects
# precisely; this counter is the blunt backstop behind it, so it should be
# generous. Still a guess, and still uncalibrated against a real refinement run.
STALL_AFTER = 15


@dataclass(frozen=True)
class Advice:
    action: str            # the imperative — what to actually do
    why: str               # one line; why this and not something else
    command: str | None = None   # the command that does it, if there is one
    urgent: bool = False   # something is wrong, not merely unfinished
    quiet: bool = False    # "nothing to do" — true, and noise on a board

    @property
    def actionable(self) -> bool:
        return not self.quiet


def _newest(paths) -> float:
    return max((p.stat().st_mtime for p in paths if p.exists()), default=0.0)


def repo_action() -> Advice | None:
    """A repo-wide blocker, if there is one — checked before any part.

    Bed size, nozzle and material feed every printability check and several
    parts' assertions. Running against another machine's numbers produces
    checks that pass for a printer you do not own, which is worse than no
    checks at all.
    """
    import printer

    if not printer.CONFIGURED:
        return Advice(
            "Configure your printer and material.",
            "Running on generic defaults: every bed-fit check, mass estimate "
            "and minimum-wall assertion is currently answering for a machine "
            "nobody owns.",
            "./cad setup", urgent=True)
    return None


def orientation(dirs: list[Path]) -> list[Advice]:
    """Repo-wide advice, stated ONCE — not once per part.

    Two things are true of the repo rather than of any part in it, and both
    were previously discovered by asking every part in turn and getting the
    same answer back N times. A newcomer's first `cad next` printed "configure
    your printer" four times, about four finished lanterns they did not make.

    The second rule is the one that was missing entirely. Every rule in
    `next_action` reasons from a part directory, so a person who has just
    cloned this and owns no parts falls through all of them — and the board,
    whose entire purpose is to say what to do next, said nothing about what to
    do next. That is the one moment when "what now?" is the whole question.
    """
    out = []
    blocker = repo_action()
    if blocker is not None:
        out.append(blocker)

    if not any(collection_of(d) == "private" for d in dirs):
        out.append(Advice(
            "Design something — describe the part you want to Claude.",
            "Nothing in parts/ yet. You are not meant to drive this by typing "
            "commands: say what you want in the conversation and Claude drafts "
            "the spec, writes the model, runs the builds and reads the checks. "
            "examples/README.md shows four finished parts and how to extend "
            "them.",
            "./cad new <name>   # if you would rather start it by hand"))
    return out


def next_action(part_dir: Path, machine: bool = True) -> Advice:
    """The single next thing to do for this part.

    `machine=False` suppresses the repo-wide printer blocker, for callers that
    state it once themselves — see `orientation`.
    """
    blocker = repo_action() if machine else None
    if blocker is not None:
        return blocker

    name = part_dir.name
    spec = part_dir / "spec.md"
    model = part_dir / "model.py"
    review = part_dir / "build" / "review" / "sheet.png"
    accepted = part_dir / "accepted"

    # --- 1. Is there a spec at all? ---------------------------------------
    if not spec.is_file():
        return Advice("Write spec.md — what it is for, and how you will know it worked.",
                      "Geometry written before a spec becomes the spec by default.",
                      f"$EDITOR {spec}")

    crit = partlib.criteria_by_axis(spec)
    n_total = sum(len(v) for v in crit.values())

    # A part staged `done` has been validated in the hand, and the stage is
    # declared rather than inferred — so it outranks every rule below, all of
    # which reason from what happens to be on disk. Without this, a finished
    # part still carrying a `good` verdict and an STL in build/ is advised to
    # go and print it again.
    if partlib.read_stage(spec) == "done":
        open_crit = [c for v in crit.values() for c in v if not c.checked]
        if open_crit:
            return Advice(
                f"{len(open_crit)} criteria are unticked on a part marked done.",
                "Either the criterion was settled and nobody recorded it, or "
                "the part is not actually done. Not urgent — the object exists "
                "and works; this is the ledger being behind the world.",
                f"$EDITOR {spec}")
        return Advice("Nothing outstanding — validated in the hand.",
                      "Revisit only on a new requirement.", None, quiet=True)

    # --- 2. Criteria: the only part of a spec that can settle anything -----
    if n_total == 0:
        return Advice("Add acceptance criteria to spec.md.",
                      "Prose sets context; only a checklist can settle a review. "
                      "Without criteria every evaluation starts from scratch.",
                      f"$EDITOR {spec}", urgent=True)

    # The lesson from this repo's first worked example: criteria stated only on
    # the construction axis converge tightly on a well-formed useless object.
    # An axis you do not state stays unconstrained however detailed the rest is.
    if not crit[FUNCTION] and not crit[UNCLASSIFIED]:
        return Advice(
            "Add criteria under '### Does it do its job?' in spec.md.",
            "Every criterion here is about construction. A list of geometric "
            "invariants will certify a part that is built perfectly and does "
            "nothing — it has happened in this repo.",
            f"$EDITOR {spec}", urgent=True)

    gen = partlib.generation(spec)

    # --- 3. Is there geometry? --------------------------------------------
    if not model.is_file():
        return Advice("Write model.py to satisfy the spec.",
                      f"{n_total} criteria are settled; the search can start.",
                      f"$EDITOR {model}")

    entries = [e for e in history.read(part_dir) if e.generation == gen]

    if not entries:
        return Advice("Build it.",
                      "No iteration recorded against the current criteria.",
                      f"./cad build {name}")

    last = entries[-1]

    # --- 4. Has the model moved since the last build? ---------------------
    if model.stat().st_mtime > _newest([review]):
        return Advice("Rebuild — model.py has changed since the last render.",
                      "The sheet on disk no longer shows the current geometry.",
                      f"./cad build {name}")

    # --- 5. Convergence check, before asking for another evaluation -------
    stalled = history.laps(part_dir, gen)
    if stalled >= STALL_AFTER:
        return Advice(
            f"Revise the criteria in spec.md — {stalled} judged iterations "
            f"without a 'good'.",
            "Tuning parameters moves within the target; this many laps means "
            "the target is wrong or unstated. Changing the criteria opens a "
            "new generation and resets the history.",
            f"$EDITOR {spec}", urgent=True)

    # --- 6. The evaluation itself -----------------------------------------
    if last.verdict == "untested":
        return Advice(
            f"Open {review.relative_to(part_dir.parent.parent)} and read it "
            f"against the criteria, then record a verdict.",
            "This is the evaluation step. Nothing else can do it.",
            f"./cad accept {name} good|bad|mixed \"why\"")

    if last.verdict in ("bad", "mixed"):
        return Advice("Change one parameter and rebuild.",
                      f"Iteration #{last.i} was {last.verdict}"
                      + (f" — {last.note}" if last.note else "")
                      + ". Read history.md first; some values are ruled out.",
                      f"./cad build {name} --note \"<what you are testing>\"")

    # --- 7. Verdict is good: get it to the plate --------------------------
    unresolved_print = [c for c in crit[PRINT] if not c.checked]

    if last.verdict == "good":
        stl = list(part_dir.glob("build/*.stl"))
        if not stl:
            return Advice("Export the mesh.",
                          "The renders satisfy the criteria they can settle.",
                          f"./cad build {name} --stl")
        return Advice("Slice it in Bambu Studio and print it.",
                      f"{len(unresolved_print)} criteria can only be settled by "
                      f"the physical object." if unresolved_print
                      else "The mesh is ready.",
                      f"./cad accept {name} printed \"<what came out>\"  # after printing")

    if last.verdict == "printed":
        if unresolved_print:
            return Advice(
                "Record the print in prints.md and tick off what it settled.",
                f"{len(unresolved_print)} print-only criteria are still open. "
                "Measurements taken now are the ones that stop you paying for "
                "this print twice.",
                f"$EDITOR {part_dir / 'prints.md'}")
        if not accepted.is_dir():
            return Advice("Freeze the accepted mesh.",
                          "Every print-only criterion is settled but the STL "
                          "that produced the object is still in git-ignored "
                          "build output.",
                          f"./cad accept {name} good \"validated in the hand\"")

        # The slicer project is a deliverable and the only file here that
        # nothing regenerates — the settings in it were paid for in failed
        # prints. Two have already been lost from git-ignored build/ output.
        if not list(accepted.glob("*.3mf")) and not list(part_dir.glob("build/*.3mf")):
            return Advice(
                "Save the slicer project into accepted/.",
                "The mesh is frozen but the settings that made it print are "
                "not. Plate layout, supports and per-object tweaks live only "
                "in the .3mf, and nothing in this repo can regenerate them. "
                "Two have already been lost by leaving them in build/.",
                f"Save As → {(accepted / (name + '.3mf'))}")
        return Advice("Mark it done.",
                      "Every criterion is settled and the mesh is frozen.",
                      f"./cad stage {name} done")

    return Advice("Nothing outstanding.", "All criteria settled.", None, quiet=True)


def board(dirs: list[Path], all: bool = False) -> list[tuple[Path, Advice]]:
    """Next action for every part that HAS one, most urgent first.

    Parts with nothing outstanding are dropped rather than listed saying so.
    A board of "nothing to do" lines is not a board — and the finished
    examples, which nobody is working on, otherwise crowd out the one part
    that actually needs something. `all=True` keeps them.

    The printer blocker is left to `orientation`, which states it once.
    """
    rows = [(d, next_action(d, machine=False)) for d in dirs]
    if not all:
        rows = [r for r in rows if r[1].actionable]
    rows.sort(key=lambda r: (not r[1].urgent, r[0].name))
    return rows
