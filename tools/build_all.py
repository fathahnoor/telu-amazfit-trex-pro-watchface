#!/usr/bin/env python3
"""Satu perintah build penuh: aset -> mockup -> pack -> verifikasi.

Pakai dari root repo:
  python tools/build_all.py
Hasil: out/telu_trex_pro.bin untuk uji instalasi pada jam.
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(*args):
    print("+", " ".join(args))
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def main():
    run("tools/gen_telu.py")
    run("tools/check_round.py", "build/telu")
    run("tools/render_mockup.py", "build/telu", "build/mockup_360.png",
        "--small", "build/mockup_220.png")
    shutil.copy(ROOT / "build" / "mockup_220.png", ROOT / "build" / "telu" / "preview.png")
    (ROOT / "out").mkdir(exist_ok=True)
    run("tools/pack_watchface.py", "build/telu", "out/telu_trex_pro.bin")
    run("tools/verify_bin.py")
    run("tools/render_mockup.py", "build/verified_bin", "out/preview.png")
    run("tools/render_mockup.py", "build/verified_bin", "out/preview_max.png",
        "--time", "1259", "--steps", "99999", "--kcal", "9999",
        "--hr", "199", "--batt", "100", "--day", "31", "--wday", "1", "--ampm", "PM")
    run("tools/render_mockup.py", "build/verified_bin", "out/preview_zero.png",
        "--time", "0007", "--steps", "0", "--kcal", "0", "--hr", "0", "--batt", "0")
    run("tools/render_mockup.py", "build/verified_bin", "out/preview_idle.png", "--mode", "idle")
    shutil.copyfile(ROOT / "out/telu_trex_pro.bin", ROOT / "out/telu_redline_compat_v4.bin")
    print("BUILD OK -> out/telu_trex_pro.bin (alias: out/telu_redline_compat_v4.bin)")


if __name__ == "__main__":
    main()
