#!/usr/bin/env python3
"""Validator lingkaran: pastikan semua elemen dinamis di dalam r=175.

Layar fisik bulat; konten di luar lingkaran terpotong bezel. Gagalkan build
bila ada kotak elemen yang keluar. Dijalankan oleh tools/build_all.py.
"""

import json
import math
import sys
from pathlib import Path

from PIL import Image

CX = CY = 180
SAFE_R = 175

# jumlah digit maksimum per elemen (nama -> (lebar_digit_max, suffix?))
MAXDIGITS = {
    ("Time", 0): 2, ("Time", 1): 2,
    ("Calories",): 4, ("Steps",): 5, ("HeartRate",): 3,
    ("Battery",): 3, ("Day",): 2,
}


def box_dist(x, y, w, h):
    return max(math.hypot(px - CX, py - CY)
               for px, py in ((x, y), (x + w, y), (x, y + h), (x + w, y + h)))


def dims(folder, index):
    with Image.open(Path(folder) / f"{index}.png") as im:
        return im.size


def number_box(folder, text_cfg, img_index, count, ndigits, suffix_index=None):
    node = text_cfg["Image"]
    x0, y0 = node["X"], node["Y"]
    cells = [dims(folder, img_index + i)[0] for i in range(count)]
    # lebar terburuk: ndigits digit terlebar + spacing
    widest = sorted(cells, reverse=True)[:ndigits]
    total = sum(widest) + text_cfg.get("Spacing", 0) * max(0, ndigits - 1)
    if suffix_index is not None:
        total += dims(folder, suffix_index)[0]
    h = dims(folder, img_index)[1]
    align = text_cfg.get("Alignment", "Left")
    if align == "Right":
        x = x0 - total
    elif align == "Center":
        x = x0 - total // 2
    else:
        x = x0
    return x, y0, total, h


def main():
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("build/telu")
    params = json.loads((folder / "watchface.json").read_text())
    bad = []

    def check(name, x, y, w, h):
        dist = box_dist(x, y, w, h)
        flag = "OK " if dist <= SAFE_R else "FAIL"
        print("%s %-22s box=(%d,%d %dx%d) maxdist=%.1f" % (flag, name, x, y, w, h, dist))
        if dist > SAFE_R:
            bad.append(name)

    t = params["Time"]["Digital"]
    hms = t["HoursMinutesSeconds"]
    hms = hms if isinstance(hms, list) else [hms]
    for e in hms:
        txt = e["Text"]
        rng = txt["Image"]["ImageRange"]["ImageRange"]
        nd = MAXDIGITS[("Time", e["Type"])]
        check("time type%d" % e["Type"],
              *number_box(folder, txt, rng["ImageIndex"], rng["ImagesCount"], nd))
    for key in ("AM", "PM"):
        ap = t[key]
        rng = ap["ImageRange"]["ImageRange"]
        w, h = dims(folder, rng["ImageIndex"])
        check(key, ap["Coordinates"]["X"], ap["Coordinates"]["Y"], w, h)

    for e in params["System"]["Data"]:
        typ = e["Type"]
        if "NumberSequence" not in e:
            continue
        txt = e["NumberSequence"]["Text"]
        rng = txt["Image"]["ImageRange"]["ImageRange"]
        nd = MAXDIGITS[(typ,)]
        suf = None
        if "SuffixImage" in txt["Image"]:
            s = txt["Image"]["SuffixImage"]["ImageRange"]
            suf = s["ImageIndex"]
        check(typ, *number_box(folder, txt, rng["ImageIndex"], rng["ImagesCount"], nd, suf))

    ymd = params["System"]["Date"]["YearMonthDay"]
    ymd = ymd if isinstance(ymd, list) else [ymd]
    for e in ymd:
        txt = e["Text"]
        rng = txt["Image"]["ImageRange"]["ImageRange"]
        check("day", *number_box(folder, txt, rng["ImageIndex"], rng["ImagesCount"], 2))
    e = params["System"]["Date"]["Week"]
    txt = e["Text"]
    rng = txt["Image"]["ImageRange"]["ImageRange"]
    base, cnt = rng["ImageIndex"], rng["ImagesCount"]
    for i in range(cnt):
        w, h = dims(folder, base + i)
        align = txt.get("Alignment", "Left")
        x0 = txt["Image"]["X"]
        x = x0 if align == "Left" else (x0 - w // 2 if align == "Center" else x0 - w)
        check("weekday%d" % i, x, txt["Image"]["Y"], w, h)

    idle = params["IdleScreen"]
    thms = idle["Time"]["Digital"]["HoursMinutesSeconds"]
    thms = thms if isinstance(thms, list) else [thms]
    for e in thms:
        txt = e["Text"]
        rng = txt["Image"]["ImageRange"]["ImageRange"]
        nd = MAXDIGITS[("Time", e["Type"])]
        check("idle type%d" % e["Type"],
              *number_box(folder, txt, rng["ImageIndex"], rng["ImagesCount"], nd))
    e = idle["Date"]["Week"]
    txt = e["Text"]
    rng = txt["Image"]["ImageRange"]["ImageRange"]
    base, cnt = rng["ImageIndex"], rng["ImagesCount"]
    for i in range(cnt):
        w, h = dims(folder, base + i)
        check("idle weekday%d" % i, 180 - w // 2, txt["Image"]["Y"], w, h)

    if bad:
        print("GAGAL: %d elemen di luar lingkaran: %s" % (len(bad), bad))
        return 1
    print("LINGKARAN AMAN: semua elemen di dalam r=%d" % SAFE_R)
    return 0


if __name__ == "__main__":
    sys.exit(main())
