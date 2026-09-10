"""Scrub a saved slicer project (.3mf) of who made it and when, for publication.

A Bambu Studio project is a zip, and it records more than the plate: the date
it was created and last modified — in the model's metadata, and again as the
timestamp of every entry in the archive — and the MakerWorld account ID of
whoever saved it (`DesignerUserId`). `_undated` already took the date out of
the filename; the same date, and an account ID, went out inside the file.

What changes:

- `3D/3dmodel.model`: the creation and modification dates and the designer
  fields are emptied. Bambu Studio treats them as optional.
- `Metadata/project_settings.config`: any print-host address or credential is
  emptied. A LAN printer's address is nobody else's business.
- thumbnails: PNG metadata stripped, as for any published image.
- every archive entry is restamped to 1980-01-01, the zip format's epoch.

Everything else — geometry, plate layout, slicer settings — is copied as it
is, because that is the point of publishing a project.

A project carrying sliced G-code is refused: its header records the time it
was sliced. And if a date is still present anywhere outside the mesh after
scrubbing, that is refused too, loudly, rather than published — the same rule
`_scrub` follows with `[date removed]`: a scrubber that meets a form it does
not know should say so.
"""
import re
import zipfile
from pathlib import Path

from . import imgmeta

EPOCH = (1980, 1, 1, 0, 0, 0)
MODEL_FIELDS = ("CreationDate", "ModificationDate", "Designer", "DesignerUserId", "DesignerCover")
HOST_KEYS = ("print_host", "print_host_webui", "printhost_apikey", "printhost_user",
             "printhost_password", "printhost_cafile", "printhost_port")
_DATE = re.compile(rb"20\d\d-\d\d-\d\d")


class UnsupportedProject(ValueError):
    pass


def scrub(src, dst) -> int:
    """Write the project at `src` to `dst` (a path or a binary file object).

    Returns how many identifying values were cleared, not counting the entry
    timestamps, which are always rewritten.
    """
    name_of = Path(src).name
    cleared = 0

    def empty(match):
        nonlocal cleared
        if match.group(2):
            cleared += 1
        return match.group(1) + match.group(3)

    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, "w") as zout:
        for info in zin.infolist():
            entry = info.filename
            if entry.lower().endswith(".gcode"):
                raise UnsupportedProject(
                    f"{name_of} contains sliced G-code ({entry}), whose header records when it "
                    f"was sliced. Save the project unsliced and publish that.")
            data = zin.read(info)
            if entry == "3D/3dmodel.model":
                for field in MODEL_FIELDS:
                    data = re.sub(rb'(<metadata name="%s"[^>]*>)([^<]*)(</metadata>)' % field.encode(),
                                  empty, data)
            elif entry == "Metadata/project_settings.config":
                for key in HOST_KEYS:
                    data = re.sub(rb'("%s"\s*:\s*")([^"]*)(")' % key.encode(), empty, data)
            elif entry.lower().endswith(".png"):
                data, dropped = imgmeta._png(data)
                cleared += dropped
            if not entry.startswith("3D/Objects/") and not entry.lower().endswith(".png"):
                leftover = _DATE.search(data)
                if leftover:
                    raise UnsupportedProject(
                        f"{name_of}: {entry} still carries a date ({leftover.group().decode()}) after "
                        f"scrubbing. Teach cadkit/threemf.py that field rather than publishing it.")
            out = zipfile.ZipInfo(entry, date_time=EPOCH)
            out.compress_type = info.compress_type
            out.external_attr = info.external_attr
            zout.writestr(out, data)
    return cleared
