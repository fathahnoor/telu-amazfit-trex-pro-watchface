#!/usr/bin/env python3
"""Render mockup dari folder build (watchface.json + PNG) untuk verifikasi visual.

Pakai:
  python tools/render_mockup.py build/telu out/mockup_360.png [--small out/mockup_220.png]
  Data contoh bisa dioverride: --time 0512 --kcal 29 --steps 1115 --hr 97
    --batt 92 --wday 2 --day 12 --ampm AM
  wday: 0=MON..6=SUN (konvensi T-Rex Pro teramati).
"""

import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

TELU_RED = (237, 30, 40, 255)
HALIGN = {"Left": 0, "Center": 1, "Right": 2}


def load(folder):
    folder = Path(folder)
    params = json.loads((folder / "watchface.json").read_text())
    imgs = {}
    for p in folder.glob("[0-9]*.png"):
        imgs[int(p.stem)] = Image.open(p).convert("RGBA")
    return params, imgs


def draw_number(canvas, imgs, text_cfg, digits, rng, align, spacing):
    """Gambar deretan digit. text_cfg = node Text (punya Image)."""
    node = text_cfg["Image"]
    x0, y0 = node["X"], node["Y"]
    base, count = rng["ImageIndex"], rng["ImagesCount"]
    if text_cfg.get("ZeroPadding") and len(digits) < 2:
        digits = digits.rjust(2, "0")
    cells = [imgs[base + int(ch)] for ch in digits]
    widths = [c.width for c in cells]
    suffix = node.get("SuffixImage")
    simg = imgs[suffix["ImageRange"]["ImageIndex"]] if suffix else None
    total = sum(widths) + spacing * (len(cells) - 1)
    if simg is not None:
        total += spacing + simg.width
    if align == "Right":
        x = x0 - total
    elif align == "Center":
        x = x0 - total // 2
    else:
        x = x0
    for cell, w in zip(cells, widths):
        canvas.alpha_composite(cell, (int(x), y0))
        x += w + spacing
    suffix = node.get("SuffixImage")
    if suffix:
        s = suffix["ImageRange"]
        simg = imgs[s["ImageIndex"]]
        canvas.alpha_composite(simg, (int(x), y0))
        x += simg.width
    return int(x)


def draw_arc(canvas, angle, frac, color):
    d = ImageDraw.Draw(canvas)
    cx, cy = angle["X"], angle["Y"]
    r = angle["Radius"]
    start = angle["StartAngle"]
    span = (angle["EndAngle"] - start) % 360
    end = start + span * max(0.0, min(1.0, frac))
    w = 5
    if frac <= 0:
        return
    # PIL: 0 = jam 3, searah jarum jam
    d.arc([cx - r, cy - r, cx + r, cy + r], start=(start + 270) % 360,
          end=(end + 270) % 360, fill=color, width=w)


def as_list(value):
    return value if isinstance(value, list) else [value]


def draw_face(canvas, imgs, time_block, date_block, data_list, args):
    """Gambar seluruh elemen dinamis; dipakai tampilan utama dan idle."""
    hms = {e["Type"]: e for e in as_list(time_block["HoursMinutesSeconds"])}
    hh, mm = args["time"][:2], args["time"][2:]
    for typ, digits in ((0, hh), (1, mm)):
        e = hms[typ]
        txt = e["Text"]
        rng = txt["Image"]["ImageRange"]["ImageRange"]
        draw_number(canvas, imgs, txt, digits, rng, txt["Alignment"], txt["Spacing"])
    ap = time_block["AM" if args["ampm"] == "AM" else "PM"]
    rng = ap["ImageRange"]["ImageRange"]
    badge = imgs[rng["ImageIndex"]]
    canvas.alpha_composite(badge, (ap["Coordinates"]["X"], ap["Coordinates"]["Y"]))

    ymd = {e["Type"]: e for e in as_list(date_block["YearMonthDay"])}
    e = ymd[2]
    txt = e["Text"]
    rng = txt["Image"]["ImageRange"]["ImageRange"]
    draw_number(canvas, imgs, txt, args["day"], rng, txt["Alignment"], txt["Spacing"])
    txt = date_block["Week"]["Text"]
    rng = txt["Image"]["ImageRange"]["ImageRange"]
    wimg = imgs[rng["ImageIndex"] + int(args["wday"])]
    x0, y0 = txt["Image"]["X"], txt["Image"]["Y"]
    align = txt.get("Alignment", "Left")
    if align == "Right":
        x0 -= wimg.width
    elif align == "Center":
        x0 -= wimg.width // 2
    canvas.alpha_composite(wimg, (x0, y0))

    data = {e["Type"]: e for e in as_list(data_list)}
    for key, digits in (("Calories", args["kcal"]), ("Steps", args["steps"]),
                        ("HeartRate", args["hr"])):
        e = data[key]["NumberSequence"]
        txt = e["Text"]
        rng = txt["Image"]["ImageRange"]["ImageRange"]
        draw_number(canvas, imgs, txt, digits, rng, txt["Alignment"], txt["Spacing"])
    e = data["Battery"]
    draw_arc(canvas, e["CircleScale"]["Angle"], int(args["batt"]) / 100.0, TELU_RED)
    if "NumberSequence" in e:
        txt = e["NumberSequence"]["Text"]
        rng = txt["Image"]["ImageRange"]["ImageRange"]
        draw_number(canvas, imgs, txt, args["batt"], rng, txt["Alignment"], txt["Spacing"])


def main(argv):
    folder = Path(argv[1])
    out = Path(argv[2])
    args = {"time": "0532", "kcal": "29", "steps": "1115", "hr": "97",
            "batt": "92", "wday": "5", "day": "12", "ampm": "AM"}
    i = 3
    while i < len(argv):
        if argv[i].startswith("--"):
            key = argv[i][2:]
            if key == "small":
                i += 2
                continue
            args[key] = argv[i + 1]
            i += 2
        else:
            i += 1
    small = None
    if "--small" in argv:
        small = Path(argv[argv.index("--small") + 1])

    params, imgs = load(folder)

    if args.get("mode") == "idle":
        idle = params["IdleScreen"]
        canvas = imgs[idle["BackgroundImageIndex"]].copy()
        draw_face(canvas, imgs, idle["Time"]["Digital"], idle["Date"],
                  idle["Data"], args)
    else:
        canvas = imgs[0].copy()
        draw_face(canvas, imgs, params["Time"]["Digital"],
                  params["System"]["Date"], params["System"]["Data"], args)

    canvas.save(out)
    print("mockup:", out)
    if small:
        canvas.resize((220, 220), Image.LANCZOS).save(small)
        print("small:", small)


if __name__ == "__main__":
    main(sys.argv)
