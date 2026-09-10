"""Strip identifying metadata from images bound for publication, losslessly.

A photograph of a finished part carries far more than the picture: the second
it was taken, the camera's make, model and serial number, the lens, the editing
software, and a timezone. `cad promote` scrubbed dates out of the text it
published while copying images through untouched, which undid the point — one
JPEG's DateTimeOriginal rebuilds the calendar that withholding `history.md`
exists to protect, and a serial number ties together every photo ever taken
with that camera.

Everything here works at the container level. Compressed image data is copied
byte for byte and never decoded or re-encoded, so a published image is
pixel-identical to its working copy.

Two things survive, because losing them visibly damages the image and neither
identifies anyone:

- a JPEG's EXIF **orientation**, rewritten as a one-tag EXIF block — without it
  a portrait photo publishes sideways;
- **colour profiles** (JPEG ICC, PNG iCCP/sRGB/gAMA/cHRM, GIF ICCRGBG1012) —
  without them the colours shift.

No third-party dependencies, deliberately: this runs on every promotion, and a
publishing safeguard that quietly does nothing when a tool is missing is worse
than none.
"""
import struct
from pathlib import Path

SUPPORTED = {".jpg", ".jpeg", ".png", ".gif"}


class UnsupportedImage(ValueError):
    pass


def supports(path: Path) -> bool:
    return Path(path).suffix.lower() in SUPPORTED


def strip(src: Path, dst: Path) -> int:
    """Write `src` to `dst` without its metadata; return how many blocks were dropped."""
    src, dst = Path(src), Path(dst)
    suffix = src.suffix.lower()
    if suffix not in SUPPORTED:         # before reading, so the refusal names the real problem
        raise UnsupportedImage(f"{src.name}: no metadata stripper for {suffix}")
    data = src.read_bytes()
    if suffix in (".jpg", ".jpeg"):
        out, dropped = _jpeg(data)
    elif suffix == ".png":
        out, dropped = _png(data)
    elif suffix == ".gif":
        out, dropped = _gif(data)
    else:
        raise UnsupportedImage(f"{src.name}: no metadata stripper for {suffix}")
    dst.write_bytes(out)
    return dropped


# ---------------------------------------------------------------- JPEG

_APP0_JFIF, _APP14_ADOBE = 0xE0, 0xEE


def _jpeg(data: bytes) -> tuple[bytes, int]:
    if data[:2] != b"\xff\xd8":
        raise UnsupportedImage("not a JPEG (no SOI marker)")
    out = bytearray(b"\xff\xd8")
    dropped, orientation, exif_at = 0, None, None
    i = 2
    while True:
        if data[i] != 0xFF:
            raise UnsupportedImage(f"corrupt JPEG: expected a marker at byte {i}")
        while data[i] == 0xFF:          # fill bytes may pad before a marker
            i += 1
        marker = data[i]
        i += 1
        if marker == 0xD9:              # EOI. Anything after it (a multi-picture
            out += b"\xff\xd9"          # secondary image, trailing junk) carries
            if i < len(data):           # metadata of its own and is dropped.
                dropped += 1
            break
        if 0xD0 <= marker <= 0xD7 or marker == 0x01:
            out += bytes((0xFF, marker))
            continue
        (length,) = struct.unpack(">H", data[i:i + 2])
        payload = data[i + 2:i + length]
        segment = bytes((0xFF, marker)) + data[i:i + length]
        i += length
        if marker == 0xDA:              # start of scan: header, then entropy-coded data
            out += segment
            j = i
            while True:                 # up to the next real marker; FF00 is a stuffed
                j = data.index(b"\xff", j)      # byte and FFD0-D7 are restarts
                following = data[j + 1]
                if following == 0x00 or 0xD0 <= following <= 0xD7:
                    j += 2
                elif following == 0xFF:
                    j += 1
                else:
                    break
            out += data[i:j]
            i = j
            continue
        if marker == 0xE1:              # APP1: EXIF or XMP
            if payload.startswith(b"Exif\x00\x00"):
                orientation = _exif_orientation(payload[6:])
                exif_at = len(out)
            dropped += 1
            continue
        if 0xE0 <= marker <= 0xEF:      # other APPn: keep JFIF, Adobe and ICC only
            if marker in (_APP0_JFIF, _APP14_ADOBE) or (marker == 0xE2 and payload.startswith(b"ICC_PROFILE\x00")):
                out += segment
            else:
                dropped += 1
            continue
        if marker == 0xFE:              # comment
            dropped += 1
            continue
        out += segment                  # tables, frame headers: the image itself
    if orientation not in (None, 1):
        out[exif_at:exif_at] = _orientation_app1(orientation)
    return bytes(out), dropped


