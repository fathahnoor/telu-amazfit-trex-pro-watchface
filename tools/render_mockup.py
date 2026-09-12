#!/usr/bin/env python3
"""Render mockup dari folder build (watchface.json + PNG) untuk verifikasi visual.

Pakai:
  python tools/render_mockup.py build/telu out/mockup_360.png [--small out/mockup_220.png]
  Data contoh bisa dioverride: --time 0512 --kcal 29 --steps 1115 --hr 97
    --batt 92 --wday 2 --day 12 --ampm AM
  wday: 0=TUE..6=MON (konvensi T-Rex Pro teramati).
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
    total = sum(widths) + spacing * (len(cells) - 1)
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
    w = 7
    # PIL: 0 = jam 3, searah jarum jam
    d.arc([cx - r, cy - r, cx + r, cy + r], start=(start + 270) % 360,
          end=(end + 270) % 360, fill=color, width=w)


def main(argv):
    folder = Path(argv[1])
    out = Path(argv[2])
    args = {"time": "0532", "kcal": "29", "steps": "1115", "hr": "97",
            "batt": "92", "wday": "2", "day": "12", "ampm": "AM"}
    for a in argv[3:]:
        if a.startswith("--") and "=" not in a and argv.index(a) + 1 < len(argv):
            pass
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

    def as_list(x):
        return x if isinstance(x, list) else [x]

    canvas = imgs[0].copy()

    t = params["Time"]["Digital"]
    hms = {e["Type"]: e for e in as_list(t["HoursMinutesSeconds"])}
    hh, mm = args["time"][:2], args["time"][2:]
    for typ, digits in ((0, hh), (1, mm)):
        e = hms[typ]
        txt = e["Text"]
        rng = txt["Image"]["ImageRange"]["ImageRange"]
        draw_number(canvas, imgs, txt, digits, rng, txt["Alignment"], txt["Spacing"])
    ap = t["AM" if args["ampm"] == "AM" else "PM"]
    rng = ap["ImageRange"]["ImageRange"]
    badge = imgs[rng["ImageIndex"]]
    canvas.alpha_composite(badge, (ap["Coordinates"]["X"], ap["Coordinates"]["Y"]))

    data = {e["Type"]: e for e in as_list(params["System"]["Data"])}
    for key, digits in (("Calories", args["kcal"]), ("Steps", args["steps"]),
                        ("HeartRate", args["hr"])):
        e = data[key]["NumberSequence"]
        txt = e["Text"]
        rng = txt["Image"]["ImageRange"]["ImageRange"]
        draw_number(canvas, imgs, txt, digits, rng, txt["Alignment"], txt["Spacing"])
    e = data["Battery"]
    draw_arc(canvas, e["CircleScale"]["Angle"], int(args["batt"]) / 100.0, TELU_RED)
    txt = e["NumberSequence"]["Text"]
    rng = txt["Image"]["ImageRange"]["ImageRange"]
    draw_number(canvas, imgs, txt, args["batt"], rng, txt["Alignment"], txt["Spacing"])

    ymd = {e["Type"]: e for e in as_list(params["System"]["Date"]["YearMonthDay"])}
    e = ymd[2]
    txt = e["Text"]
    rng = txt["Image"]["ImageRange"]["ImageRange"]
    draw_number(canvas, imgs, txt, args["day"], rng, txt["Alignment"], txt["Spacing"])
    e = params["System"]["Date"]["Week"]
    txt = e["Text"]
    rng = txt["Image"]["ImageRange"]["ImageRange"]
    base = rng["ImageIndex"]
    wimg = imgs[base + int(args["wday"])]
    x0 = txt["Image"]["X"]
    canvas.alpha_composite(wimg, (x0, txt["Image"]["Y"]))

    canvas.save(out)
    print("mockup:", out)
    if small:
        canvas.resize((220, 220), Image.LANCZOS).save(small)
        print("small:", small)


if __name__ == "__main__":
    main(sys.argv)
