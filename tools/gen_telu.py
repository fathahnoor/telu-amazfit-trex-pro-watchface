#!/usr/bin/env python3
"""Generator aset + watchface.json untuk TEL-U T-Rex Pro (360x360, UIHH_GT2).

Arah desain "REDLINE": jam horizontal, kapsul menit merah, indeks instrumen,
komplikasi ringkas, dan latar idle hitam.

ROUND-SAFE: semua konten teks/ikon/badge wajib di dalam lingkaran aman
r=175 (layar fisik bulat; sudut kotak 360x360 terpotong bezel).

Output ke build/telu/: 0.png background, 1.png AM, 2.png PM,
3-12 digit besar, 13-22 digit kecil, 23-32 digit medium, 33 nodata,
34 persen, 35-41 weekday (MON..SUN), 42 slot kosong, 43 latar idle,
preview.png (indeks 44), watchface.json.
"""

import json
import math
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
    # Instrument bezel: quiet minor ticks and four red cardinal markers.
    for deg in range(0, 360, 6):
        major = deg % 30 == 0
        p1 = watch_angle_xy(180, 180, 169 if major else 173, deg)
        p2 = watch_angle_xy(180, 180, 177, deg)
        d.line([p1, p2], fill=(TELU_RED if deg % 90 == 0 else (68, 70, 76)) + (255,), width=3 if major else 1)
    d.arc([17, 17, 343, 343], 205, 335, fill=TELU_DEEP + (255,), width=2)
    # Compact wordmark, separated from the time and date.
    d.rounded_rectangle([100, 40, 124, 64], radius=6, fill=TELU_RED + (255,))
    d.text((107, 42), "T", font=font(FONT_BOLD, 20), fill=WHITE + (255,))
    d.text((134, 38), "TELKOM", font=font(FONT_BOLD, 20), fill=WHITE + (255,))
    draw_tracked(d, (135, 59), "UNIVERSITY", font(FONT_SEMI, 10), GRAY_LIGHT, 2)
    # A single red minute capsule gives the dial its identity.
    d.rounded_rectangle([187, 112, 303, 216], radius=18, fill=TELU_RED + (255,))
    d.line([69, 222, 291, 222], fill=(42, 43, 49, 255), width=1)
    for x in (130, 236):
        d.line([x, 239, x, 284], fill=(42, 43, 49, 255), width=1)
    for x, label, icon in ((61, "KCAL", icon_flame), (154, "STEPS", icon_steps), (251, "BPM", icon_heart)):
        bg.alpha_composite(icon(12, TELU_RED), (x, 235))
        d.text((x + 16, 232), label, font=font(FONT_SEMI, 14), fill=GRAY_LIGHT + (255,))
    d.rounded_rectangle([126, 303, 139, 311], radius=2, outline=GRAY_LIGHT + (255,), width=1)
    d.rectangle([140, 305, 141, 309], fill=GRAY_LIGHT + (255,))
    d.arc([8, 8, 352, 352], 65, 115, fill=TELU_DEEP + (255,), width=5)
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
    img = Image.new("RGBA", (30, 19), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, 29, 18], radius=4, fill=(38, 39, 45, 255))
    d.text((15, 9), text, font=font(FONT_BOLD, 14), anchor="mm", fill=WHITE + (255,))
    return img


