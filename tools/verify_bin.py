"""Verifikasi .bin hasil pack vs sumber desain (toleran kuantisasi RGB565)."""
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from trexpro_wf import unpack, names_to_ids, decode_image

REPO = Path(__file__).resolve().parent.parent
BIN = REPO / "out" / "telu_trex_pro.bin"
SRC = REPO / "build" / "telu"


def norm(node):
    if isinstance(node, dict):
        return {k: norm(v) for k, v in node.items()}
    if isinstance(node, list) and len(node) == 1:
        return norm(node[0])
    if isinstance(node, list):
        return [norm(v) for v in node]
    return node


params, images, _ = unpack(BIN.read_bytes())
print("bin: %d gambar" % len(images))
assert len(images) == 43, "jumlah gambar harus 43"

named = json.loads((SRC / "watchface.json").read_text())
expected = names_to_ids(named)
exp = norm(json.loads(json.dumps(expected)))
got = norm(json.loads(json.dumps({str(k): v for k, v in params.items()})))
print("params sama:", exp == got)

bad = 0
maxd = 0
for i in range(42):
    src_img = Image.open(SRC / f"{i}.png").convert("RGBA")
    w, h, px = decode_image(images[i])
    assert (w, h) == src_img.size, (i, (w, h), src_img.size)
    a, b = src_img.tobytes(), px
    d = max(abs(x - y) for x, y in zip(a, b))
    maxd = max(maxd, d)
    # piksel fully transparan/opaque harus eksak; hanya tepi antialias yg noise
    if d > 8:
        bad += 1
        print("img %d delta besar: %d" % (i, d))
w, h, px = decode_image(images[42])
src_prev = Image.open(SRC / "preview.png").convert("RGBA")
d = max(abs(x - y) for x, y in zip(src_prev.tobytes(), px))
maxd = max(maxd, d)
print("preview 220x220 ok:", (w, h) == (220, 220), "delta:", d)
print("max delta global:", maxd, "| gambar bermasalah:", bad)
print("VERIFIKASI SELESAI")
