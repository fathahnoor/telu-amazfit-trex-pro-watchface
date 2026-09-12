#!/usr/bin/env python3
"""Satu perintah build penuh: aset -> mockup -> pack -> verifikasi.

Pakai dari root repo:
  python tools/build_all.py
Hasil: out/telu_trex_pro.bin siap import ke jam.
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
    run("tools/render_mockup.py", "build/telu", "build/mockup_360.png",
        "--small", "build/mockup_220.png")
    shutil.copy(ROOT / "build" / "mockup_220.png", ROOT / "build" / "telu" / "preview.png")
    (ROOT / "out").mkdir(exist_ok=True)
    run("tools/pack_watchface.py", "build/telu", "out/telu_trex_pro.bin")
    run("tools/verify_bin.py")
    print("BUILD OK -> out/telu_trex_pro.bin")


if __name__ == "__main__":
    main()