def make_digit(ch, cell_w, cell_h, font_path, font_size, fill=WHITE,
               shadow=None, italic=0.0):
    img = Image.new("RGBA", (cell_w * 2, cell_h * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fnt = font(font_path, font_size * 2)
    w, h = text_size(d, ch, fnt)
    box = d.textbbox((0, 0), ch, font=fnt)
    x = (cell_w * 2 - w) // 2 - box[0]
    y = (cell_h * 2 - h) // 2 - box[1]
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
    img = Image.new("RGBA", (tw + pad * 2 * scale, th + font_size * scale + pad * 2 * scale), (0, 0, 0, 0))
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
I_BIG = 3        # 3..12 digit besar Anton
I_SMALL = 13     # 13..22 digit Rajdhani Bold (nilai)
I_MED = 23       # 23..32 digit Rajdhani (baterai %, tanggal)
I_NODATA = 33
I_PCT = 34
I_WEEK = 35      # 35..41 MON..SUN

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


# Koordinat kiri utk elemen yang dulu rata kanan. Firmware T-Rex Pro tidak
# menghormati Alignment "Right" (teks mulai di X lalu memanjang ke kanan,
# sehingga jam masuk kapsul dan menit keluar layar). Semua elemen digambar
# dengan Alignment "Left" + X hasil hitung lebar maksimum.
HOURS_X = 62       # 170 - 2 digit x 54
MINUTES_X = 191    # 299 - 2 digit x 54
BATTERY_TEXT_X = 159  # 220 - (3 digit + suffix)


def time_digital():
    """Blok waktu horizontal; dipakai tampilan utama maupun idle."""
    return {
        "HoursMinutesSeconds": [
            {"Type": 0, "Independent": True,
             "Text": number_text_image(HOURS_X, 114, I_BIG, 10, align="Left",
                                      spacing=0, zeropad=1)},
            {"Type": 1, "Independent": True,
             "Text": number_text_image(MINUTES_X, 114, I_BIG, 10, align="Left",
                                      spacing=0, zeropad=1)},
        ],
        "AM": {"Coordinates": {"X": 237, "Y": 83},
               "ImageRange": img_range(I_AM, 1)},
        "PM": {"Coordinates": {"X": 237, "Y": 83},
               "ImageRange": img_range(I_PM, 1)},
    }


def date_system():
    return {
        "YearMonthDay": [
            {"Type": 2, "Independent": True,
             "Text": number_text_image(192, 83, I_MED, 10, align="Left",
                                      spacing=2, zeropad=1)},
        ],
        "Week": {
            "Independent": True,
            "Text": number_text_image(129, 86, I_WEEK, 7, align="Left",
                                      spacing=0, zeropad=0, unknown6=1),
        },
    }


def data_system():
    return [
        {"Type": "Battery",
         "CircleScale": {
             "Angle": {"X": 180, "Y": 180, "StartAngle": 155.0,
                       "EndAngle": 205.0, "Radius": 172.0},
             "Color": "0xFFED1E28", "Width": 5, "Flatness": 180,
         },
         "NumberSequence": {
             "Independent": True,
             "Text": number_text_image(BATTERY_TEXT_X, 297, I_MED, 10,
                                      align="Left", spacing=2, zeropad=0,
                                      suffix=img_range(I_PCT, 1)),
         }},
        {"Type": "Steps",
         "NumberSequence": {
             "Independent": True,
             "Text": number_text_image(146, 253, I_SMALL, 10, align="Left",
                                      spacing=1, zeropad=0,
                                      nodata=I_NODATA),
         }},
        {"Type": "Calories",
         "NumberSequence": {
             "Independent": True,
             "Text": number_text_image(59, 253, I_SMALL, 10, align="Left",
                                      spacing=1, zeropad=0,
                                      nodata=I_NODATA),
         }},
        {"Type": "HeartRate",
         "NumberSequence": {
             "Independent": True,
             "Text": number_text_image(250, 253, I_SMALL, 10, align="Left",
                                      spacing=1, zeropad=0,
                                      nodata=I_NODATA),
         }},
    ]


def build_params(preview_index):
    """Tampilan utama dan selalu-nyala (idle) memakai layout yang sama,
    termasuk latar, sehingga preview, jam utama, dan always-on identik."""
    return {
        "Background": {
            "Preview": img_range(preview_index, 1),
            "ImageIndex": I_BG,
        },
        "Time": {"Digital": time_digital()},
        "System": {"Date": date_system(), "Data": data_system()},
        "IdleScreen": {
            "Time": {"Digital": time_digital()},
            "Date": date_system(),
            "Data": data_system(),
            "BackgroundImageIndex": I_BG,
        },
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    make_background().save(OUT / "0.png")
    make_badge("AM").save(OUT / "1.png")
    make_badge("PM").save(OUT / "2.png")

    for d in range(10):
        make_digit(str(d), 54, 100, FONT_DISPLAY, 91, WHITE, None,
                   italic=0.0).save(OUT / f"{3 + d}.png")
        make_digit(str(d), 16, 30, FONT_BOLD, 29).save(OUT / f"{13 + d}.png")
        make_digit(str(d), 15, 22, FONT_BOLD, 23).save(OUT / f"{23 + d}.png")

    make_text_image("--", FONT_BOLD, 30, WHITE).save(OUT / "33.png")
    make_text_image("%", FONT_BOLD, 20, GRAY_LIGHT).save(OUT / "34.png")

    for i, day in enumerate(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]):
        make_text_image(day, FONT_BOLD, 19, WHITE, tracking=2).save(
            OUT / f"{35 + i}.png")

    assert I_WEEK == 35
    preview_index = 44
    Image.new("RGBA", (360, 360), BLACK + (255,)).save(OUT / "43.png")
    # Slot 42 used to be the preview. Keep numbered assets contiguous.
    Image.new("RGBA", (1, 1), (0, 0, 0, 0)).save(OUT / "42.png")

    (OUT / "watchface.json").write_text(
        json.dumps(build_params(preview_index), indent=2))
    print("aset ditulis ke", OUT, "| preview index:", preview_index)


if __name__ == "__main__":
    main()