def _exif_orientation(tiff: bytes):
    try:
        order = {b"II": "<", b"MM": ">"}[tiff[:2]]
        (ifd,) = struct.unpack(order + "I", tiff[4:8])
        (count,) = struct.unpack(order + "H", tiff[ifd:ifd + 2])
        for k in range(count):
            entry = ifd + 2 + 12 * k
            tag, kind, _ = struct.unpack(order + "HHI", tiff[entry:entry + 8])
            if tag == 0x0112 and kind == 3:
                return struct.unpack(order + "H", tiff[entry + 8:entry + 10])[0]
    except (KeyError, IndexError, struct.error):
        pass
    return None


def _orientation_app1(value: int) -> bytes:
    """A minimal EXIF block carrying nothing but Orientation."""
    tiff = (b"MM\x00\x2a" + struct.pack(">I", 8) + struct.pack(">H", 1)
            + struct.pack(">HHIHH", 0x0112, 3, 1, value, 0) + struct.pack(">I", 0))
    payload = b"Exif\x00\x00" + tiff
    return b"\xff\xe1" + struct.pack(">H", len(payload) + 2) + payload


# ---------------------------------------------------------------- PNG

# Ancillary chunks that describe the pixels rather than the photographer.
# Everything else ancillary — tEXt, zTXt, iTXt, eXIf and tIME, the last of which
# is a modification timestamp — is dropped. Critical chunks are always kept.
_PNG_KEEP = {b"tRNS", b"cHRM", b"gAMA", b"iCCP", b"sBIT", b"sRGB", b"cICP", b"bKGD",
             b"pHYs", b"sPLT", b"hIST", b"acTL", b"fcTL", b"fdAT"}
_PNG_SIG = b"\x89PNG\r\n\x1a\n"


def _png(data: bytes) -> tuple[bytes, int]:
    if not data.startswith(_PNG_SIG):
        raise UnsupportedImage("not a PNG (bad signature)")
    out, dropped, i = bytearray(_PNG_SIG), 0, len(_PNG_SIG)
    while i < len(data):
        (length,) = struct.unpack(">I", data[i:i + 4])
        kind = data[i + 4:i + 8]
        chunk = data[i:i + 12 + length]
        i += 12 + length
        critical = not (kind[0] & 0x20)
        if critical or kind in _PNG_KEEP:
            out += chunk
        else:
            dropped += 1
        if kind == b"IEND":
            break
    if i < len(data):
        dropped += 1
    return bytes(out), dropped


# ---------------------------------------------------------------- GIF

# Application extensions that make the file work: looping, and a colour profile.
_GIF_KEEP_APP = {b"NETSCAPE2.0", b"ANIMEXTS1.0", b"ICCRGBG1012"}


def _gif(data: bytes) -> tuple[bytes, int]:
    if data[:6] not in (b"GIF87a", b"GIF89a"):
        raise UnsupportedImage("not a GIF (bad signature)")

    def past_subblocks(j):
        while True:
            size = data[j]
            j += 1 + size
            if size == 0:
                return j

    flags = data[10]
    i = 13 + (3 * (2 << (flags & 7)) if flags & 0x80 else 0)
    out, dropped = bytearray(data[:i]), 0
    while True:
        block = data[i]
        if block == 0x3B:               # trailer
            out += b";"
            if i + 1 < len(data):
                dropped += 1
            break
        if block == 0x2C:               # image: descriptor, local colour table, LZW data
            start, local = i, data[i + 9]
            i += 10 + (3 * (2 << (local & 7)) if local & 0x80 else 0) + 1
            i = past_subblocks(i)
            out += data[start:i]
            continue
        if block == 0x21:               # extension
            label, start = data[i + 1], i
            end = past_subblocks(i + 2)
            if label == 0xFE:           # comment
                keep = False
            elif label == 0xFF:         # application: XMP is one of these
                keep = data[i + 3:i + 14] in _GIF_KEEP_APP
            else:                       # graphic control, plain text
                keep = True
            if keep:
                out += data[start:end]
            else:
                dropped += 1
            i = end
            continue
        raise UnsupportedImage(f"corrupt GIF: unexpected block 0x{block:02x} at byte {i}")
    return bytes(out), dropped
