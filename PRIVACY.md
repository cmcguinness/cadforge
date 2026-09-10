# Two collections: what is public and what is not

**If you have just cloned this and want to design something: put it in `parts/`.** That directory is git-ignored, `cad new` scaffolds there by default, and nothing you make will ever be committed to a repo you did not set up yourself. You can stop reading here.

The rest of this file is for the case where you *do* want some of your work public — normally in **your own fork or your own remote**, not upstream. `examples/` is not a submissions folder: it is the worked examples that ship with the harness, and in your fork it becomes wherever your published parts go. (A pull request is of course possible, and a part that teaches something the existing four do not is welcome — but that is a deliberate offer, not what `cad promote` does.)

The tooling is meant to be shared. Most of what you design with it probably is not. So parts live in one of two trees, in the same working directory:

```
cadforge/                 ← public repo (this one)
  cadkit/  printer.py  template/  cad  README.md  CLAUDE.md
  examples/<name>/        ← published parts. Committed here.
  parts/                  ← .gitignore'd by this repo…
    .git/                 ← …and its own separate, private repo
    assemblies/           ← private shared interfaces (parts that FIT)
    projects/<name>/      ← private sets (parts that BELONG together)
    <name>/
```

The harness treats them identically — same contract, same commands, same everything. Which tree a part is in is a statement about whether it is published, not about how it is built. `cad status` shows both and labels them.

One working directory, one virtualenv, one `./cad build <anything>`. That matters: a separation that adds daily friction is one you route around.

## Setting it up

The public repo is a normal clone. The private tree is a second repo nested inside it:

```bash
cd cadforge/parts
git init
git remote add origin git@github.com:<you>/<something>-parts.git   # private!
git add -A && git commit -m "my parts"
git push -u origin main
```

`cadforge/.gitignore` contains `/parts/`, so the outer repo never sees any of it — not the files, not the history, not the remote.

**Mind which repo you are in.** `git status` at the repo root reports on the public repo and will not mention anything under `parts/`. Run git from inside `parts/` for the private one. This is the one real cost of the arrangement.

## Private assemblies and projects

`assemblies/` and `projects/` have no `__init__.py`, so they are Python namespace packages and merge across both collection roots. Something used only by private parts lives under `parts/` and imports with no special handling:

- `parts/assemblies/<name>.py` → `assemblies.<name>`
- `parts/projects/<name>/shared.py` → `projects.<name>.shared`

**Anything at the repo root is public**, because the root tree is committed. That is the trap: a private project's `shared.py` was once written to the root `assemblies/`, where it was untracked but *not* ignored — one `git add .` from being published. Only `/parts/` is git-ignored.

`cad promote` refuses to publish a part that imports a still-private assembly, or that belongs to a still-private **project**. The second matters more than it sounds: an assembly is obviously code, whereas a project carries a `project.md` full of measurements, workshop standards and a slicer profile — a document nobody thinks of as one until it is public.

## Promotion is publishing, not a file move

```bash
cad promote <name>          # dry run: lists exactly what would become public
cad promote <name> --yes
```

It **copies** a part from the ignored tree into the committed one — *your* committed one. Whether that is actually public depends entirely on where you push, and the command cannot know: it can only tell you what stops being ignored. If your fork is private, promoting is a filing decision and nothing more. Read the rest of this section as though it were public anyway, because forks get opened up later.

**The private copy stays, and stays authoritative.** The published one is a snapshot: keep refining in `parts/`, and re-run `cad promote` to refresh it. `cad build <name>` always resolves to the working copy, so you cannot accidentally edit the thing that the next promotion overwrites. `cad status` shows one row per part and marks it `private*` when a snapshot is public.

### What is withheld

**The iteration ledger is never published.** `history.jsonl` and `history.md` carry one dated row per build, and the dates alone reconstruct which evenings you spent how — a fairly complete picture of your schedule, offered to anyone who clones the repo. It stays in the working copy, where it does its real job of stopping the search circling.

**Dates are stripped from everything else that goes out.** Withholding the ledger by itself achieves very little, which is worth stating because it is not obvious: `prints.md` headings are dated, `accepted/ACCEPTED.md` carries a `date` field, specs cite when a measurement was taken, and the accepted mesh is named `<part>-YYYYmmdd-HHMM.stl` — precise to the minute. Any one of those rebuilds the calendar. So promotion rewrites all of them, and renames the mesh to `<part>.stl`.

**Image metadata goes too, and it is the bigger leak.** A photograph carries the second it was taken, the camera's make, model and **serial number**, the lens, the editing software and a timezone. Any one of those undoes the date scrubbing, and a serial number ties together every photo ever taken with that camera. Promotion copied images through untouched for a long time, so this was published for a while before anyone looked. Every published JPEG, PNG and GIF is now rewritten without it by `cadkit/imgmeta.py`, at the container level: the compressed image data is copied byte for byte, so the published image is pixel-identical. EXIF orientation and colour profiles are kept, because losing them turns photos sideways or shifts their colours. An image in a format it cannot strip (WebP, for one) is refused before anything is copied, rather than published as-is.

**Two more places a date hides.** A render sheet has the time it was made drawn across its top — on purpose, because an undated render is indistinguishable from a stale one during review — so promotion crops that banner off the published copy. A saved Bambu Studio project (`.3mf`) is a zip that records its creation and modification dates, a timestamp on every entry in the archive, and the MakerWorld account ID of whoever saved it; promotion empties those fields, restamps every entry to 1980-01-01, and clears any print-host address or credential (`cadkit/threemf.py`). A project that carries sliced G-code is refused, because the G-code header records when it was sliced.

A date form the scrubber does not recognise becomes a visible `[date removed]` rather than passing through. That is deliberate: a silent scrubber you cannot audit is worse than a loud one. If you see that marker in `examples/`, teach `_scrub` in `cadkit/cli.py` the new form — do not hand-edit the published file, which the next promotion will overwrite.

### What still goes out, and deserves a look

`notes.md` records what you believed, what turned out to be true, and what a failed print cost. `prints.md` records measurements of your actual components and your actual room. `inspiration/` carries the artwork the part was traced from. That record is exactly what makes a published part worth reading, and exactly what deserves a look first — so `cad promote` lists everything and does nothing until you pass `--yes`.

Things worth checking before confirming:

- **Measurements of your home, body, or possessions.** A desk thickness is harmless; some measurements are not.
- **Notes written in frustration.** `notes.md` is at its most valuable when written immediately after a failure, which is also when it is least considered.
- **Anything naming another person, a client, or an unreleased product.** Household reviewers included — write "a household reviewer", not a name.
- **Artwork you do not have the right to redistribute.** `inspiration/` is published in full.

## Going the other way

There is no `cad demote`. Unpublishing does not work — if it has been pushed, it is out. Move the directory back by hand and remove it from the public repo's history yourself, knowing that anyone who cloned already has it.
