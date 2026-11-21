#!/usr/bin/env python3
"""make.fun entry: The Passport Page of a Country That Isn't There.

Writes /output/entry.png — an open passport spread for the invented
Republic of Valdoria. Primary renderer uses Pillow; if Pillow is
missing in the grading sandbox, a pure-stdlib renderer draws a
simplified version of the same spread so the program never crashes.
No network. Deterministic output.
"""
import os
import sys

OUT = "/output/entry.png"
W, H = 1024, 1024

# ---------------------------------------------------------------- data
COUNTRY = "REPUBLIC OF VALDORIA"
COUNTRY_NATIVE = "REPUBLIKA E VALDORISË"
CAPITAL = "KESTREL"
LANGUAGE = "Valdorian"

HOLDER = {
    "surname": "MARAKU",
    "given": "ELENA DRITA",
    "sex": "F",
    "dob": "14 JUN 1988",
    "pob": CAPITAL,
    "nationality": "VALDORIAN",
    "number": "VA482917",
    "issue": "12 MAR 2024",
    "expiry": "12 MAR 2034",
    "authority": CAPITAL,
}

# Neighbouring countries; every stamp is dated AFTER the 12 MAR 2024 issue.
STAMPS = [
    ("DRAVNIA", "ARRIVAL", "28 JUN 2024", "ZELENGRAD", (31, 84, 160)),
    ("OSTREK", "DEPARTURE", "03 SEP 2024", "TARNOV", (122, 54, 140)),
    ("MIRAVEL", "ARRIVAL", "17 JAN 2025", "PORT MIRA", (178, 58, 46)),
    ("KORVATH", "DEPARTURE", "09 MAY 2026", "KORVATH BORDER", (26, 110, 74)),
]

VISA_TEXT = ("VISA — VALID FOR THE THREE VALLEYS ONLY. "
             "HOLDER MUST REGISTER AT KESTREL WITHIN 7 DAYS OF ENTRY.")
FEE_TEXT = "FEE PAID — 12 VALDA"


# ---------------------------------------------------------------- MRZ (ICAO 9303, TD3)
def mrz_check(s):
    vals = {str(i): i for i in range(10)}
    for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        vals[ch] = 10 + i
    vals["<"] = 0
    total = 0
    for i, ch in enumerate(s):
        total += vals[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)


def mrz_lines():
    name = "MARAKU<<ELENA<DRITA"
    line1 = ("P<VAL" + name).ljust(44, "<")
    doc = "VA482917<"
    body = (doc + mrz_check(doc) + "VAL" + "880614" + mrz_check("880614")
            + "F" + "340312" + mrz_check("340312") + "<" * 15)
    line2 = body + mrz_check(body)
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    return line1, line2


# ---------------------------------------------------------------- fonts (PIL)
def load_fonts():
    """Return a dict of truetype fonts; fall back to PIL's default font."""
    from PIL import ImageFont
    cands = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    ]
    have = [p for p in cands if os.path.exists(p)]
    bold = next((p for p in have if "Bold" in p and "Sans" in p), None)
    reg = next((p for p in have if "Bold" not in p and "Sans" in p
                and "Mono" not in p), None)
    serif_b = next((p for p in have if "Serif-Bold" in p), None)
    mono = next((p for p in have if "Mono" in p), None)

    def f(path, size):
        if path:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
        return ImageFont.load_default()

    return {
        "head": f(serif_b or bold, 27),
        "head_small": f(bold, 20),
        "sub": f(reg, 13),
        "label": f(bold, 12),
        "value": f(bold, 16),
        "value_sm": f(reg, 15),
        "mrz": f(mono or reg, 16),
        "stamp": f(bold, 15),
        "stamp_sm": f(reg, 12),
        "note": f(reg, 11),
    }


# ---------------------------------------------------------------- colours
INK = (32, 38, 32)
GREEN = (24, 74, 44)
GREEN_DK = (16, 52, 30)
COVER = (18, 46, 28)
PAPER = (247, 242, 228)
PAPER_EDGE = (226, 216, 192)
LABEL = (96, 104, 90)
SKIN = (216, 178, 140)
SKIN_SH = (198, 158, 120)
HAIR = (52, 38, 26)


