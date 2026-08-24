# inspiration

Source imagery this part was made from: the reference photo, the drawing, the AI-generated silhouette, the thing you saw and wanted to build.

**Put it here rather than at the part root**, and put it here *before* tracing anything. Two reasons, both learned the expensive way:

- **A source that lives outside the repo stops existing.** `raven_lantern`'s artwork pointed into a per-session chat image cache. By the time anyone noticed, it was gone — so that outline can now only be edited as coordinates, never re-traced against what it was supposed to look like. Artwork is part of the record, exactly like `notes.md`.
- **A part traced from a picture is not described without the picture.** The outline data in `*_outline.py` is a list of numbers. Whether it still *reads* as the subject is a question only the original can settle.

A trace script belongs beside the part and should read from here:

```python
SRC = Path(__file__).parent / "inspiration" / "<name>.png"
```

Delete this file once there is real artwork in the directory.
