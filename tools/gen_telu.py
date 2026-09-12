#!/usr/bin/env python3
"""Generator aset + watchface.json untuk TEL-U T-Rex Pro (360x360, UIHH_GT2).

Arah desain "MIDNIGHT BLAZE": tipografi memimpin (Anton condensed italic +
Rajdhani), hitam dominan + merah Tel-U tajam, monogram T angular raksasa
sebagai potongan identitas, slash diagonal, chip data, glow terkendali.

ROUND-SAFE: semua konten teks/ikon/badge wajib di dalam lingkaran aman
r=175 (layar fisik bulat; sudut kotak 360x360 terpotong bezel).

Output ke build/telu/: 0.png background, 1.png AM, 2.png PM,
3-12 digit besar, 13-22 digit kecil, 23-32 digit medium, 33 nodata,
34 persen, 35-41 weekday (TUE..MON), preview.png, watchface.json.
"""

import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 360
CX = CY = 180
SAFE_R = 175

TELU_RED = (237, 30, 40)
TELU_MAROON = (182, 37, 42)
TELU_DARK = (122, 16, 21)
TELU_DEEP = (58, 8, 11)
GRAY_DARK = (85, 86, 91)
GRAY_LIGHT = (149, 149, 151)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CHIP_BG = (16, 16, 20)
CHIP_EDGE = (48, 48, 54)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "telu"
FONTS = ROOT / "assets" / "fonts"