# ---------------------------------------------------------------- PIL helpers
def text_c(d, cx, y, s, font, fill=INK):
    d.text((cx, y), s, font=font, fill=fill, anchor="ma")


def wrap(d, s, font, max_w):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_portrait(d, x0, y0, w, h):
    """Dignified front-facing passport portrait, plain background."""
    from PIL import ImageDraw
    cx = x0 + w // 2
    # background
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(201, 212, 214))
    # shoulders / jacket
    d.rounded_rectangle([x0 + 8, y0 + h - 52, x0 + w - 8, y0 + h + 6],
                        radius=18, fill=(38, 62, 52))
    # shirt + collar
    d.polygon([(cx - 16, y0 + h - 50), (cx + 16, y0 + h - 50),
               (cx, y0 + h - 18)], fill=(240, 238, 230))
    # neck
    d.rectangle([cx - 13, y0 + h - 78, cx + 13, y0 + h - 48], fill=SKIN_SH)
    # ears
    d.ellipse([x0 + w // 2 - 40, y0 + 62, x0 + w // 2 - 30, y0 + 82],
              fill=SKIN)
    d.ellipse([x0 + w // 2 + 30, y0 + 62, x0 + w // 2 + 40, y0 + 82],
              fill=SKIN)
    # hair (behind face)
    d.ellipse([cx - 36, y0 + 12, cx + 36, y0 + 78], fill=HAIR)
    # face
    d.ellipse([cx - 32, y0 + 26, cx + 32, y0 + 104], fill=SKIN)
    # hair fringe over the forehead
    d.ellipse([cx - 32, y0 + 24, cx + 32, y0 + 52], fill=HAIR)
    d.polygon([(cx - 32, y0 + 44), (cx - 10, y0 + 30), (cx + 6, y0 + 46),
               (cx + 32, y0 + 40), (cx + 32, y0 + 26), (cx - 32, y0 + 26)],
              fill=HAIR)
    # eyebrows
    d.line([cx - 22, y0 + 58, cx - 8, y0 + 56], fill=HAIR, width=3)
    d.line([cx + 8, y0 + 56, cx + 22, y0 + 58], fill=HAIR, width=3)
    # eyes
    for ex in (cx - 15, cx + 15):
        d.ellipse([ex - 6, y0 + 62, ex + 6, y0 + 70], fill=(255, 255, 255))
        d.ellipse([ex - 3, y0 + 63, ex + 3, y0 + 69], fill=(30, 26, 22))
    # nose
    d.line([cx - 2, y0 + 70, cx - 2, y0 + 86], fill=SKIN_SH, width=2)
    d.line([cx - 3, y0 + 86, cx + 4, y0 + 86], fill=SKIN_SH, width=2)
    # mouth, neutral
    d.line([cx - 9, y0 + 97, cx + 9, y0 + 97], fill=(120, 70, 60), width=2)
    # soft cheek tone
    d.ellipse([cx - 26, y0 + 78, cx - 14, y0 + 88], fill=(214, 160, 128))
    d.ellipse([cx + 14, y0 + 78, cx + 26, y0 + 88], fill=(214, 160, 128))


def draw_stamp(page, box, country, kind, date, place, colour, angle):
    """One ink stamp: drawn on its own layer, rotated, pasted."""
    from PIL import Image, ImageDraw
    w, h = box[2] - box[0], box[3] - box[1]
    layer = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    r = 12
    ld.rounded_rectangle([20, 20, 20 + w, 20 + h], radius=r,
                         outline=colour + (255,), width=3)
    ld.rounded_rectangle([24, 24, 24 + w - 8, 24 + h - 8], radius=r - 2,
                         outline=colour + (255,), width=1)
    fonts = load_fonts()
    text_c(ld, 20 + w // 2, 28, country, fonts["stamp"], colour + (255,))
    text_c(ld, 20 + w // 2, 52, kind, fonts["stamp_sm"], colour + (255,))
    text_c(ld, 20 + w // 2, 72, date, fonts["stamp"], colour + (255,))
    text_c(ld, 20 + w // 2, 94, place, fonts["stamp_sm"], colour + (255,))
    rot = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    page.paste(rot, (box[0] - 20, box[1] - 20), rot)


def draw_spread_pil():
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (W, H), COVER)
    d = ImageDraw.Draw(img)
    fonts = load_fonts()
    # pages
    d.rectangle([24, 20, 500, 1004], fill=PAPER, outline=PAPER_EDGE, width=2)
    d.rectangle([524, 20, 1000, 1004], fill=PAPER, outline=PAPER_EDGE,
                width=2)
    d.line([500, 20, 500, 1004], fill=(120, 100, 70), width=2)
    d.line([524, 20, 524, 1004], fill=(120, 100, 70), width=2)

    # ================= left page: data page =================
    # small mountain emblem
    ex, ey = 262, 40
    d.ellipse([ex - 16, ey - 16, ex + 16, ey + 16], outline=GREEN, width=2)
    d.polygon([(ex - 11, ey + 8), (ex - 3, ey - 8), (ex + 2, ey + 2),
               (ex + 6, ey - 5), (ex + 12, ey + 8)], outline=GREEN, width=2)
    text_c(d, 262, 66, COUNTRY, fonts["head"], GREEN_DK)
    text_c(d, 262, 100, COUNTRY_NATIVE, fonts["sub"], LABEL)
    text_c(d, 262, 122, "PASSPORT  ·  PASAPORTA", fonts["head_small"],
           GREEN_DK)
    d.line([54, 152, 470, 152], fill=GREEN, width=2)

    # portrait frame
    px0, py0, px1, py1 = 60, 170, 210, 340
    d.rounded_rectangle([px0, py0, px1, py1], radius=4,
                        outline=GREEN_DK, width=2)
    draw_portrait(d, px0 + 3, py0 + 3, px1 - px0 - 6, py1 - py0 - 6)

    # data rows beside the portrait
    rows = [("Surname", HOLDER["surname"]), ("Given names", HOLDER["given"]),
            ("Sex", HOLDER["sex"]), ("Date of birth", HOLDER["dob"]),
            ("Place of birth", HOLDER["pob"])]
    y = 176
    for label, val in rows:
        d.text((232, y), label.upper(), font=fonts["label"], fill=LABEL)
        d.text((232, y + 15), val, font=fonts["value"], fill=INK)
        y += 34
    d.line([54, 356, 470, 356], fill=PAPER_EDGE, width=1)

    # lower data, two columns
    left = [("Nationality", HOLDER["nationality"]),
            ("Date of issue", HOLDER["issue"]),
            ("Authority", HOLDER["authority"])]
    right = [("Passport No.", HOLDER["number"]),
             ("Date of expiry", HOLDER["expiry"]),
             ("Languages", "Valdorian · English")]
    y = 372
    for (l1, v1), (l2, v2) in zip(left, right):
        d.text((54, y), l1.upper(), font=fonts["label"], fill=LABEL)
        d.text((54, y + 15), v1, font=fonts["value"], fill=INK)
        d.text((272, y), l2.upper(), font=fonts["label"], fill=LABEL)
        d.text((272, y + 15), v2, font=fonts["value"], fill=INK)
        y += 40
    d.line([54, 500, 470, 500], fill=PAPER_EDGE, width=1)

    # holder's signature
    d.text((54, 516), "HOLDER'S SIGNATURE", font=fonts["label"], fill=LABEL)
    sig = [(60, 550), (74, 544), (88, 552), (100, 540), (112, 550),
           (124, 546), (138, 554), (152, 542), (166, 552), (180, 546),
           (196, 554), (212, 542), (228, 552), (244, 544), (260, 552),
           (276, 546)]
    d.line(sig, fill=INK, width=2, joint="curve")
    d.line([54, 566, 300, 566], fill=LABEL, width=1)

    # machine-readable zone
    d.line([54, 880, 470, 880], fill=GREEN, width=1)
    l1, l2 = mrz_lines()
    d.text((54, 892), l1, font=fonts["mrz"], fill=INK)
    d.text((54, 916), l2, font=fonts["mrz"], fill=INK)
    d.text((54, 946), "This passport is the property of the "
           "Republic of Valdoria.", font=fonts["note"], fill=LABEL)

    # ================= right page: visas =================
    text_c(d, 762, 44, "VISAS", fonts["head"], GREEN_DK)
    text_c(d, 762, 78, "VIZAT", fonts["sub"], LABEL)
    d.line([554, 108, 970, 108], fill=GREEN, width=2)

    angles = [-4, 3, -2, 5]
    boxes = [(560, 130, 760, 250), (776, 130, 964, 250),
             (560, 272, 760, 392), (776, 272, 964, 392)]
    for (country, kind, date, place, colour), box, ang in zip(
            STAMPS, boxes, angles):
        draw_stamp(img, box, country, kind, date, place, colour, ang)

    # visa condition box
    d.rounded_rectangle([554, 420, 970, 540], radius=4, outline=GREEN_DK,
                        width=2)
    d.text((574, 436), "VISA CONDITION", font=fonts["label"], fill=GREEN_DK)
    lines = wrap(d, VISA_TEXT, fonts["value_sm"], 380)
    y = 460
    for ln in lines:
        d.text((574, y), ln, font=fonts["value_sm"], fill=INK)
        y += 20

    # fee stamp
    d.rounded_rectangle([554, 566, 770, 646], radius=4,
                        outline=(178, 58, 46), width=2)
    d.text((574, 582), "FEE PAID", font=fonts["label"], fill=(178, 58, 46))
    d.text((574, 602), "12 VALDA", font=fonts["stamp"], fill=(178, 58, 46))
    d.text((790, 590), "REVENUE", font=fonts["label"], fill=LABEL)
    d.text((790, 608), "12 MAR 2024", font=fonts["value_sm"], fill=INK)

    # entry note, bottom of right page
    d.line([554, 880, 970, 880], fill=GREEN, width=1)
    d.text((554, 892), "Entries above are the holder's travel history "
           "since issue.", font=fonts["note"], fill=LABEL)
    d.text((554, 912), "No stamp predates 12 MAR 2024.",
           font=fonts["note"], fill=LABEL)
    return img


# ---------------------------------------------------------------- stdlib fallback
# 5x7 bitmap font (uppercase, digits, basic punctuation). Used only if
# Pillow is unavailable in the grading sandbox.
_FONT = {
    'A': ("01110","10001","10001","11111","10001","10001","10001"),
    'B': ("11110","10001","10001","11110","10001","10001","11110"),
    'C': ("01110","10001","10000","10000","10000","10001","01110"),
    'D': ("11110","10001","10001","10001","10001","10001","11110"),
    'E': ("11111","10000","10000","11110","10000","10000","11111"),
    'F': ("11111","10000","10000","11110","10000","10000","10000"),
    'G': ("01110","10001","10000","10111","10001","10001","01111"),
    'H': ("10001","10001","10001","11111","10001","10001","10001"),
    'I': ("01110","00100","00100","00100","00100","00100","01110"),
    'J': ("00111","00010","00010","00010","00010","10010","01100"),
    'K': ("10001","10010","10100","11000","10100","10010","10001"),
    'L': ("10000","10000","10000","10000","10000","10000","11111"),
    'M': ("10001","11011","10101","10101","10001","10001","10001"),
    'N': ("10001","11001","10101","10011","10001","10001","10001"),
    'O': ("01110","10001","10001","10001","10001","10001","01110"),
    'P': ("11110","10001","10001","11110","10000","10000","10000"),
    'Q': ("01110","10001","10001","10001","10101","10010","01101"),
    'R': ("11110","10001","10001","11110","10100","10010","10001"),
    'S': ("01111","10000","10000","01110","00001","00001","11110"),
    'T': ("11111","00100","00100","00100","00100","00100","00100"),
    'U': ("10001","10001","10001","10001","10001","10001","01110"),
    'V': ("10001","10001","10001","10001","10001","01010","00100"),
    'W': ("10001","10001","10001","10101","10101","11011","10001"),
    'X': ("10001","10001","01010","00100","01010","10001","10001"),
    'Y': ("10001","10001","01010","00100","00100","00100","00100"),
    'Z': ("11111","00001","00010","00100","01000","10000","11111"),
    '0': ("01110","10001","10011","10101","11001","10001","01110"),
    '1': ("00100","01100","00100","00100","00100","00100","01110"),
    '2': ("01110","10001","00001","00110","01000","10000","11111"),
    '3': ("11111","00010","00100","00010","00001","10001","01110"),
    '4': ("00010","00110","01010","10010","11111","00010","00010"),
    '5': ("11111","10000","11110","00001","00001","10001","01110"),
    '6': ("00110","01000","10000","11110","10001","10001","01110"),
    '7': ("11111","00001","00010","00100","01000","01000","01000"),
    '8': ("01110","10001","10001","01110","10001","10001","01110"),
    '9': ("01110","10001","10001","01111","00001","00010","01100"),
    ' ': ("00000","00000","00000","00000","00000","00000","00000"),
    '.': ("00000","00000","00000","00000","00000","01100","01100"),
    ',': ("00000","00000","00000","00000","01100","00100","01000"),
    '-': ("00000","00000","00000","01110","00000","00000","00000"),
    '/': ("00001","00010","00010","00100","01000","01000","10000"),
    '<': ("00010","00100","01000","10000","01000","00100","00010"),
    '>': ("01000","00100","00010","00001","00010","00100","01000"),
    ':': ("00000","01100","01100","00000","01100","01100","00000"),
    '(': ("00010","00100","01000","01000","01000","00100","00010"),
    ')': ("01000","00100","00010","00010","00010","00100","01000"),
    "'": ("00100","00100","01000","00000","00000","00000","00000"),
}
_TRANS = str.maketrans({"Ë": "E", "—": "-", "·": ".", "ë": "e"})


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(self.h, y1)):
            for x in range(max(0, x0), min(self.w, x1)):
                self.set(x, y, c)

    def frame(self, x0, y0, x1, y1, c, t=2):
        self.rect(x0, y0, x1, y0 + t, c)
        self.rect(x0, y1 - t, x1, y1, c)
        self.rect(x0, y0, x0 + t, y1, c)
        self.rect(x1 - t, y0, x1, y1, c)

    def hline(self, x0, x1, y, c, t=1):
        self.rect(x0, y - t // 2, x1, y + (t + 1) // 2, c)

    def ellipse(self, x0, y0, x1, y1, c):
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
        for y in range(max(0, y0), min(self.h, y1)):
            dy = (y - cy) / ry
            if abs(dy) > 1:
                continue
            dx = rx * (1 - dy * dy) ** 0.5
            for x in range(max(0, int(cx - dx)), min(self.w, int(cx + dx) + 1)):
                self.set(x, y, c)

    def poly(self, pts, c):
        ys = sorted(set(p[1] for p in pts))
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
                if y1 == y2:
                    continue
                if min(y1, y2) <= y < max(y1, y2):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(max(0, int(xs[i])), min(self.w, int(xs[i + 1]) + 1)):
                    self.set(x, y, c)

    def text(self, x, y, s, c, scale=2):
        s = s.translate(_TRANS).upper()
        cx = x
        for ch in s:
            g = _FONT.get(ch, _FONT[' '])
            for r, row in enumerate(g):
                for col, bit in enumerate(row):
                    if bit == '1':
                        self.rect(cx + col * scale, y + r * scale,
                                  cx + (col + 1) * scale,
                                  y + (r + 1) * scale, c)
            cx += 6 * scale

    def text_w(self, s, scale=2):
        return len(s.translate(_TRANS)) * 6 * scale

    def text_c(self, cx, y, s, c, scale=2):
        self.text(cx - self.text_w(s, scale) // 2, y, s, c, scale)


def png_bytes(cv):
    import struct, zlib, binascii
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]

    def chunk(t, data):
        c = struct.pack(">I", len(data)) + t + data
        return c + struct.pack(">I", binascii.crc32(t + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + chunk(b"IEND", b""))


def draw_spread_stdlib():
    cv = Canvas(W, H, COVER)
    cv.rect(24, 20, 500, 1004, PAPER)
    cv.rect(524, 20, 1000, 1004, PAPER)
    # left page
    cv.text_c(262, 48, COUNTRY, GREEN_DK, 2)
    cv.text_c(262, 76, COUNTRY_NATIVE, LABEL, 1)
    cv.text_c(262, 100, "PASSPORT", GREEN_DK, 2)
    cv.hline(54, 470, 132, GREEN, 2)
    # portrait
    cv.frame(60, 150, 210, 320, GREEN_DK, 2)
    cv.rect(63, 153, 207, 317, (201, 212, 214))
    cv.ellipse(95, 250, 175, 317, (38, 62, 52))
    cv.ellipse(108, 168, 162, 252, SKIN)
    cv.ellipse(106, 164, 164, 205, HAIR)
    cv.rect(116, 208, 124, 212, (30, 26, 22))
    cv.rect(146, 208, 154, 212, (30, 26, 22))
    cv.rect(124, 232, 146, 236, (120, 70, 60))
    rows = [("SURNAME", HOLDER["surname"]), ("GIVEN NAMES", HOLDER["given"]),
            ("SEX", HOLDER["sex"]), ("DATE OF BIRTH", HOLDER["dob"]),
            ("PLACE OF BIRTH", HOLDER["pob"])]
    y = 160
    for label, val in rows:
        cv.text(232, y, label, LABEL, 1)
        cv.text(232, y + 10, val, INK, 2)
        y += 32
    cv.hline(54, 470, 340, PAPER_EDGE, 1)
    y = 356
    for label, val in [("NATIONALITY", HOLDER["nationality"]),
                       ("PASSPORT NO.", HOLDER["number"]),
                       ("DATE OF ISSUE", HOLDER["issue"]),
                       ("DATE OF EXPIRY", HOLDER["expiry"]),
                       ("AUTHORITY", HOLDER["authority"])]:
        cv.text(54, y, label, LABEL, 1)
        cv.text(54, y + 10, val, INK, 2)
        y += 34
    l1, l2 = mrz_lines()
    cv.hline(54, 470, 880, GREEN, 1)
    cv.text(54, 892, l1, INK, 1)
    cv.text(54, 910, l2, INK, 1)
    # right page
    cv.text_c(762, 48, "VISAS", GREEN_DK, 2)
    cv.hline(554, 970, 100, GREEN, 2)
    boxes = [(560, 130, 760, 250), (776, 130, 964, 250),
             (560, 272, 760, 392), (776, 272, 964, 392)]
    for (country, kind, date, place, colour), (x0, y0, x1, y1) in zip(
            STAMPS, boxes):
        cv.frame(x0, y0, x1, y1, colour, 2)
        cv.text_c((x0 + x1) // 2, y0 + 14, country, colour, 2)
        cv.text_c((x0 + x1) // 2, y0 + 40, kind, colour, 1)
        cv.text_c((x0 + x1) // 2, y0 + 60, date, colour, 2)
        cv.text_c((x0 + x1) // 2, y0 + 86, place, colour, 1)
    cv.frame(554, 420, 970, 540, GREEN_DK, 2)
    cv.text(574, 436, "VISA CONDITION", GREEN_DK, 1)
    cv.text(574, 460, "VISA - VALID FOR THE THREE", INK, 1)
    cv.text(574, 478, "VALLEYS ONLY. HOLDER MUST", INK, 1)
    cv.text(574, 496, "REGISTER AT KESTREL WITHIN", INK, 1)
    cv.text(574, 514, "7 DAYS OF ENTRY.", INK, 1)
    cv.frame(554, 566, 770, 646, (178, 58, 46), 2)
    cv.text(574, 582, "FEE PAID", (178, 58, 46), 1)
    cv.text(574, 602, "12 VALDA", (178, 58, 46), 2)
    cv.text(790, 590, "REVENUE", LABEL, 1)
    cv.text(790, 608, "12 MAR 2024", INK, 1)
    return png_bytes(cv)


# ---------------------------------------------------------------- main
def main():
    os.makedirs("/output", exist_ok=True)
    try:
        from PIL import Image  # noqa: F401
        img = draw_spread_pil()
        img.save(OUT, format="PNG")
        print("rendered with Pillow")
    except ImportError:
        with open(OUT, "wb") as f:
            f.write(draw_spread_stdlib())
        print("rendered with stdlib fallback (Pillow unavailable)")
    size = os.path.getsize(OUT)
    print(f"wrote {OUT}: {size} bytes")
    assert size <= 1048576, "entry.png exceeds 1 MiB"


if __name__ == "__main__":
    main()
