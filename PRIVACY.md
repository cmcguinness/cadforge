# Two collections: what is public and what is not

`cadforge` is meant to be shared. Most of what you design with it probably is
not. So parts live in one of two trees, in the same working directory:

```
cadforge/                 ← public repo (this one)
  cadkit/  printer.py  template/  cad  README.md  CLAUDE.md
  examples/<name>/        ← published parts. Committed here.
  parts/                  ← .gitignore'd by this repo…
    .git/                 ← …and its own separate, private repo
    assemblies/           ← private shared interfaces
    <name>/
```

The harness treats them identically — same contract, same commands, same
everything. Which tree a part is in is a statement about whether it is
published, not about how it is built. `cad status` shows both and labels them.

One working directory, one virtualenv, one `./cad build <anything>`. That
matters: a separation that adds daily friction is one you route around.

## Setting it up

The public repo is a normal clone. The private tree is a second repo nested
inside it:

```bash
cd cadforge/parts
git init
git remote add origin git@github.com:<you>/<something>-parts.git   # private!
git add -A && git commit -m "my parts"
git push -u origin main
```

`cadforge/.gitignore` contains `/parts/`, so the outer repo never sees any of
it — not the files, not the history, not the remote.

**Mind which repo you are in.** `git status` at the repo root reports on the
public repo and will not mention anything under `parts/`. Run git from inside
`parts/` for the private one. This is the one real cost of the arrangement.

## Private assemblies

`assemblies/` has no `__init__.py`, so it is a Python namespace package and
merges across both collection roots. A shared interface used only by private
parts lives at `parts/assemblies/<name>.py` and imports as `assemblies.<name>`
with no special handling.

`cad promote` refuses to publish a part that imports a still-private assembly,
because it would be an example that cannot build the moment somebody clones the
repo.

## Promotion is publishing, not a file move

```bash
cad promote <name>          # dry run: lists exactly what would become public
cad promote <name> --yes
```

A part carries more than geometry. `notes.md` records what you believed, what
turned out to be true, and what a failed print cost. `history.md` records every
parameter you tried and every one you rejected, with your reasons attached.
`prints.md` records measurements of your actual desk, your actual components,
your actual room.

That record is exactly what makes a promoted part worth reading, and exactly
what deserves a look before it goes out. So `cad promote` lists the files and
their sizes and does nothing until you pass `--yes`.

Things worth checking before confirming:

- **Measurements of your home, body, or possessions.** A desk thickness is
  harmless; some measurements are not.
- **Notes written in frustration.** `notes.md` is at its most valuable when
  written immediately after a failure, which is also when it is least
  considered.
- **Anything naming another person, a client, or an unreleased product.**
- **Whether the iteration history tells a story you want told.** It usually
  reflects well — it is a record of careful work — but it is a record.

The private original is left in place; delete it once you are happy. A name
present in both collections is an error rather than a precedence rule, and
`cad status` will refuse it, because it means a promoted part and its private
original have diverged.

## Going the other way

There is no `cad demote`. Unpublishing does not work — if it has been pushed, it
is out. Move the directory back by hand and remove it from the public repo's
history yourself, knowing that anyone who cloned already has it.