FONT_DISPLAY = str(FONTS / "Anton-Regular.ttf")
FONT_BOLD = str(FONTS / "Rajdhani-Bold.ttf")
FONT_SEMI = str(FONTS / "Rajdhani-SemiBold.ttf")
FONT_MED = str(FONTS / "Rajdhani-Medium.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def text_size(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def draw_tracked(draw, xy, text, fnt, fill, tracking=0):
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


def assert_circle(name, x, y, w, h, r=SAFE_R):
    for px, py in ((x, y), (x + w, y), (x, y + h), (x + w, y + h)):
        dist = math.hypot(px - CX, py - CY)
        assert dist <= r, "%s keluar lingkaran: (%d,%d) dist=%.1f" % (name, px, py, dist)


def watch_angle_xy(cx, cy, r, deg):
    rad = math.radians(deg)
    return cx + r * math.sin(rad), cy - r * math.cos(rad)


def pil_arc_angles(start_deg, end_deg):
    return (start_deg + 270) % 360, (end_deg + 270) % 360


def shear(img, factor=0.16):
    """Miringkan (italic) gambar: geser x sebanding y."""
    w, h = img.size
    shift = int(abs(factor) * h) + 4
    out = Image.new("RGBA", (w + shift * 2, h), (0, 0, 0, 0))
    out.alpha_composite(img, (shift, 0))
    return out.transform(out.size, Image.AFFINE, (1, factor, -factor * h, 0, 1, 0),
                         resample=Image.BICUBIC)


def vgradient(size, top, bottom):
    w, h = size
    base = Image.new("RGB", (1, h))
    px = base.load()
    for y in range(h):
        t = y / max(1, h - 1)
        px[0, y] = tuple(int(a + (b - a) * t) for a, b in zip(top, bottom))
    return base.resize(size)


def make_background():
    bg = Image.new("RGBA", (W, H), BLACK + (255,))
    d = ImageDraw.Draw(bg)

    # Tekstur karbon halus (noise redup)
    rnd = random.Random(7)
    for _ in range(2600):
        x, y = rnd.randrange(W), rnd.randrange(H)
        if math.hypot(x - CX, y - CY) < 178:
            v = rnd.randrange(6, 15)
            d.point((x, y), fill=(v, v, v + 2, 255))

    # Blaze diagonal kiri (marun gelap, energi)
    blaze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    db = ImageDraw.Draw(blaze)
    db.polygon([(0, 96), (168, 28), (214, 74), (46, 142), (0, 130)],
               fill=TELU_MAROON + (255,))
    db.polygon([(0, 150), (52, 130), (66, 152), (0, 172)], fill=TELU_RED + (255,))
    # gradasi vertikal halus pada blaze agar tidak flat
    grad = vgradient((W, H), (255, 255, 255), (110, 110, 110))
    blaze.putalpha(grad.split()[0].point(lambda v: int(v * 0.55)))
    bg.alpha_composite(blaze)

    # Monogram T angular raksasa (potongan identitas), bleed kiri
    t_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dt = ImageDraw.Draw(t_layer)
    # palang atas miring + kaki miring + potongan diagonal
    dt.polygon([(28, 150), (196, 118), (204, 148), (36, 180)], fill=TELU_DARK + (255,))
    dt.polygon([(96, 168), (140, 160), (96, 330), (52, 330)], fill=TELU_DARK + (255,))
    dt.polygon([(150, 128), (170, 124), (104, 320), (84, 320)], fill=TELU_DEEP + (255,))
    # highlight tepi merah terang (sisi kanan palang)
    dt.line([196, 118, 204, 148], fill=TELU_RED + (255,), width=3)
    dt.line([140, 160, 96, 330], fill=TELU_RED + (255,), width=2)
    # glow merah terkendali di sekitar T
    glow = t_layer.filter(__import__("PIL.ImageFilter", fromlist=["x"]).GaussianBlur(14))
    glow = Image.eval(glow, lambda v: v // 4)
    bg.alpha_composite(glow)
    bg.alpha_composite(t_layer)

    # Ring teknologi + tick
    d = ImageDraw.Draw(bg)
    d.ellipse([CX - 176, CY - 176, CX + 176, CY + 176],
              outline=(120, 24, 28, 255), width=2)
    d.ellipse([CX - 169, CY - 169, CX + 169, CY + 169],
              outline=TELU_RED + (255,), width=1)
    for deg in (0, 90, 180, 270):
        x1, y1 = watch_angle_xy(CX, CY, 160, deg)
        x2, y2 = watch_angle_xy(CX, CY, 176, deg)
        d.line([x1, y1, x2, y2], fill=TELU_RED + (255,), width=4)

    # Track arc baterai bawah
    a0, a1 = pil_arc_angles(155, 205)
    d.arc([CX - 172, CY - 172, CX + 172, CY + 172],
          start=a0, end=a1, fill=(90, 18, 21, 255), width=8)

    # Chip data kiri (statis; angka dinamis digambar jam di atasnya)
    for y in (92, 158, 222):
        d.rounded_rectangle([40, y, 172, y + 62], radius=9, fill=CHIP_BG + (255,),
                            outline=CHIP_EDGE + (255,), width=1)
        d.rectangle([40, y + 12, 45, y + 50], fill=TELU_RED + (255,))
    f_label = font(FONT_SEMI, 17)
    d.text((58, 96), "KCAL", font=f_label, fill=GRAY_LIGHT + (255,))
    d.text((58, 162), "STEPS", font=f_label, fill=TELU_RED + (255,))
    d.text((58, 226), "PULSE", font=f_label, fill=TELU_RED + (255,))
    assert_circle("label kcal", 58, 96, 60, 18)
    assert_circle("label steps", 58, 162, 66, 18)
    assert_circle("label pulse", 58, 226, 70, 18)

    # Ikon kecil di dalam chip (putih agar pop)
    bg.alpha_composite(icon_flame(16, WHITE), (150, 98))
    bg.alpha_composite(icon_steps(16, WHITE), (150, 164))
    bg.alpha_composite(icon_heart(16, WHITE), (150, 230))

    # Lockup branding: kotak T merah + teks
    f_brand = font(FONT_SEMI, 13)
    label = "TELKOM UNIVERSITY"
    tw = tracked_width(d, label, f_brand, tracking=2)
    box = 22
    total = box + 6 + tw
    x0 = (W - total) // 2
    assert_circle("branding", x0, 310, total, box)
    d.rounded_rectangle([x0, 310, x0 + box, 310 + box], radius=5,
                        fill=TELU_RED + (255,))
    f_t = font(FONT_BOLD, 18)
    w, h = text_size(d, "T", f_t)
    d.text((x0 + (box - w) // 2, 310 + (box - h) // 2 - 1), "T", font=f_t,
           fill=WHITE + (255,))
    draw_tracked(d, (x0 + box + 6, 314), label, f_brand, WHITE, tracking=2)

    return bg


def icon_flame(size=16, color=WHITE):
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


def icon_steps(size=16, color=WHITE):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    d.ellipse([0.12 * s, 0.30 * s, 0.42 * s, 0.98 * s], fill=color + (255,))
    d.ellipse([0.58 * s, 0.02 * s, 0.88 * s, 0.70 * s], fill=color + (255,))
    for cx, cy, r in [(0.27, 0.16, 0.09), (0.73, 0.84, 0.09)]:
        d.ellipse([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s],
                  fill=color + (255,))
    return img


def icon_heart(size=16, color=WHITE):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    d.ellipse([0.06 * s, 0.14 * s, 0.52 * s, 0.60 * s], fill=color + (255,))
    d.ellipse([0.48 * s, 0.14 * s, 0.94 * s, 0.60 * s], fill=color + (255,))
    d.polygon([(0.08 * s, 0.44 * s), (0.92 * s, 0.44 * s),
               (0.50 * s, 0.96 * s)], fill=color + (255,))
    return img


def make_badge(text):
    """Badge angular (jajaran genjang) merah."""
    img = Image.new("RGBA", (40, 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(8, 0), (40, 0), (32, 24), (0, 24)], fill=TELU_RED + (255,))
    d.polygon([(8, 0), (40, 0), (32, 24), (0, 24)], outline=WHITE + (255,))
    fnt = font(FONT_BOLD, 15)
    w, h = text_size(d, text, fnt)
    d.text(((40 - w) // 2 + 1, (24 - h) // 2 - 1), text, font=fnt,
           fill=WHITE + (255,))
    return img


def make_digit(ch, cell_w, cell_h, font_path, font_size, fill=WHITE,
               shadow=None, italic=0.0):
    img = Image.new("RGBA", (cell_w * 2, cell_h * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fnt = font(font_path, font_size * 2)
    w, h = text_size(d, ch, fnt)
    x = (cell_w * 2 - w) // 2
    y = (cell_h * 2 - h) // 2 - 4
    if shadow:
        d.text((x + 6, y + 6), ch, font=fnt, fill=shadow + (255,))
    d.text((x, y), ch, font=fnt, fill=fill + (255,))
    img = img.resize((cell_w, cell_h), Image.LANCZOS)
    if italic:
        img = shear(img, italic)
        # pangkas tengah agar ukuran sel tetap
        x0 = (img.width - cell_w) // 2
        img = img.crop((x0, 0, x0 + cell_w, cell_h))
    return img


def make_text_image(text, font_path, font_size, fill, tracking=0, pad=2,
                    shadow=None, italic=0.0):
    scale = 2
    tmp = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    fnt = font(font_path, font_size * scale)
    tw = tracked_width(d, text, fnt, tracking * scale)
    _, th = text_size(d, text, fnt)
    img = Image.new("RGBA", (tw + pad * 2 * scale, th + pad * 2 * scale), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if shadow:
        draw_tracked(d, (pad * scale + 4, pad * scale + 4), text, fnt, shadow,
                     tracking * scale)
    draw_tracked(d, (pad * scale, pad * scale), text, fnt, fill, tracking * scale)
    img = img.resize((img.width // scale, img.height // scale), Image.LANCZOS)
    if italic:
        img = shear(img, italic)
    box = img.getbbox()
    return img.crop(box) if box else img


I_BG = 0
I_AM = 1
I_PM = 2
I_BIG = 3        # 3..12 digit besar Anton italic + bayangan
I_SMALL = 13     # 13..22 digit Rajdhani Bold (nilai)
I_MED = 23       # 23..32 digit Rajdhani (baterai %, tanggal)
I_NODATA = 33
I_PCT = 34
I_WEEK = 35      # 35..41 TUE..MON

LANG = 2
SHADOW = (110, 18, 22)


def img_range(index, count):
    return {"Language": LANG, "ImageRange": {"ImageIndex": index, "ImagesCount": count}}


def number_text_image(x, y, index, count, align="Left", spacing=0, zeropad=0,
                      suffix=None, nodata=None, unknown6=0):
    img = {"X": x, "Y": y, "ImageRange": img_range(index, count)}
    if nodata is not None:
        img["NoDataImageIndex"] = nodata
    if suffix is not None:
        img["SuffixImage"] = suffix
    return {"Image": img, "Alignment": align, "Spacing": spacing,
            "ZeroPadding": zeropad, "Unknown6": unknown6}


def build_params(preview_index):
    return {
        "Background": {
            "Preview": img_range(preview_index, 1),
            "ImageIndex": I_BG,
        },
        "Time": {
            "Digital": {
                "HoursMinutesSeconds": [
                    {"Type": 0, "Independent": True,
                     "Text": number_text_image(314, 74, I_BIG, 10, align="Right",
                                              spacing=0, zeropad=1)},
                    {"Type": 1, "Independent": True,
                     "Text": number_text_image(314, 180, I_BIG, 10, align="Right",
                                              spacing=0, zeropad=0)},
                ],
                "AM": {"Coordinates": {"X": 80, "Y": 44},
                       "ImageRange": img_range(I_AM, 1)},
                "PM": {"Coordinates": {"X": 80, "Y": 44},
                       "ImageRange": img_range(I_PM, 1)},
            },
        },
        "System": {
            "Date": {
                "YearMonthDay": [
                    {"Type": 2, "Independent": True,
                     "Text": number_text_image(218, 36, I_MED, 10, align="Left",
                                              spacing=2, zeropad=1)},
                ],
                "Week": {
                    "Independent": True,
                    "Text": number_text_image(162, 38, I_WEEK, 7, align="Left",
                                              spacing=0, zeropad=0,
                                              unknown6=1),
                },
            },
            "Data": [
                {"Type": "Battery",
                 "CircleScale": {
                     "Angle": {"X": 180, "Y": 180, "StartAngle": 155.0,
                               "EndAngle": 205.0, "Radius": 172.0},
                     "Color": "0xFFED1E28", "Width": 8, "Flatness": 180,
                 },
                 "NumberSequence": {
                     "Independent": True,
                     "Text": number_text_image(283, 286, I_MED, 10, align="Right",
                                              spacing=2, zeropad=0,
                                              suffix=img_range(I_PCT, 1)),
                 }},
                {"Type": "Steps",
                 "NumberSequence": {
                     "Independent": True,
                     "Text": number_text_image(58, 184, I_SMALL, 10, align="Left",
                                              spacing=1, zeropad=0,
                                              nodata=I_NODATA),
                 }},
                {"Type": "Calories",
                 "NumberSequence": {
                     "Independent": True,
                     "Text": number_text_image(58, 118, I_SMALL, 10, align="Left",
                                              spacing=1, zeropad=0,
                                              nodata=I_NODATA),
                 }},
                {"Type": "HeartRate",
                 "NumberSequence": {
                     "Independent": True,
                     "Text": number_text_image(58, 246, I_SMALL, 10, align="Left",
                                              spacing=1, zeropad=0,
                                              nodata=I_NODATA),
                 }},
            ],
        },
        "IdleScreen": {
            "Time": {
                "Digital": {
                    "HoursMinutesSeconds": [
                        {"Type": 0, "Independent": True,
                         "Text": number_text_image(180, 92, I_BIG, 10,
                                                  align="Center", spacing=0,
                                                  zeropad=1)},
                        {"Type": 1, "Independent": True,
                         "Text": number_text_image(180, 198, I_BIG, 10,
                                                  align="Center", spacing=0,
                                                  zeropad=0)},
                    ],
                },
            },
            "Date": {
                "Week": {
                    "Independent": True,
                    "Text": number_text_image(180, 308, I_WEEK, 7, align="Center",
                                              spacing=0, zeropad=0,
                                              unknown6=1),
                },
            },
            "Data": [
                {"Type": "Battery",
                 "CircleScale": {
                     "Angle": {"X": 180, "Y": 180, "StartAngle": 155.0,
                               "EndAngle": 205.0, "Radius": 172.0},
                     "Color": "0xFFED1E28", "Width": 8, "Flatness": 180,
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
        make_digit(str(d), 64, 100, FONT_DISPLAY, 86, WHITE, SHADOW,
                   italic=0.14).save(OUT / f"{3 + d}.png")
        make_digit(str(d), 26, 34, FONT_BOLD, 38).save(OUT / f"{13 + d}.png")
        make_digit(str(d), 19, 25, FONT_BOLD, 30).save(OUT / f"{23 + d}.png")

    make_text_image("--", FONT_BOLD, 30, WHITE).save(OUT / "33.png")
    make_text_image("%", FONT_BOLD, 26, WHITE).save(OUT / "34.png")

    for i, day in enumerate(["TUE", "WED", "THU", "FRI", "SAT", "SUN", "MON"]):
        make_text_image(day, FONT_BOLD, 24, WHITE, tracking=3).save(
            OUT / f"{35 + i}.png")

    assert I_WEEK == 35
    preview_index = 42

    (OUT / "watchface.json").write_text(
        json.dumps(build_params(preview_index), indent=2))
    print("aset ditulis ke", OUT, "| preview index:", preview_index)


if __name__ == "__main__":
    main()
