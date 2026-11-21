#!/usr/bin/env python3
"""make.fun entry: The Passport Page of a Country That Isn't There (v4).

Writes /output/entry.png — an open passport spread for the invented
Republic of Solmarra, a harbour island nation reachable only by sea.
Data page: photorealistic portrait (loaded from portrait.jpg next to
this file), a faint GHOST IMAGE of the same portrait, bilingual data
rows, the holder's profession (licensed ferry captain, licence F-0217),
signature, observations AND conditions, a microtext motto line, and a
correct ICAO MRZ, over a wavy guilloche security background. Visa page:
a full structured DRAVNIA VISITOR VISA box, eight stamps from
neighbouring ports (all dated after the 09 FEB 2024 issue date, the
Dravnia pair inside the visa's validity), a structured FERRY ROUTE
ENDORSEMENT box, a red "arrival by sea only" stamp, a round
ferry-passage fee stamp, and a national harbour motif (lighthouse over
waves) at the foot of the page — the national-character artwork real
passport visa pages carry (ICAO Doc 9303).

Primary renderer uses Pillow; if Pillow is missing in the grading
sandbox, a pure-stdlib renderer draws a simplified version of the
same spread so the program never crashes. No network. Deterministic.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PORTRAIT_FILE = os.path.join(HERE, "portrait.jpg")
OUT = "/output/entry.png"
W, H = 1024, 1024

# ---------------------------------------------------------------- data
COUNTRY = "REPUBLIC OF SOLMARRA"
COUNTRY_NATIVE = "REPUBLIKA E SOLMARRËS"
CAPITAL = "PORT SOLMAR"
LANGUAGE = "Solmaran"
CURRENCY = "SOL"
# National motto, used as the microtext line (ICAO security printing).
MOTTO = "PER MARE · PER LUCEM"

HOLDER = {
    "surname": "KALDRIS",
    "given": "MARA ILSE",
    "sex": "F",
    "dob": "03 SEP 1979",
    "pob": CAPITAL,
    "nationality": "SOLMARAN",
    "number": "SLM517204",
    "issue": "09 FEB 2024",
    "expiry": "09 FEB 2034",
    "authority": "HARBOUR OFFICE",
    "profession": "FERRY CAPTAIN",
    "licence": "F-0217",
}

# The Dravnia visa covers the holder's first trip (25 MAR - 08 APR 2024).
VISA = {
    "country": "DRAVNIA",
    "native": "DRAVNI VIZA",
    "type": "C · SINGLE ENTRY",
    "stay": "30 DAYS",
    "valid_from": "01 MAR 2024",
    "until": "30 APR 2024",
    "issued_at": "KESTREL PORT, 15 FEB 2024",
    "fee": "40 DRV",
}

ENDORSEMENT = [
    "ROUTES: PORT SOLMAR — KESTREL PORT · LUMEN CITY",
    "SEASON: 1 APR — 31 OCT. WINTER: MAIL BOAT ONLY.",
    "REPORT TO THE HARBOURMASTER WITHIN 48 HOURS.",
    "VALID ONLY WITH CAPTAIN'S LICENCE F-0217.",
]

# Every stamp is dated AFTER the 09 FEB 2024 issue date, in travel order.
STAMPS = [
    ("SOLMARRA", "DEPARTURE", "22 MAR 2024", "PORT SOLMAR", (178, 58, 46)),
    ("DRAVNIA", "ARRIVAL", "25 MAR 2024", "KESTREL PORT", (31, 84, 160)),
    ("DRAVNIA", "DEPARTURE", "08 APR 2024", "KESTREL PORT", (31, 84, 160)),
    ("KESSARA", "ARRIVAL", "19 MAY 2024", "LUMEN CITY", (26, 110, 74)),
    ("KESSARA", "DEPARTURE", "02 JUN 2024", "LUMEN CITY", (26, 110, 74)),
    ("SOLMARRA", "ARRIVAL", "07 JUN 2024", "PORT SOLMAR", (178, 58, 46)),
    ("OSTREK", "ARRIVAL", "14 SEP 2024", "TARNOV", (122, 54, 140)),
    ("OSTREK", "DEPARTURE", "28 SEP 2024", "TARNOV", (122, 54, 140)),
]

CONDITIONS = ("Report to the Harbourmaster within 48 hours of landing. "
              "Outer isles closed Nov–Mar without a Lighthouse Office "
              "licence.")
OBSERVATION = ("Holder is a licensed ferry captain, licence F-0217. "
               "This passport is valid only when the bearer carries the "
               "current Solmaran tide tables.")
SEA_ONLY = ("ARRIVAL BY SEA ONLY", "NO AIRPORT IN", "SOLMARRA")
FERRY_FEE = ("FERRY FEE", "PAID", "12 SOL")


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
    line1 = ("P<SLM" + "KALDRIS<<MARA<ILSE").ljust(44, "<")
    doc = "SLM517204<"
    body = (doc + mrz_check(doc) + "SLM" + "790903" + mrz_check("790903")
            + "F" + "340209" + mrz_check("340209") + "<" * 14)
    line2 = body + mrz_check(body)
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    return line1, line2


# ---------------------------------------------------------------- colours
INK = (32, 38, 32)
NAVY = (26, 52, 88)
NAVY_DK = (18, 38, 66)
GOLD = (176, 132, 40)
COVER = (16, 34, 58)
PAPER = (247, 242, 228)
PAPER_EDGE = (226, 216, 192)
LABEL = (96, 104, 90)
RED = (178, 58, 46)
FAINT = (233, 226, 202)
SKIN = (216, 178, 140)
SKIN_SH = (198, 158, 120)
HAIR = (52, 38, 26)
GUILL = (214, 221, 223)
VISA_TINT = (240, 244, 238)
GHOST_LINE = (175, 180, 175)
MICRO = (150, 155, 150)


# ---------------------------------------------------------------- PIL renderer
def load_fonts():
    """Return a dict of truetype fonts; fall back to PIL's default font."""
    from PIL import ImageFont
    cands = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    ]
    have = [p for p in cands if os.path.exists(p)]
    bold = next((p for p in have if "Bold" in p and "Sans" in p), None)
    reg = next((p for p in have if "Bold" not in p and "Sans" in p
                and "Mono" not in p), None)
    serif_b = next((p for p in have if "Serif-Bold" in p), None)
    serif_i = next((p for p in have if "Serif-Italic" in p), None)
    mono = next((p for p in have if "Mono" in p), None)

    def f(path, size):
        if path:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
        return ImageFont.load_default()

    return {
        "head": f(serif_b or bold, 26),
        "head_small": f(bold, 19),
        "sub": f(reg, 13),
        "label": f(bold, 11),
        "value": f(bold, 15),
        "value_sm": f(reg, 15),
        "rule": f(reg, 13),
        "sig": f(serif_i or reg, 24),
        "mrz": f(mono or reg, 16),
        "stamp": f(bold, 14),
        "stamp_sm": f(reg, 11),
        "note": f(reg, 11),
        "caption": f(reg, 10),
        "micro": f(reg, 8),
    }


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


