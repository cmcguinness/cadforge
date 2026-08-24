"""Per-part iteration history — the memory that keeps refinement from circling.

The failure this exists to prevent
----------------------------------
Refinement loops oscillate. Wall thickness goes 2.0 → 3.0 because a print felt
flimsy, then 3.0 → 2.4 because it looked chunky, then back toward 3.0 for the
same reason as the first time. Each step is locally reasonable. The information
that would stop it — "2.4 was tried in iteration 3 and rejected as flimsy" — is
the thing nobody writes down, because at the time it feels obvious.

So it is not written down by hand. Every build compares the current parameters
against the recorded history and appends an entry when they differ, with the
diff computed rather than remembered. Returning to a parameter set that already
carries a verdict is reported loudly.

Two files, both git-tracked, both in the part's own directory:

  history.jsonl   append-only, one JSON object per iteration. The record.
  history.md      a rendered table. The thing a human or an agent actually reads
                  before proposing the next change.

An entry's verdict starts as "untested" and is filled in later — after a render
review, or after a print. That lag is the point: the entry is created when the
change is made, so it cannot be forgotten by the time the outcome is known.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

VERDICTS = {
    "untested": "built, not yet judged",
    "good": "satisfies the acceptance criteria",
    "bad": "rejected — do not return to these values",
    "mixed": "partly right; see the note",
    "printed": "physically printed; see prints.md",
}


@dataclass
class Entry:
    i: int
    date: str
    digest: str
    params: dict
    changed: dict            # {param: [old, new]}
    verdict: str
    note: str
    generation: str = "nocrit"   # hash of the acceptance criteria at build time

    @classmethod
    def from_json(cls, d: dict) -> "Entry":
        return cls(
            i=d["i"], date=d.get("date", ""), digest=d["digest"],
            params=d.get("params", {}), changed=d.get("changed", {}),
            verdict=d.get("verdict", "untested"), note=d.get("note", ""),
            generation=d.get("generation", "nocrit"),
        )


def _path(part_dir: Path) -> Path:
    return part_dir / "history.jsonl"


def read(part_dir: Path) -> list[Entry]:
    p = _path(part_dir)
    if not p.is_file():
        return []
    out = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if line:
            out.append(Entry.from_json(json.loads(line)))
    return out


def _same(a, b) -> bool:
    """Whether two parameter values are the same value.

    Compared after a round trip through JSON, because that is what the previous
    entry has already been through and this one has not. A tuple parameter — a
    sign's two lines of text, say — comes back as a list, so a plain `!=` reports
    it as changed on every single build and fills the ledger with rows that
    record nothing. A ledger nobody trusts is a ledger nobody reads.
    """
    return json.dumps(a, sort_keys=True, default=str) == \
        json.dumps(b, sort_keys=True, default=str)


def _diff(old: dict, new: dict) -> dict:
    keys = set(old) | set(new)
    return {k: [old.get(k), new.get(k)] for k in sorted(keys)
            if not _same(old.get(k), new.get(k))}


def record(part_dir: Path, params, note: str = "",
           generation: str = "nocrit") -> tuple[Entry | None, list[Entry]]:
    """Append an entry if these parameters differ from the most recent ones.

    Returns (new_entry_or_None, prior_entries_with_the_same_digest). The second
    element is the oscillation signal: a non-empty list means these exact values
    have been here before, and the caller should say so before more work is done
    on the strength of them.

    Everything is scoped to `generation` — the hash of the acceptance criteria.
    When the criteria change, the target moves, and earlier verdicts were
    answers to a different question. Comparing across that boundary would fire
    the guard on parameters that were only ever rejected under the old
    definition of good.
    """
    all_entries = read(part_dir)
    entries = [e for e in all_entries if e.generation == generation]
    values = params.to_dict()
    digest = params.digest()

    revisits = [e for e in entries if e.digest == digest]
    if entries and entries[-1].digest == digest:
        return None, [e for e in revisits if e.i != entries[-1].i]

    entry = Entry(
        i=len(all_entries) + 1,
        date=date.today().isoformat(),
        digest=digest,
        params=values,
        changed=_diff(entries[-1].params, values) if entries else {},
        verdict="untested",
        note=note,
        generation=generation,
    )
    with _path(part_dir).open("a") as fh:
        fh.write(json.dumps(entry.__dict__, sort_keys=True, default=str) + "\n")
    render_markdown(part_dir)
    return entry, revisits


def set_verdict(part_dir: Path, verdict: str, note: str = "", i: int | None = None) -> Entry:
    if verdict not in VERDICTS:
        raise SystemExit(f"unknown verdict '{verdict}'. one of: {', '.join(VERDICTS)}")
    entries = read(part_dir)
    if not entries:
        raise SystemExit("no history yet — build the part first")
    target = entries[-1] if i is None else next((e for e in entries if e.i == i), None)
    if target is None:
        raise SystemExit(f"no iteration {i}")
    target.verdict = verdict
    if note and note not in target.note:
        # Append rather than replace — a verdict often arrives in stages (renders
        # first, then the print) and each note is a separate observation. Skip
        # exact repeats so re-accepting doesn't stutter.
        target.note = (target.note + " " + note).strip() if target.note else note
    with _path(part_dir).open("w") as fh:
        for e in entries:
            fh.write(json.dumps(e.__dict__, sort_keys=True, default=str) + "\n")
    render_markdown(part_dir)
    return target


def rejected_values(part_dir: Path, generation: str | None = None) -> dict[str, list[tuple]]:
    """{param: [(value, iteration, note), ...]} for every value that was in play
    on an iteration judged 'bad'.

    Consult this before proposing a change. It is deliberately blunt — a value
    appears here if it was present in a rejected iteration, not necessarily
    because it was the cause. That over-reports, which is the safe direction:
    it prompts a look at the note rather than silently blessing a repeat.
    """
    out: dict[str, list[tuple]] = {}
    for e in read(part_dir):
        if e.verdict != "bad":
            continue
        if generation is not None and e.generation != generation:
            continue  # rejected against a target that has since moved
        for k, v in e.params.items():
            out.setdefault(k, []).append((v, e.i, e.note))
    return out


def render_markdown(part_dir: Path) -> Path:
    """Rewrite history.md from the jsonl. Generated — never edit it by hand."""
    entries = read(part_dir)
    lines = [
        f"# {part_dir.name} — iteration history",
        "",
        "<!-- GENERATED from history.jsonl by cadkit/history.py. Do not edit. -->",
        "<!-- Add reasoning to notes.md; add print outcomes to prints.md. -->",
        "",
        # One paragraph per line, deliberately long. A single newline inside a
        # paragraph is a hard line break to Typora and anything else that
        # renders Markdown with breaks-on-newline, which shreds the text.
        # Source-wrapping generated prose is not a kindness to the reader.
        "Read this before proposing a parameter change. An iteration marked **bad** is a direction already ruled out — returning to it needs a reason that did not exist the first time.",
        "",
        "A **generation** is one set of acceptance criteria. Editing the criteria moves the target, so verdicts do not carry across a generation boundary and the oscillation guard does not compare across one.",
        "",
    ]

    if not entries:
        lines += ["_Nothing built yet._", ""]

    seen_gen = None
    for e in entries:
        if e.generation != seen_gen:
            seen_gen = e.generation
            lines += [
                "",
                f"## generation `{e.generation}`",
                "",
                "| # | date | verdict | changed from previous | note |",
                "|---|------|---------|-----------------------|------|",
            ]
        if e.changed:
            chg = ", ".join(f"`{k}` {a} → {b}" for k, (a, b) in e.changed.items())
        else:
            chg = "_first of this generation_"
        note = e.note.replace("|", "\\|") or ""
        lines.append(f"| {e.i} | {e.date} | **{e.verdict}** | {chg} | {note} |")

    rej = rejected_values(part_dir, generation=seen_gen)
    if rej:
        lines += ["", "## Values rejected in the current generation", "",
                  "Over-reports by design: a value is listed because it was in play",
                  "when the iteration was rejected, not because it was proven to be",
                  "the cause. Read the note before reusing one.", ""]
        for k in sorted(rej):
            vals = ", ".join(f"`{v}` (#{i})" for v, i, _ in rej[k])
            lines.append(f"- **{k}**: {vals}")

    out = part_dir / "history.md"
    out.write_text("\n".join(lines) + "\n")
    return out


def summary(part_dir: Path, generation: str | None = None) -> str:
    entries = read(part_dir)
    if generation is not None:
        entries = [e for e in entries if e.generation == generation]
    if not entries:
        return "no iterations"
    last = entries[-1]
    bad = sum(1 for e in entries if e.verdict == "bad")
    return f"{len(entries)} iter, last {last.verdict}" + (f", {bad} rejected" if bad else "")


def laps(part_dir: Path, generation: str) -> int:
    """JUDGED iterations in this generation that did not reach a `good`.

    The convergence counter. Each lap is supposed to cost a human evaluation,
    which is the scarce resource here — so a high count means the search is not
    closing and the criteria, not the parameters, are what to change.

    **An `untested` iteration is not a lap.** It counted as one at first, which
    made the counter measure builds rather than evaluations: a part being worked
    on quickly — geometry rewritten a dozen times in a session without anyone
    being asked to look — tripped the stall warning having consumed no human
    attention whatsoever, and was told its criteria were wrong on the strength
    of that. The rule then fires hardest exactly when it is least applicable,
    which is worse than not existing, because the advice is confident.

    Evidence of a bad target is a human looking at a render and saying no. Only
    that is counted here.
    """
    n = 0
    for e in read(part_dir):
        if e.generation != generation:
            continue
        if e.verdict in ("good", "printed"):
            n = 0
        elif e.verdict != "untested":
            n += 1
    return n
