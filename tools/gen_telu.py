#!/usr/bin/env python3
"""Generator aset + watchface.json untuk TEL-U T-Rex Pro (360x360, UIHH_GT2).

Output ke build/telu/: 0.png background, 1.png AM, 2.png PM,
3-12 digit besar, 13-22 digit kecil, 23-32 digit medium, 33 nodata,
34 persen, 35-41 weekday (TUE..MON), preview.png, watchface.json.

Peta indeks dipakai juga oleh tools/pack_watchface.py.
"""

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 360
CX = CY = 180

TELU_RED = (237, 30, 40)
TELU_MAROON = (182, 37, 42)
GRAY_DARK = (85, 86, 91)
GRAY_LIGHT = (149, 149, 151)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "telu"

FONT_BLACK = "C:/Windows/Fonts/ariblk.ttf"
FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_size(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def draw_tracked(draw, xy, text, fnt, fill, tracking=0):
    """Teks dengan letter-spacing manual. Kembalikan lebar total."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill + (255,))
        w, _ = text_size(draw, ch, fnt)
        x += w + tracking
    return x - xy[0] - tracking


def tracked_width(draw, text, fnt, tracking=0):
    total = 0
    for ch in text:
        w, _ = text_size(draw, ch, fnt)
        total += w + tracking
    return total - tracking


def watch_angle_xy(cx, cy, r, deg):
    """Sudut jam: 0 = atas, searah jarum jam."""
    rad = math.radians(deg)
    return cx + r * math.sin(rad), cy - r * math.cos(rad)


def pil_arc_angles(start_deg, end_deg):
    """Konversi sudut-jam ke sudut PIL (0 = jam 3, searah jarum jam)."""
    return (start_deg + 270) % 360, (end_deg + 270) % 360


# ---------------------------------------------------------------------------
# Ikon vektor sederhana
# ---------------------------------------------------------------------------

def icon_flame(size=22, color=TELU_RED):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    d.polygon([
        (0.50 * s, 0.02 * s), (0.72 * s, 0.30 * s), (0.62 * s, 0.34 * s),
        (0.80 * s, 0.62 * s), (0.50 * s, 0.98 * s), (0.20 * s, 0.62 * s),
        (0.38 * s, 0.34 * s), (0.30 * s, 0.28 * s),
    ], fill=color + (255,))
    d.ellipse([0.38 * s, 0.58 * s, 0.62 * s, 0.86 * s], fill=(0, 0, 0, 255))
    return img


def icon_steps(size=22, color=TELU_RED):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    # dua tapak kaki
    d.ellipse([0.12 * s, 0.30 * s, 0.42 * s, 0.98 * s], fill=color + (255,))
    d.ellipse([0.58 * s, 0.02 * s, 0.88 * s, 0.70 * s], fill=color + (255,))
    for cx, cy, r in [(0.27, 0.16, 0.09), (0.73, 0.84, 0.09)]:
        d.ellipse([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s],
                  fill=color + (255,))
    return img


def icon_heart(size=22, color=TELU_RED):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    d.ellipse([0.06 * s, 0.14 * s, 0.52 * s, 0.60 * s], fill=color + (255,))
    d.ellipse([0.48 * s, 0.14 * s, 0.94 * s, 0.60 * s], fill=color + (255,))
    d.polygon([(0.08 * s, 0.44 * s), (0.92 * s, 0.44 * s),
               (0.50 * s, 0.96 * s)], fill=color + (255,))
    return img


def icon_bolt(size=20, color=TELU_RED):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    d.polygon([(0.58 * s, 0.02 * s), (0.20 * s, 0.58 * s), (0.46 * s, 0.58 * s),
               (0.40 * s, 0.98 * s), (0.80 * s, 0.40 * s), (0.53 * s, 0.40 * s)],
              fill=color + (255,))
    return img


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

def make_background():
    bg = Image.new("RGBA", (W, H), BLACK + (255,))
    d = ImageDraw.Draw(bg)

    # Ring dekoratif tepi (marun + merah, tipis)
    d.ellipse([CX - 176, CY - 176, CX + 176, CY + 176],
              outline=TELU_MAROON + (255,), width=2)
    d.ellipse([CX - 169, CY - 169, CX + 169, CY + 169],
              outline=TELU_RED + (255,), width=1)

    # Tick 12/3/6/9
    for deg in (0, 90, 180, 270):
        x1, y1 = watch_angle_xy(CX, CY, 166, deg)
        x2, y2 = watch_angle_xy(CX, CY, 176, deg)
        d.line([x1, y1, x2, y2], fill=TELU_RED + (255,), width=3)

    # Track arc baterai (bawah, 135 -> 225, r=160)
    a0, a1 = pil_arc_angles(135, 225)
    d.arc([CX - 160, CY - 160, CX + 160, CY + 160],
          start=a0, end=a1, fill=(90, 18, 21, 255), width=7)

    # Divider vertikal halus
    d.line([158, 56, 158, 320], fill=(42, 42, 46, 255), width=1)

    # Kolom kiri: ikon + label + separator
    f_label = font(FONT_BOLD, 19)
    bg.alpha_composite(icon_flame(22), (16, 60))
    d.text((44, 60), "KCAL", font=f_label, fill=GRAY_LIGHT + (255,))
    d.line([16, 132, 130, 132], fill=GRAY_DARK + (255,), width=2)

    bg.alpha_composite(icon_steps(22), (16, 142))
    d.text((44, 142), "STEP", font=f_label, fill=TELU_RED + (255,))
    d.line([16, 214, 130, 214], fill=GRAY_DARK + (255,), width=2)

    bg.alpha_composite(icon_heart(22), (16, 224))
    d.text((44, 224), "HR", font=f_label, fill=TELU_RED + (255,))

    bg.alpha_composite(icon_bolt(20), (16, 28))

    # Branding bawah
    f_brand = font(FONT_BOLD, 15)
    label = "TELKOM UNIVERSITY"
    tw = tracked_width(d, label, f_brand, tracking=3)
    x0 = (W - tw) // 2
    draw_tracked(d, (x0, 330), label, f_brand, WHITE, tracking=3)
    d.line([x0 - 16, 338, x0 - 6, 338], fill=TELU_RED + (255,), width=2)
    d.line([x0 + tw + 6, 338, x0 + tw + 16, 338], fill=TELU_RED + (255,), width=2)

    return bg


# ---------------------------------------------------------------------------
# Badge AM/PM, digit, weekday, persen
# ---------------------------------------------------------------------------

def make_badge(text):
    img = Image.new("RGBA", (46, 28), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, 45, 27], radius=6, fill=TELU_RED + (255,))
    fnt = font(FONT_BOLD, 17)
    w, h = text_size(d, text, fnt)
    d.text(((46 - w) // 2, (28 - h) // 2 - 1), text, font=fnt,
           fill=WHITE + (255,))
    return img


def make_digit(ch, cell_w, cell_h, font_path, font_size, fill=WHITE):
    img = Image.new("RGBA", (cell_w, cell_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fnt = font(font_path, font_size)
    w, h = text_size(d, ch, fnt)
    d.text(((cell_w - w) // 2, (cell_h - h) // 2 - 2), ch, font=fnt,
           fill=fill + (255,))
    return img


def make_text_image(text, font_path, font_size, fill, tracking=0, pad=2):
    tmp = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    fnt = font(font_path, font_size)
    tw = tracked_width(d, text, fnt, tracking)
    _, th = text_size(d, text, fnt)
    img = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_tracked(d, (pad, pad), text, fnt, fill, tracking)
    box = img.getbbox()
    return img.crop(box) if box else img


# ---------------------------------------------------------------------------
# watchface.json (parameter bernama sesuai skema UIHH_GT2)
# ---------------------------------------------------------------------------

# Indeks gambar
I_BG = 0
I_AM = 1
I_PM = 2
I_BIG = 3        # 3..12 digit besar
I_SMALL = 13     # 13..22 digit kecil (nilai)
I_MED = 23       # 23..32 digit medium (baterai %, tanggal)
I_NODATA = 33
I_PCT = 34
I_WEEK = 35      # 35..41 TUE..MON

LANG = 2  # english/default seperti file asli


def img_range(index, count):
    return {"Language": LANG, "ImageRange": {"ImageIndex": index, "ImagesCount": count}}


def positioned_image(x, y, index):
    return {"Coordinates": {"X": x, "Y": y}, "ImageIndex": index}


def number_text_image(x, y, index, count, align="Left", spacing=0, zeropad=0,
                      suffix=None, nodata=None, unknown6=0):
    img = {"X": x, "Y": y, "ImageRange": img_range(index, count)}
    if nodata is not None:
        img["NoDataImageIndex"] = nodata
    if suffix is not None:
        img["SuffixImage"] = suffix
    text = {"Image": img, "Alignment": align, "Spacing": spacing,
            "ZeroPadding": zeropad, "Unknown6": unknown6}
    return text


def build_params(preview_index):
    return {
        "Background": {
            "Preview": img_range(preview_index, 1),
            "ImageIndex": I_BG,
        },
        "Time": {
            "Digital": {
                # Type 0 = jam, 1 = menit (kanan, kanan-rata)
                "HoursMinutesSeconds": [
                    {"Type": 0, "Independent": True,
                     "Text": number_text_image(332, 80, I_BIG, 10, align="Right",
                                              spacing=0, zeropad=1)},
                    {"Type": 1, "Independent": True,
                     "Text": number_text_image(332, 186, I_BIG, 10, align="Right",
                                              spacing=0, zeropad=0)},
                ],
                "AM": {"Coordinates": {"X": 288, "Y": 30},
                       "ImageRange": img_range(I_AM, 1)},
                "PM": {"Coordinates": {"X": 288, "Y": 30},
                       "ImageRange": img_range(I_PM, 1)},
            },
        },
        "System": {
            "Date": {
                # Type 2 = tanggal, Type 1 = bulan (tak dipakai; hari saja)
                "YearMonthDay": [
                    {"Type": 2, "Independent": True,
                     "Text": number_text_image(224, 30, I_MED, 10, align="Left",
                                              spacing=2, zeropad=1)},
                ],
                "Week": {
                    "Independent": True,
                    "Text": number_text_image(180, 32, I_WEEK, 7, align="Left",
                                              spacing=0, zeropad=0,
                                              unknown6=1),
                },
            },
            "Data": [
                {"Type": "Battery",
                 "CircleScale": {
                     "Angle": {"X": 180, "Y": 180, "StartAngle": 135.0,
                               "EndAngle": 225.0, "Radius": 160.0},
                     "Color": "0xFFED1E28", "Width": 7, "Flatness": 180,
                 },
                 "NumberSequence": {
                     "Independent": True,
                     "Text": number_text_image(42, 26, I_MED, 10, align="Left",
                                              spacing=2, zeropad=0,
                                              suffix=img_range(I_PCT, 1)),
                 }},
                {"Type": "Steps",
                 "NumberSequence": {
                     "Independent": True,
                     "Text": number_text_image(16, 168, I_SMALL, 10, align="Left",
                                              spacing=2, zeropad=0,
                                              nodata=I_NODATA),
                 }},
                {"Type": "Calories",
                 "NumberSequence": {
                     "Independent": True,
                     "Text": number_text_image(16, 86, I_SMALL, 10, align="Left",
                                              spacing=2, zeropad=0,
                                              nodata=I_NODATA),
                 }},
                {"Type": "HeartRate",
                 "NumberSequence": {
                     "Independent": True,
                     "Text": number_text_image(16, 250, I_SMALL, 10, align="Left",
                                              spacing=2, zeropad=0,
                                              nodata=I_NODATA),
                 }},
            ],
        },
        "IdleScreen": {
            "Time": {
                "Digital": {
                    "HoursMinutesSeconds": [
                        {"Type": 0, "Independent": True,
                         "Text": number_text_image(180, 96, I_BIG, 10,
                                                  align="Center", spacing=0,
                                                  zeropad=1)},
                        {"Type": 1, "Independent": True,
                         "Text": number_text_image(180, 202, I_BIG, 10,
                                                  align="Center", spacing=0,
                                                  zeropad=0)},
                    ],
                },
            },
            "Date": {
                "Week": {
                    "Independent": True,
                    "Text": number_text_image(180, 312, I_WEEK, 7, align="Center",
                                              spacing=0, zeropad=0,
                                              unknown6=1),
                },
            },
            "Data": [
                {"Type": "Battery",
                 "CircleScale": {
                     "Angle": {"X": 180, "Y": 180, "StartAngle": 135.0,
                               "EndAngle": 225.0, "Radius": 160.0},
                     "Color": "0xFFED1E28", "Width": 7, "Flatness": 180,
                 }},
            ],
            "BackgroundImageIndex": I_BG,
        },
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    make_background().save(OUT / "0.png")
    make_badge("AM").save(OUT / "1.png")
    make_badge("PM").save(OUT / "2.png")

    for d in range(10):
        make_digit(str(d), 76, 100, FONT_BLACK, 86).save(OUT / f"{3 + d}.png")
        make_digit(str(d), 26, 36, FONT_BOLD, 31).save(OUT / f"{13 + d}.png")
        make_digit(str(d), 18, 24, FONT_BOLD, 21).save(OUT / f"{23 + d}.png")

    make_text_image("--", FONT_BOLD, 30, WHITE).save(OUT / "33.png")
    make_text_image("%", FONT_BOLD, 21, WHITE).save(OUT / "34.png")

    for i, day in enumerate(["TUE", "WED", "THU", "FRI", "SAT", "SUN", "MON"]):
        make_text_image(day, FONT_BOLD, 21, TELU_RED, tracking=2).save(
            OUT / f"{35 + i}.png")

    assert I_WEEK == 35
    n_numbered = 42  # 0..41
    preview_index = n_numbered  # preview jadi gambar terakhir

    (OUT / "watchface.json").write_text(
        json.dumps(build_params(preview_index), indent=2))
    print("aset ditulis ke", OUT, "| preview index:", preview_index)


if __name__ == "__main__":
    main()