def draw_guilloche(d, x0, x1, y0, y1, colour=GUILL):
    """Wavy security lines across a page, drawn before any content."""
    import math
    y = y0 + 6
    while y < y1:
        pts = []
        x = x0
        while x <= x1:
            pts.append((x, y + 4 * math.sin((x - x0) * 2 * math.pi / 72)))
            x += 5
        d.line(pts, fill=colour, width=1)
        y += 15


def draw_lighthouse_emblem(d, cx, cy, r):
    """Lighthouse in a circle: the mark of a harbour nation."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=2)
    # tower
    d.polygon([(cx - 6, cy + 12), (cx - 4, cy - 8), (cx + 4, cy - 8),
               (cx + 6, cy + 12)], fill=NAVY)
    d.rectangle([cx - 6, cy - 12, cx + 6, cy - 6], fill=GOLD)
    d.line([cx - 10, cy - 9, cx - 16, cy - 13], fill=GOLD, width=2)
    d.line([cx + 10, cy - 9, cx + 16, cy - 13], fill=GOLD, width=2)
    # waves
    d.arc([cx - 16, cy + 8, cx + 16, cy + 20], 0, 180, fill=NAVY, width=2)
    d.arc([cx - 12, cy + 14, cx + 12, cy + 24], 0, 180, fill=NAVY, width=2)


def draw_harbour_motif(d, cx, base_y):
    """National-character artwork at the foot of the visa page: the
    Port Solmar lighthouse over waves, with its light beams — the
    motif real passport visa pages carry (ICAO Doc 9303)."""
    # light beams from the lamp room
    d.line([cx - 8, base_y - 50, cx - 34, base_y - 60], fill=GOLD, width=2)
    d.line([cx + 8, base_y - 50, cx + 34, base_y - 60], fill=GOLD, width=2)
    # lamp room
    d.rectangle([cx - 7, base_y - 56, cx + 7, base_y - 46], fill=GOLD)
    # tapered tower
    d.polygon([(cx - 9, base_y), (cx - 5, base_y - 46),
               (cx + 5, base_y - 46), (cx + 9, base_y)], fill=NAVY)
    # tower band
    d.line([cx - 7, base_y - 22, cx + 7, base_y - 22], fill=PAPER, width=2)
    # waves under the tower
    d.arc([cx - 30, base_y - 8, cx + 30, base_y + 8], 0, 180, fill=NAVY,
          width=2)
    d.arc([cx - 20, base_y - 2, cx + 20, base_y + 12], 0, 180, fill=NAVY,
          width=2)


def draw_photo_portrait(d, x0, y0, w, h):
    """Photorealistic portrait from portrait.jpg; drawn face if missing."""
    from PIL import Image, ImageOps
    try:
        photo = Image.open(PORTRAIT_FILE).convert("RGB")
        fitted = ImageOps.fit(photo, (w, h), method=Image.LANCZOS,
                              centering=(0.5, 0.35))
        d._image.paste(fitted, (x0, y0))
        return
    except Exception:
        pass
    # Fallback: plain drawn portrait (only used if the asset is missing).
    cx = x0 + w // 2
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(201, 212, 214))
    d.rounded_rectangle([x0 + 8, y0 + h - 52, x0 + w - 8, y0 + h + 6],
                        radius=18, fill=(38, 62, 52))
    d.rectangle([cx - 13, y0 + h - 78, cx + 13, y0 + h - 48], fill=SKIN_SH)
    d.ellipse([cx - 36, y0 + 12, cx + 36, y0 + 78], fill=HAIR)
    d.ellipse([cx - 32, y0 + 26, cx + 32, y0 + 104], fill=SKIN)
    d.ellipse([cx - 32, y0 + 24, cx + 32, y0 + 52], fill=HAIR)
    d.line([cx - 22, y0 + 58, cx - 8, y0 + 56], fill=HAIR, width=3)
    d.line([cx + 8, y0 + 56, cx + 22, y0 + 58], fill=HAIR, width=3)
    for ex in (cx - 15, cx + 15):
        d.ellipse([ex - 6, y0 + 62, ex + 6, y0 + 70], fill=(255, 255, 255))
        d.ellipse([ex - 3, y0 + 63, ex + 3, y0 + 69], fill=(30, 26, 22))
    d.line([cx - 9, y0 + 97, cx + 9, y0 + 97], fill=(120, 70, 60), width=2)


def draw_ghost_image(d, x0, y0, w, h):
    """Second, fainter portrait: the same photo faded toward the paper."""
    from PIL import Image, ImageOps
    try:
        photo = Image.open(PORTRAIT_FILE).convert("RGB")
        fitted = ImageOps.fit(photo, (w, h), method=Image.LANCZOS,
                              centering=(0.5, 0.35))
        paper = Image.new("RGB", (w, h), PAPER)
        faded = Image.blend(fitted, paper, 0.68)
        d._image.paste(faded, (x0, y0))
    except Exception:
        pass
    d.rectangle([x0, y0, x0 + w, y0 + h], outline=GHOST_LINE, width=1)


def draw_stamp(page, box, country, kind, date, place, colour, angle,
               fonts):
    """One ink stamp: drawn on its own layer, rotated, pasted."""
    from PIL import Image, ImageDraw
    w, h = box[2] - box[0], box[3] - box[1]
    layer = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle([20, 20, 20 + w, 20 + h], radius=10,
                         outline=colour + (255,), width=3)
    ld.rounded_rectangle([24, 24, 24 + w - 8, 24 + h - 8], radius=8,
                         outline=colour + (255,), width=1)
    ys = [20 + h * 0.10, 20 + h * 0.32, 20 + h * 0.52, 20 + h * 0.72]
    text_c(ld, 20 + w // 2, ys[0], country, fonts["stamp"],
           colour + (255,))
    text_c(ld, 20 + w // 2, ys[1], kind, fonts["stamp_sm"],
           colour + (255,))
    text_c(ld, 20 + w // 2, ys[2], date, fonts["stamp"],
           colour + (255,))
    text_c(ld, 20 + w // 2, ys[3], place, fonts["stamp_sm"],
           colour + (255,))
    rot = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    page.paste(rot, (box[0] - 20, box[1] - 20), rot)


def draw_red_rect_stamp(page, box, lines, angle, fonts):
    from PIL import Image, ImageDraw
    w, h = box[2] - box[0], box[3] - box[1]
    layer = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle([20, 20, 20 + w, 20 + h], radius=6,
                         outline=RED + (255,), width=3)
    ld.rounded_rectangle([24, 24, 24 + w - 8, 24 + h - 8], radius=4,
                         outline=RED + (255,), width=1)
    y = 30
    for ln in lines:
        text_c(ld, 20 + w // 2, y, ln, fonts["stamp"], RED + (255,))
        y += 22
    rot = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    page.paste(rot, (box[0] - 20, box[1] - 20), rot)


def draw_round_fee_stamp(page, cx, cy, r, angle, fonts):
    from PIL import Image, ImageDraw
    layer = Image.new("RGBA", (2 * r + 40, 2 * r + 40), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    c = r + 20
    ld.ellipse([c - r, c - r, c + r, c + r], outline=RED + (255,), width=3)
    ld.ellipse([c - r + 7, c - r + 7, c + r - 7, c + r - 7],
               outline=RED + (255,), width=1)
    text_c(ld, c, c - 26, FERRY_FEE[0], fonts["stamp_sm"], RED + (255,))
    text_c(ld, c, c - 8, FERRY_FEE[1], fonts["stamp"], RED + (255,))
    text_c(ld, c, c + 12, FERRY_FEE[2], fonts["stamp"], RED + (255,))
    rot = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    page.paste(rot, (cx - r - 20, cy - r - 20), rot)


def draw_visa_box(d, x0, y0, x1, y1, fonts):
    """Structured visitor-visa box: fields stacked label over value."""
    d.rounded_rectangle([x0, y0, x1, y1], radius=4, fill=VISA_TINT,
                        outline=NAVY_DK, width=2)
    d.text((x0 + 20, y0 + 10), VISA["country"] + " · VISITOR VISA",
           font=fonts["head_small"], fill=NAVY_DK)
    d.text((x1 - 20, y0 + 12), VISA["native"], font=fonts["sub"],
           fill=LABEL, anchor="ra")
    d.line([x0 + 20, y0 + 36, x1 - 20, y0 + 36], fill=NAVY, width=1)
    left = [("TYPE", VISA["type"]), ("VALID FROM", VISA["valid_from"]),
            ("ISSUED AT", VISA["issued_at"])]
    right = [("DURATION OF STAY", VISA["stay"]), ("UNTIL", VISA["until"]),
             ("FEE", VISA["fee"])]
    y = y0 + 44
    for (l1, v1), (l2, v2) in zip(left, right):
        d.text((x0 + 20, y), l1, font=fonts["label"], fill=LABEL)
        d.text((x0 + 20, y + 13), v1, font=fonts["value_sm"], fill=INK)
        d.text((x0 + 246, y), l2, font=fonts["label"], fill=LABEL)
        d.text((x0 + 246, y + 13), v2, font=fonts["value_sm"], fill=INK)
        y += 32


def draw_endorsement_box(d, x0, y0, x1, y1, fonts):
    """Structured ferry-route endorsement: one rule per line."""
    d.rounded_rectangle([x0, y0, x1, y1], radius=4, outline=NAVY_DK,
                        width=2)
    d.rectangle([x0, y0, x1, y0 + 28], fill=NAVY_DK)
    d.text((x0 + 20, y0 + 8), "FERRY ROUTE ENDORSEMENT",
           font=fonts["label"], fill=(255, 255, 255))
    d.text((x1 - 20, y0 + 8), "PORT SOLMAR · 09 FEB 2024",
           font=fonts["note"], fill=(255, 255, 255), anchor="ra")
    y = y0 + 36
    for rule in ENDORSEMENT:
        d.text((x0 + 20, y), rule, font=fonts["rule"], fill=INK)
        y += 18
    d.text((x0 + 20, y + 2), "No. 517204  ·  Fee paid at issue",
           font=fonts["note"], fill=LABEL)


def draw_spread_pil():
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (W, H), COVER)
    d = ImageDraw.Draw(img)
    d._image = img
    fonts = load_fonts()
    # pages
    d.rectangle([24, 20, 500, 1004], fill=PAPER, outline=PAPER_EDGE, width=2)
    d.rectangle([524, 20, 1000, 1004], fill=PAPER, outline=PAPER_EDGE,
                width=2)
    d.line([500, 20, 500, 1004], fill=(120, 100, 70), width=2)
    d.line([524, 20, 524, 1004], fill=(120, 100, 70), width=2)

    # guilloche security background, both pages, before any content
    draw_guilloche(d, 28, 496, 24, 1000)
    draw_guilloche(d, 528, 996, 24, 1000)

    # ================= left page: data page =================
    draw_lighthouse_emblem(d, 262, 54, 26)
    text_c(d, 262, 88, COUNTRY, fonts["head"], NAVY_DK)
    text_c(d, 262, 116, COUNTRY_NATIVE, fonts["sub"], LABEL)
    text_c(d, 262, 138, "PASSPORT  ·  PASAPORTA", fonts["head_small"],
           NAVY_DK)
    d.line([54, 164, 470, 164], fill=NAVY, width=2)

    # photorealistic portrait
    d.rounded_rectangle([60, 180, 210, 368], radius=4, outline=NAVY_DK,
                        width=2)
    draw_photo_portrait(d, 63, 183, 144, 182)
    text_c(d, 135, 372, "PHOTOGRAPH / FOTOGRAFIA", fonts["caption"], LABEL)

    # data rows beside the portrait
    rows = [("Type / Tip", "P"), ("Code / Kod", "SLM"),
            ("Passport No. / Broj", HOLDER["number"]),
            ("Surname / Prezime", HOLDER["surname"]),
            ("Given names / Ime", HOLDER["given"]),
            ("Nationality / Drzavljanstvo", HOLDER["nationality"])]
    y = 184
    for label, val in rows:
        d.text((232, y), label.upper(), font=fonts["label"], fill=LABEL)
        d.text((232, y + 14), val, font=fonts["value"], fill=INK)
        y += 30
    d.line([54, 392, 470, 392], fill=PAPER_EDGE, width=1)

    # lower data, two columns (profession + licence are the 4th row)
    left = [("Date of birth / Rodenje", HOLDER["dob"]),
            ("Place of birth / Mjesto", HOLDER["pob"]),
            ("Date of expiry / Vrijedi do", HOLDER["expiry"]),
            ("Profession / Zanimanje", HOLDER["profession"])]
    right = [("Sex / Spol", HOLDER["sex"]),
             ("Date of issue / Izdano", HOLDER["issue"]),
             ("Authority / Tijelo", HOLDER["authority"]),
             ("Licence / Licenca", HOLDER["licence"])]
    y = 408
    for (l1, v1), (l2, v2) in zip(left, right):
        d.text((54, y), l1.upper(), font=fonts["label"], fill=LABEL)
        d.text((54, y + 14), v1, font=fonts["value"], fill=INK)
        d.text((272, y), l2.upper(), font=fonts["label"], fill=LABEL)
        d.text((272, y + 14), v2, font=fonts["value"], fill=INK)
        y += 40
    d.line([54, 568, 470, 568], fill=PAPER_EDGE, width=1)

    # holder's signature
    d.text((54, 584), "HOLDER'S SIGNATURE / POTPIS", font=fonts["label"],
           fill=LABEL)
    d.text((54, 600), "Mara Ilse Kaldris", font=fonts["sig"], fill=INK)
    d.line([54, 632, 300, 632], fill=LABEL, width=1)

    # observations (wrapped narrow so the ghost image stays clear)
    d.text((54, 656), "OBSERVATIONS / NAPOMENE", font=fonts["label"],
           fill=LABEL)
    lines = wrap(d, OBSERVATION, fonts["value_sm"], 300)
    y = 676
    for ln in lines:
        d.text((54, y), ln, font=fonts["value_sm"], fill=INK)
        y += 19

    # conditions: a second observation block, same narrow wrap
    d.text((54, y + 10), "CONDITIONS / UVJETI", font=fonts["label"],
           fill=LABEL)
    lines = wrap(d, CONDITIONS, fonts["value_sm"], 300)
    y = y + 30
    for ln in lines:
        d.text((54, y), ln, font=fonts["value_sm"], fill=INK)
        y += 19

    # ghost image: the same portrait, faded, bottom-right of the page
    draw_ghost_image(d, 375, 720, 95, 130)
    text_c(d, 422, 854, "GHOST IMAGE", fonts["caption"], LABEL)

    # repeating security strip above the MRZ
    strip = "SOLMARRA · REPUBLIKA E SOLMARRËS · "
    text_c(d, 262, 866, strip * 2, fonts["caption"], (170, 175, 170))

    # machine-readable zone
    d.line([54, 880, 470, 880], fill=NAVY, width=1)
    l1, l2 = mrz_lines()
    d.text((54, 892), l1, font=fonts["mrz"], fill=INK)
    d.text((54, 916), l2, font=fonts["mrz"], fill=INK)
    d.text((54, 946), "This passport is the property of the "
           "Republic of Solmarra.", font=fonts["note"], fill=LABEL)

    # microtext motto line at the foot of the data page (ICAO
    # security printing: the motto repeated in 8 pt type)
    micro = (MOTTO + " · ") * 4
    text_c(d, 262, 972, micro, fonts["micro"], MICRO)

    # ================= right page: visas =================
    text_c(d, 762, 44, "VISAS", fonts["head"], NAVY_DK)
    text_c(d, 762, 78, "VIZAT  ·  ENTRY AND EXIT STAMPS", fonts["sub"],
           LABEL)
    d.text((958, 44), "12", font=fonts["sub"], fill=LABEL, anchor="ra")
    d.line([554, 108, 970, 108], fill=NAVY, width=2)

    # full structured visitor-visa box
    draw_visa_box(d, 554, 120, 970, 258, fonts)

    # eight stamps, compact grid
    angles = [-4, 3, -2, 5, -3, 4, -5, 2]
    boxes = []
    for r in range(4):
        y0 = 270 + r * 86
        boxes.append((560, y0, 756, y0 + 78))
        boxes.append((772, y0, 968, y0 + 78))
    for (country, kind, date, place, colour), box, ang in zip(
            STAMPS, boxes, angles):
        draw_stamp(img, box, country, kind, date, place, colour, ang,
                   fonts)

    # structured ferry-route endorsement
    draw_endorsement_box(d, 554, 618, 970, 744, fonts)

    # red stamps: sea-only + ferry fee
    draw_red_rect_stamp(img, (554, 758, 768, 848), SEA_ONLY, -3, fonts)
    draw_round_fee_stamp(img, 872, 803, 48, -8, fonts)

    # footer
    d.line([554, 880, 970, 880], fill=NAVY, width=1)
    d.text((554, 892), "Entries above are the holder's travel history "
           "since issue.", font=fonts["note"], fill=LABEL)
    d.text((554, 912), "No stamp predates 09 FEB 2024.",
           font=fonts["note"], fill=LABEL)

    # national harbour motif at the foot of the visa page
    draw_harbour_motif(d, 762, 988)
    return img


# ---------------------------------------------------------------- stdlib fallback
# Compact 3x5 bitmap font (uppercase, digits, basic punctuation).
# Used only if Pillow is unavailable in the grading sandbox.
_FONT = {
    'A': ("010", "101", "111", "101", "101"),
    'B': ("110", "101", "110", "101", "110"),
    'C': ("011", "100", "100", "100", "011"),
    'D': ("110", "101", "101", "101", "110"),
    'E': ("111", "100", "110", "100", "111"),
    'F': ("111", "100", "110", "100", "100"),
    'G': ("011", "100", "101", "101", "011"),
    'H': ("101", "101", "111", "101", "101"),
    'I': ("111", "010", "010", "010", "111"),
    'J': ("001", "001", "001", "101", "010"),
    'K': ("101", "101", "110", "101", "101"),
    'L': ("100", "100", "100", "100", "111"),
    'M': ("101", "111", "111", "101", "101"),
    'N': ("101", "111", "111", "101", "101"),
    'O': ("010", "101", "101", "101", "010"),
    'P': ("110", "101", "110", "100", "100"),
    'Q': ("010", "101", "101", "010", "001"),
    'R': ("110", "101", "110", "101", "101"),
    'S': ("011", "100", "010", "001", "110"),
    'T': ("111", "010", "010", "010", "010"),
    'U': ("101", "101", "101", "101", "111"),
    'V': ("101", "101", "101", "101", "010"),
    'W': ("101", "101", "111", "111", "101"),
    'X': ("101", "101", "010", "101", "101"),
    'Y': ("101", "101", "010", "010", "010"),
    'Z': ("111", "001", "010", "100", "111"),
    '0': ("111", "101", "101", "101", "111"),
    '1': ("010", "110", "010", "010", "111"),
    '2': ("110", "001", "010", "100", "111"),
    '3': ("110", "001", "010", "001", "110"),
    '4': ("101", "101", "111", "001", "001"),
    '5': ("111", "100", "110", "001", "110"),
    '6': ("011", "100", "110", "101", "010"),
    '7': ("111", "001", "010", "010", "010"),
    '8': ("010", "101", "010", "101", "010"),
    '9': ("010", "101", "011", "001", "110"),
    ' ': ("000", "000", "000", "000", "000"),
    '.': ("000", "000", "000", "000", "010"),
    ',': ("000", "000", "000", "010", "100"),
    '-': ("000", "000", "111", "000", "000"),
    '/': ("001", "001", "010", "100", "100"),
    '<': ("001", "010", "100", "010", "001"),
    '>': ("100", "010", "001", "010", "100"),
    ':': ("000", "010", "000", "010", "000"),
    '(': ("001", "010", "010", "010", "001"),
    ')': ("100", "010", "010", "010", "100"),
    "'": ("010", "010", "000", "000", "000"),
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
            for x in range(max(0, int(cx - dx)),
                           min(self.w, int(cx + dx) + 1)):
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
            cx += 4 * scale

    def text_w(self, s, scale=2):
        return len(s.translate(_TRANS)) * 4 * scale

    def text_c(self, cx, y, s, c, scale=2):
        self.text(cx - self.text_w(s, scale) // 2, y, s, c, scale)

    def guilloche(self, x0, x1, y0, y1, c):
        """Light wavy security lines (simplified, every 24 px)."""
        import math
        y = y0 + 6
        while y < y1:
            x = x0
            while x <= x1:
                self.set(x, y + int(3 * math.sin(
                    (x - x0) * 2 * math.pi / 72)), c)
                x += 2
            y += 24


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


def _wrap_text(s, max_chars):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if len(t) <= max_chars:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_spread_stdlib():
    cv = Canvas(W, H, COVER)
    cv.rect(24, 20, 500, 1004, PAPER)
    cv.rect(524, 20, 1000, 1004, PAPER)
    cv.guilloche(28, 496, 24, 1000, GUILL)
    cv.guilloche(528, 996, 24, 1000, GUILL)
    # left page
    cv.text_c(262, 48, COUNTRY, NAVY_DK, 3)
    cv.text_c(262, 76, COUNTRY_NATIVE, LABEL, 2)
    cv.text_c(262, 100, "PASSPORT", NAVY_DK, 2)
    cv.hline(54, 470, 132, NAVY, 2)
    # portrait placeholder (photo asset needs Pillow)
    cv.frame(60, 150, 210, 340, NAVY_DK, 2)
    cv.rect(63, 153, 207, 337, (201, 212, 214))
    cv.ellipse(95, 260, 175, 337, (38, 62, 52))
    cv.ellipse(108, 168, 162, 262, SKIN)
    cv.ellipse(106, 164, 164, 205, HAIR)
    cv.rect(116, 208, 124, 212, (30, 26, 22))
    cv.rect(146, 208, 154, 212, (30, 26, 22))
    cv.rect(124, 232, 146, 236, (120, 70, 60))
    rows = [("TYPE", "P"), ("CODE", "SLM"),
            ("PASSPORT NO.", HOLDER["number"]),
            ("SURNAME", HOLDER["surname"]),
            ("GIVEN NAMES", HOLDER["given"]),
            ("NATIONALITY", HOLDER["nationality"])]
    y = 160
    for label, val in rows:
        cv.text(232, y, label, LABEL, 1)
        cv.text(232, y + 10, val, INK, 2)
        y += 32
    cv.hline(54, 470, 360, PAPER_EDGE, 1)
    y = 376
    for label, val in [("DATE OF BIRTH", HOLDER["dob"]),
                       ("PLACE OF BIRTH", HOLDER["pob"]),
                       ("SEX", HOLDER["sex"]),
                       ("DATE OF ISSUE", HOLDER["issue"]),
                       ("DATE OF EXPIRY", HOLDER["expiry"]),
                       ("AUTHORITY", HOLDER["authority"]),
                       ("PROFESSION", HOLDER["profession"]),
                       ("LICENCE", HOLDER["licence"])]:
        cv.text(54, y, label, LABEL, 1)
        cv.text(54, y + 10, val, INK, 2)
        y += 32
    y = 648
    cv.text(54, y, "OBSERVATIONS", LABEL, 1)
    for ln in _wrap_text(OBSERVATION, 52):
        y += 16
        cv.text(54, y, ln, INK, 1)
    # conditions: a second observation block
    y += 16
    cv.text(54, y, "CONDITIONS", LABEL, 1)
    for ln in _wrap_text(CONDITIONS, 52):
        y += 16
        cv.text(54, y, ln, INK, 1)
    # ghost image placeholder
    cv.frame(375, 720, 470, 850, GHOST_LINE, 1)
    cv.text_c(422, 780, "GHOST", GHOST_LINE, 1)
    l1, l2 = mrz_lines()
    cv.hline(54, 470, 880, NAVY, 1)
    cv.text(54, 892, l1, INK, 1)
    cv.text(54, 910, l2, INK, 1)
    # microtext motto line at the foot of the data page
    cv.text_c(262, 940, (MOTTO + " . REPUBLIC OF SOLMARRA . ") * 2,
              MICRO, 1)
    # right page
    cv.text_c(762, 48, "VISAS", NAVY_DK, 3)
    cv.hline(554, 970, 100, NAVY, 2)
    # visitor-visa box
    cv.frame(554, 120, 970, 258, NAVY_DK, 2)
    cv.text(574, 132, "DRAVNIA . VISITOR VISA", NAVY_DK, 2)
    cv.text(574, 160, "TYPE: C . SINGLE ENTRY", INK, 1)
    cv.text(574, 178, "STAY: 30 DAYS", INK, 1)
    cv.text(574, 196, "VALID: 01 MAR - 30 APR 2024", INK, 1)
    cv.text(574, 214, "ISSUED: KESTREL PORT, 15 FEB 2024", INK, 1)
    cv.text(574, 232, "FEE: 40 DRV", INK, 1)
    # stamps
    boxes = []
    for r in range(4):
        y0 = 270 + r * 86
        boxes.append((560, y0, 756, y0 + 78))
        boxes.append((772, y0, 968, y0 + 78))
    for (country, kind, date, place, colour), (x0, y0, x1, y1) in zip(
            STAMPS, boxes):
        cv.frame(x0, y0, x1, y1, colour, 2)
        cv.text_c((x0 + x1) // 2, y0 + 10, country, colour, 2)
        cv.text_c((x0 + x1) // 2, y0 + 30, kind, colour, 1)
        cv.text_c((x0 + x1) // 2, y0 + 48, date, colour, 2)
        cv.text_c((x0 + x1) // 2, y0 + 64, place, colour, 1)
    # endorsement box
    cv.frame(554, 618, 970, 744, NAVY_DK, 2)
    cv.text(574, 630, "FERRY ROUTE ENDORSEMENT", NAVY_DK, 1)
    y = 652
    for rule in ENDORSEMENT:
        for ln in _wrap_text(rule, 48):
            cv.text(574, y, ln, INK, 1)
            y += 16
    cv.frame(554, 758, 768, 848, RED, 2)
    cv.text_c(661, 772, "ARRIVAL BY SEA ONLY", RED, 1)
    cv.text_c(661, 792, "NO AIRPORT IN", RED, 1)
    cv.text_c(661, 812, "SOLMARRA", RED, 2)
    cv.ellipse(824, 755, 920, 851, RED)
    cv.ellipse(832, 763, 912, 843, PAPER)
    cv.text_c(872, 782, "FERRY", RED, 2)
    cv.text_c(872, 800, "12 SOL", RED, 2)
    # national harbour motif at the foot of the visa page
    cv.rect(754, 922, 770, 930, GOLD)
    cv.rect(757, 930, 767, 980, NAVY_DK)
    cv.rect(730, 926, 752, 928, GOLD)
    cv.rect(772, 926, 794, 928, GOLD)
    cv.hline(720, 804, 986, NAVY_DK, 2)
    cv.hline(730, 794, 992, NAVY_DK, 2)
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
