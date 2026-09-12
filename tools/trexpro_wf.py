#!/usr/bin/env python3
"""Packer/unpacker mandiri untuk watchface Amazfit T-Rex Pro (format UIHH_GT2, 360x360).

Struktur file .bin (uncompressed):
  [0..87]   header 88 byte (signature "UIHH", version 2; kolom ukuran di 76..83)
  [88..]    parameters-info (descriptor offset+panjang tiap parameter)
  [...]     parameters (data layout ter-encode protobuf-like varint)
  [...]     images-info (offset tiap gambar, 4 byte LE per gambar)
  [...]     images (bitmap proprietary, signature 0x424D)

Catatan format: hasil rekayasa komunitas. Deskriptor skema parameter di bawah
diadaptasi dari proyek watchface-js oleh Nadeflore (GPL-3.0, lihat
tools/LICENSE.watchface-js). Implementasi encode/decode di sini ditulis ulang.

Pemakaian:
  python -m tools.trexpro_wf unpack file.bin out_dir
  python -m tools.trexpro_wf pack in_dir out.bin
  Format in_dir/out_dir: watchface.json (parameter dgn nama) + manifest.json
  + <id>.png (gambar 0..N-1) + preview.png (gambar preview 220x220).
"""

import json
import struct
import sys
from pathlib import Path

HEADER_SIZE = 88
PARAM_BUFFER_SIZE_POS = 76
PARAMS_INFO_SIZE_POS = 80
COMPRESSION_START = 40
CHUNK_MAGIC = (0x4F, 0x4E)

# ---------------------------------------------------------------------------
# Varint ala protobuf (7 bit per byte, MSB = lanjut). Baca sebagai int64 signed.
# ---------------------------------------------------------------------------

def read_varint(data, offset):
    value = 0
    for i in range(10):
        byte = data[offset + i]
        value |= (byte & 0x7F) << (i * 7)
        if not (byte & 0x80):
            break
    else:
        raise ValueError("varint terlalu panjang")
    if value >= (1 << 63):
        value -= 1 << 64
    return value, offset + i + 1


def write_varint(value):
    value = int(value) & ((1 << 64) - 1)
    out = bytearray()
    for _ in range(10):
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            break
    return bytes(out)


# ---------------------------------------------------------------------------
# Parameters: sekuens (key, value); key = descriptor>>3; flag 0x02 = punya anak;
# flag 0x01/0x04 (mask 0x05) = float32. Anak = blok N byte berisi parameters.
# ---------------------------------------------------------------------------

def decode_params(buf):
    result = {}
    offset = 0
    n = len(buf)
    while offset < n:
        desc, offset = read_varint(buf, offset)
        key = desc >> 3
        if key == 0:
            raise ValueError("key 0 tidak valid pada offset %d" % offset)
        has_children = desc & 0x02
        if desc & 0x05:
            (value,) = struct.unpack_from("<f", buf, offset)
            offset += 4
        else:
            value, offset = read_varint(buf, offset)
        if has_children:
            size = int(value)
            if size <= 0:
                raise ValueError("ukuran anak <= 0")
            value = decode_params(bytes(buf[offset:offset + size]))
            offset += size
        if key in result:
            if not isinstance(result[key], list):
                result[key] = [result[key]]
            result[key].append(value)
        else:
            result[key] = value
    return result


def encode_params(params):
    out = bytearray()
    for key, value_or_list in params.items():
        key = int(key)
        values = value_or_list if isinstance(value_or_list, list) else [value_or_list]
        for value in values:
            if isinstance(value, bool):
                out += write_varint(key << 3)
                out += write_varint(int(value))
            elif isinstance(value, int):
                # literal varint
                out += write_varint(key << 3)
                out += write_varint(value)
            elif isinstance(value, float):
                # float32, flag 0x05 pada descriptor (meniru file asli)
                out += write_varint((key << 3) | 0x05)
                out += struct.pack("<f", value)
            elif isinstance(value, (dict, list)):
                children = encode_params(value if isinstance(value, dict) else {k: v for d in value for k, v in d.items()})
                out += write_varint((key << 3) | 0x02)
                out += write_varint(len(children))
                out += children
            else:
                raise ValueError("nilai parameter tidak valid: %r" % (value,))
    return bytes(out)


# ---------------------------------------------------------------------------
# Dekompresi chunk LZ77 (untuk membaca file .bin asli yang terkompresi).
# Chunk: [0x4F|0x4E][u16 size][6 byte header] lalu payload sampai size.
# 0x4E = mentah; 0x4F = terkompresi (deskriptor 32 bit, bit=1 berarti match).
# ---------------------------------------------------------------------------

def decompress_uihh(data, start=COMPRESSION_START):
    result = bytearray(data[:start])
    offset = start
    end = len(data)
    while offset < end and data[offset] in CHUNK_MAGIC:
        chunk_type = data[offset]
        chunk_size = struct.unpack_from("<H", data, offset + 1)[0]
        chunk_end = offset + chunk_size
        offset += 9
        if chunk_type == 0x4E:
            result += data[offset:chunk_end]
            offset = chunk_end
            continue
        while offset < chunk_end:
            (desc,) = struct.unpack_from("<I", data, offset)
            if not (desc & 0x80000000):
                raise ValueError("deskriptor tak terduga")
            offset += 4
            for i in range(31):
                if offset >= chunk_end:
                    break
                if (desc >> i) & 1:
                    first = data[offset]
                    low2 = first & 0x03
                    if low2 == 0:
                        length, distance = 3, first >> 2
                        offset += 1
                    elif low2 == 1:
                        pair = struct.unpack_from("<H", data, offset)[0]
                        length, distance = 3, pair >> 2
                        offset += 2
                    elif low2 == 2:
                        pair = struct.unpack_from("<H", data, offset)[0]
                        length = ((pair & 0x003C) >> 2) + 3
                        distance = pair >> 6
                        offset += 2
                    elif (first & 0x7F) == 3:
                        pair = struct.unpack_from("<I", data, offset)[0]
                        length = ((pair & 0x7F80) >> 7) + 3
                        distance = pair >> 15
                        offset += 4
                    else:
                        pair = int.from_bytes(data[offset:offset + 3], "little")
                        length = ((pair & 0x007C) >> 2) + 2
                        distance = pair >> 7
                        offset += 3
                    for _ in range(length):
                        result.append(result[len(result) - distance])
                else:
                    result.append(data[offset])
                    offset += 1
    result += data[offset:]
    return bytes(result)


# ---------------------------------------------------------------------------
# Kompresi chunk LZ77 (meniru file asli; terverifikasi round-trip).
# Chunk: [0x4F][u16 total][00 00 00 10 00 00][payload]. Payload = deskriptor
# 32 bit (bit31 set) + 31 item (0=literal 1 byte, 1=match, beberapa encoding).
# ---------------------------------------------------------------------------

CHUNK_EXTRA = bytes([0, 0, 0, 0x10, 0, 0])
CHUNK_BLOCK = 32768


def _encode_match(length, distance):
    if length == 3 and distance < 64:
        return bytes([(distance << 2) | 0])
    if length == 3 and distance < 16384:
        return struct.pack("<H", (distance << 2) | 1)
    if 3 <= length <= 18 and distance < 1024:
        return struct.pack("<H", (distance << 6) | ((length - 3) << 2) | 2)
    if 3 <= length <= 33 and distance < 131072:
        v = (distance << 7) | ((length - 2) << 2) | 3
        return bytes([v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF])
    # panjang: pecah jadi beberapa match (ditangani pemanggil via cap 33)
    raise ValueError("match tak ter-encode: %d/%d" % (length, distance))


def _compress_block(block, tail_literals=0):
    """tail_literals: paksa N byte terakhir jadi literal (agar chunk/file
    tak berakhir tepat di match multi-byte yang membuat decoder referensi
    over-read melewati EOF)."""
    out = bytearray()
    items = []  # (is_match, payload_bytes)
    # rantai hash trigram -> posisi-posisi terakhir (pencocokan cepat)
    chain = {}
    pos = 0
    end = len(block) - tail_literals
    while pos < end:
        ceiling = min(33, end - pos)
        best_len, best_dist = 0, 0
        if ceiling >= 3:
            key = (block[pos] << 16) | (block[pos + 1] << 8) | block[pos + 2]
            cands = chain.get(key)
            if cands:
                for prev in reversed(cands[-16:]):
                    dist = pos - prev
                    if dist > 131071:
                        continue
                    length = 3
                    while length < ceiling and block[prev + length] == block[pos + length]:
                        length += 1
                    if length > best_len:
                        best_len, best_dist = length, dist
                        if best_len >= ceiling:
                            break
            lst = chain.get(key)
            if lst is None:
                chain[key] = [pos]
            else:
                lst.append(pos)
                if len(lst) > 64:
                    del lst[:32]
        if best_len:
            items.append((1, _encode_match(best_len, best_dist)))
            # daftarkan trigram di dalam match agar rantai tetap akurat
            for k in range(pos + 1, min(pos + best_len, len(block) - 2)):
                kk = (block[k] << 16) | (block[k + 1] << 8) | block[k + 2]
                ll = chain.get(kk)
                if ll is None:
                    chain[kk] = [k]
                else:
                    ll.append(k)
                    if len(ll) > 64:
                        del ll[:32]
            pos += best_len
        else:
            items.append((0, bytes([block[pos]])))
            pos += 1
    for k in range(len(block) - tail_literals, len(block)):
        items.append((0, bytes([block[k]])))
    for i in range(0, len(items), 31):
        group = items[i:i + 31]
        desc = 0x80000000
        for j, (is_match, _) in enumerate(group):
            if is_match:
                desc |= 1 << j
        out += struct.pack("<I", desc)
        for _, payload in group:
            out += payload
    return bytes(out)


def compress_uihh(body):
    """Kompresi body (byte 40+) menjadi chunk-chunk 0x4F."""
    out = bytearray()
    blocks = [body[start:start + CHUNK_BLOCK]
              for start in range(0, len(body), CHUNK_BLOCK)]
    for bi, blk in enumerate(blocks):
        last = (bi == len(blocks) - 1)
        payload = _compress_block(blk, tail_literals=1 if last else 0)
        total = 9 + len(payload)
        assert total <= 0xFFFF, "chunk kebesaran: %d" % total
        out += bytes([0x4F]) + struct.pack("<H", total) + CHUNK_EXTRA + payload
    return bytes(out)


# ---------------------------------------------------------------------------
# Gambar: bitmap proprietary signature 0x424D ("BM" little endian).
# ---------------------------------------------------------------------------

BM_SIG = b"BM"
IMG_HEADER = 16


def decode_image(buf):
    if bytes(buf[0:2]) != BM_SIG:
        raise ValueError("signature gambar bukan BM")
    pixfmt = struct.unpack_from("<H", buf, 2)[0]
    if pixfmt == 0x65:
        return _decode_compressed(buf)
    if pixfmt == 0xFFFF:
        return _decode_32bit(buf)
    width = struct.unpack_from("<H", buf, 4)[0]
    height = struct.unpack_from("<H", buf, 6)[0]
    row = struct.unpack_from("<H", buf, 8)[0]
    bpp = struct.unpack_from("<H", buf, 10)[0]
    pal_count = struct.unpack_from("<H", buf, 12)[0]
    pal_trans = struct.unpack_from("<H", buf, 14)[0]
    pixels = bytearray(4 * width * height)
    if pal_count:
        palette = []
        for i in range(pal_count):
            base = IMG_HEADER + i * 4
            palette.append((buf[base], buf[base + 1], buf[base + 2]))
        psize = pal_count * 4
        ppb = 8 // bpp if bpp < 8 else 1
        mask = (1 << bpp) - 1
        for y in range(height):
            for x in range(width):
                if bpp < 8:
                    byte = buf[IMG_HEADER + psize + y * row + x // ppb]
                    pos = 8 - ((x % ppb) + 1) * bpp
                    cid = (byte >> pos) & mask
                else:
                    cid = buf[IMG_HEADER + psize + y * row + x]
                r, g, b = palette[cid]
                alpha_vis = 0xFF if cid == pal_trans - 1 else 0x00
                o = (y * width + x) * 4
                pixels[o:o + 4] = bytes((r, g, b, 0xFF - alpha_vis))
    else:
        bypp = bpp // 8
        for y in range(height):
            for x in range(width):
                pos = IMG_HEADER + y * row + x * bypp
                if bypp == 4:
                    r, g, b, a = buf[pos], buf[pos + 1], buf[pos + 2], buf[pos + 3]
                else:
                    a = 0x00
                    if bypp == 3:
                        a = buf[pos]
                        rgba = struct.unpack_from(">H", buf, pos + 1)[0]
                    else:
                        (rgba,) = struct.unpack_from("<H", buf, pos)
                    if pixfmt == 0x13:
                        a = (rgba & 0xF000) >> 8
                        b, g, r = (rgba & 0x0F00) >> 4, rgba & 0x00F0, (rgba & 0x000F) << 4
                    elif pixfmt in (0x1C, 0x09):
                        r, g, b = (rgba & 0xF800) >> 8, (rgba & 0x07E0) >> 3, (rgba & 0x001F) << 3
                    else:
                        b, g, r = (rgba & 0xF800) >> 8, (rgba & 0x07E0) >> 3, (rgba & 0x001F) << 3
                o = (y * width + x) * 4
                pixels[o:o + 4] = bytes((r, g, b, 0xFF - a))
    return width, height, bytes(pixels)


def _decode_32bit(buf):
    width = struct.unpack_from("<I", buf, 4)[0]
    height = struct.unpack_from("<I", buf, 8)[0]
    pixels = bytearray(4 * width * height)
    for y in range(height):
        for x in range(width):
            pos = 24 + (y * width + x) * 4
            o = (y * width + x) * 4
            pixels[o:o + 4] = bytes((buf[pos], buf[pos + 1], buf[pos + 2], buf[pos + 3]))
    return width, height, bytes(pixels)


def _decode_compressed(buf):
    width = struct.unpack_from("<H", buf, 4)[0]
    height = struct.unpack_from("<H", buf, 6)[0]
    data_size = struct.unpack_from("<I", buf, 12)[0]
    pixels = bytearray(4 * width * height)
    offset = IMG_HEADER
    end = IMG_HEADER + data_size
    while offset < end:
        y = struct.unpack_from("<H", buf, offset)[0]
        x = struct.unpack_from("<H", buf, offset + 2)[0]
        count = struct.unpack_from("<H", buf, offset + 4)[0]
        offset += 6
        for _ in range(count):
            (rgba,) = struct.unpack_from("<H", buf, offset)
            r, g, b = (rgba & 0xF800) >> 8, (rgba & 0x07E0) >> 3, (rgba & 0x001F) << 3
            o = (y * width + x) * 4
            pixels[o:o + 4] = bytes((r, g, b, 0xFF))
            offset += 2
            x += 1
    return width, height, bytes(pixels)


class ImageNotSupportedError(Exception):
    pass


def encode_image_indexed(pixels, width, height, bpp=8):
    count = 1 << bpp
    out = bytearray(IMG_HEADER + count * 4 + ((bpp * width * height) + 7) // 8)
    out[0:2] = BM_SIG
    struct.pack_into("<H", out, 2, 0x64)
    struct.pack_into("<H", out, 4, width)
    struct.pack_into("<H", out, 6, height)
    struct.pack_into("<H", out, 8, (width * bpp) // 8)
    struct.pack_into("<H", out, 10, bpp)
    struct.pack_into("<H", out, 12, count)
    struct.pack_into("<H", out, 14, 0)
    palette = {}
    for i in range(width * height):
        r, g, b, a = pixels[i * 4:i * 4 + 4]
        alpha_inv = 0xFF - a
        if alpha_inv == 0xFF:
            key = (0, 0, 0, 0xFF)
        elif alpha_inv == 0x00:
            key = (r, g, b, 0x00)
        else:
            raise ImageNotSupportedError("alpha parsial tak didukung gambar indexed")
        if key not in palette:
            if len(palette) >= count:
                raise ImageNotSupportedError("terlalu banyak warna")
            palette[key] = len(palette)
            rr, gg, bb, aa = key
            out[IMG_HEADER + len(palette) * 4 - 4:IMG_HEADER + len(palette) * 4 - 1] = bytes((rr, gg, bb))
            if aa == 0xFF:
                struct.pack_into("<H", out, 14, len(palette))
        out[IMG_HEADER + count * 4 + i] = palette[key]
    return bytes(out)


def encode_image_24bit(pixels, width, height):
    out = bytearray(IMG_HEADER + 3 * width * height)
    out[0:2] = BM_SIG
    struct.pack_into("<H", out, 2, 0x1B)
    struct.pack_into("<H", out, 4, width)
    struct.pack_into("<H", out, 6, height)
    struct.pack_into("<H", out, 8, width * 3)
    struct.pack_into("<H", out, 10, 24)
    struct.pack_into("<H", out, 12, 0)
    struct.pack_into("<H", out, 14, 0)
    for i in range(width * height):
        r, g, b, a = pixels[i * 4:i * 4 + 4]
        pos = IMG_HEADER + i * 3
        out[pos] = 0xFF - a
        rgb = ((b & 0xF8) << 8) | ((g & 0xFC) << 3) | ((r & 0xF8) >> 3)
        struct.pack_into(">H", out, pos + 1, rgb)
    return bytes(out)


def encode_image_32bit(pixels, width, height):
    """Format 32-bit (0xFFFF) — satu-satunya format yang teramati pada SEMUA
    gambar di file-file T-Rex Pro asli. RGBA lurus, alpha TIDAK dibalik."""
    out = bytearray(24 + 4 * width * height)
    out[0:2] = BM_SIG
    struct.pack_into("<H", out, 2, 0xFFFF)
    struct.pack_into("<I", out, 4, width)
    struct.pack_into("<I", out, 8, height)
    struct.pack_into("<I", out, 12, 32)
    struct.pack_into("<I", out, 16, 24)
    struct.pack_into("<H", out, 20, 1)
    struct.pack_into("<H", out, 22, 0)
    out[24:] = bytes(pixels)
    return bytes(out)


def encode_image(pixels, width, height):
    return encode_image_32bit(pixels, width, height)


# ---------------------------------------------------------------------------
# Header template UIHH_GT2 (88 byte). Kolom ukuran ditulis saat pack.
# Diadaptasi dari watchface-js (Nadeflore, GPL-3.0). Lihat tools/LICENSE.watchface-js.
# ---------------------------------------------------------------------------

HEADER_TEMPLATE = bytes([
    85, 73, 72, 72, 2, 0, 255, 255, 255, 255, 255, 1,
    234, 215, 0, 0, 59, 0, 252, 10, 0, 0, 134, 42,
    28, 0, 255, 255, 255, 255, 255, 255,
    36, 26, 52, 0,
]) + bytes([255] * 40) + bytes([
    150, 1, 0, 0, 35, 0, 0, 0, 48, 0, 0, 0,
])
assert len(HEADER_TEMPLATE) == HEADER_SIZE


def image_blob_length(blob):
    """Hitung panjang sebuah blob gambar dari header-nya (tanpa decode penuh)."""
    if bytes(blob[0:2]) != BM_SIG:
        raise ValueError("bukan blob gambar BM")
    pixfmt = struct.unpack_from("<H", blob, 2)[0]
    if pixfmt == 0x65:
        return IMG_HEADER + struct.unpack_from("<I", blob, 12)[0]
    if pixfmt == 0xFFFF:
        w = struct.unpack_from("<I", blob, 4)[0]
        h = struct.unpack_from("<I", blob, 8)[0]
        return 24 + w * h * 4
    w = struct.unpack_from("<H", blob, 4)[0]
    h = struct.unpack_from("<H", blob, 6)[0]
    row = struct.unpack_from("<H", blob, 8)[0]
    pal = struct.unpack_from("<H", blob, 12)[0]
    return IMG_HEADER + pal * 4 + row * h


def pack(parameters, images, compress=False):
    """parameters: dict id(int)->nilai. images: list bytes ter-encode, SEMUA
    gambar reguler (termasuk preview 220x220 sebagai entri terakhir bila ada).

    Meniru file asli: stored count = len(images)+1, tabel berisi len(images)
    entri offset. Referensi preview di parameters menunjuk indeks sebenarnya.
    compress=True: body (byte 40+) dikompresi chunk 0x4F seperti file asli.
    """
    params_info = {"1": {"1": 0, "2": len(images) + 1}}
    blobs = []
    max_len = 0
    for key, value in parameters.items():
        if key == "1":
            continue
        blob = encode_params(value if isinstance(value, dict) else {1: value})
        params_info[key] = {"1": sum(len(b) for b in blobs), "2": len(blob)}
        blobs.append(blob)
        max_len = max(max_len, len(blob))
    params_info["1"]["1"] = sum(len(b) for b in blobs)
    info_blob = encode_params(params_info)
    images_info = bytearray()
    offset = 0
    for blob in images:
        images_info += struct.pack("<I", offset)
        offset += len(blob)
    header = bytearray(HEADER_TEMPLATE)
    struct.pack_into("<I", header, PARAM_BUFFER_SIZE_POS, max_len)
    struct.pack_into("<I", header, PARAMS_INFO_SIZE_POS, len(info_blob))
    head = bytes(header[:COMPRESSION_START])
    tail = bytes(header[COMPRESSION_START:]) + info_blob + b"".join(blobs) + bytes(images_info)
    for blob in images:
        tail += blob
    # @32 = ukuran body terdekompresi setelah 40 byte header (terbukti konsisten
    # pada semua file asli: @32 == declen - 40). Ditulis ke head agar valid
    # baik untuk file compressed maupun uncompressed.
    head = bytearray(head)
    struct.pack_into("<I", head, 32, COMPRESSION_START + len(tail) - 40)
    head = bytes(head)
    if compress:
        tail = compress_uihh(tail)
    return head + tail


def unpack(data):
    """Kembalikan (parameters dict, images reguler list, header).

    Konvensi file asli (dan reader referensi): stored count = R+1, tabel info
    berisi R entri offset untuk R gambar reguler. Preview 220x220 (bila ada)
    adalah gambar reguler biasa; indeksnya dibaca dari parameters.
    """
    if data[COMPRESSION_START] in CHUNK_MAGIC:
        data = decompress_uihh(data, COMPRESSION_START)
    if not (len(data) >= HEADER_SIZE and data[0:4] == b"UIHH"):
        raise ValueError("bukan file UIHH yang valid")
    header = data[:HEADER_SIZE]
    params_info_size = struct.unpack_from("<I", data, PARAMS_INFO_SIZE_POS)[0]
    offset = HEADER_SIZE
    info = decode_params(data[offset:offset + params_info_size])
    offset += params_info_size
    params_size = info[1][1]
    stored_count = info[1][2]
    params = {}
    for key, loc in info.items():
        if key == 1:
            continue
        # Lokasi normal {1: offset, 2: size}; packer lain kadang menulis
        # {2: size} saja untuk parameter kecil di awal (offset implisit 0).
        if isinstance(loc, dict):
            off = loc.get(1, 0)
            size = loc[2]
        else:
            off, size = loc[0], loc[1]
        params[key] = decode_params(data[offset + off:offset + off + size])
    offset += params_size
    table_count = stored_count - 1
    images = []
    cur = offset + table_count * 4
    for i in range(table_count):
        rel = struct.unpack_from("<I", data, offset + i * 4)[0]
        span = image_blob_length(data[cur + rel:])
        images.append(data[cur + rel:cur + rel + span])
    return params, images, header


# ---------------------------------------------------------------------------
# Skema UIHH_GT2 + konversi nama <-> id.
# Skema diadaptasi dari watchface-js (Nadeflore, GPL-3.0).
# ---------------------------------------------------------------------------

SCHEMA = {
    "parameters": {
        "3:Background": {
            "1:Preview": "LocalizedImageRange",
            "2:ImageIndex": "imgid",
            "3:Color": "color",
        },
        "4:Time": {
            "1:Digital": {
                "1:HoursMinutesSeconds": "NumberSequence",
                "2:AM": "PositionedLocalizedImageRange",
                "3:PM": "PositionedLocalizedImageRange",
            },
        },
        "5:System": {
            "1:Status": {
                "1:Bluetooth": "PositionedImage",
                "2:DoNotDisturb": "PositionedImage",
                "3:Lock": "PositionedImage",
                "4:Alarm": "PositionedImage",
            },
            "2:Date": {
                "1:YearMonthDay": "NumberSequence",
                "2:Week": "NumberSequence",
            },
            "3:Data": {
                "1:Type": "datatype",
                "3:CircleScale": {
                    "1:Angle": {
                        "1:X": "int",
                        "2:Y": "int",
                        "3:StartAngle": "float",
                        "4:EndAngle": "float",
                        "5:Radius": "float",
                    },
                    "3:Radius": "int",
                    "4:Color": "color",
                    "5:Width": "int",
                    "6:Flatness": "int",
                    "8:ImageIndex": "imgid",
                },
                "5:NumberSequence": "NumberSequence",
                "7:Icon": "PositionedImage",
            },
        },
        "10:IdleScreen": {
            "1:Time": {
                "1:Digital": {
                    "1:HoursMinutesSeconds": "NumberSequence",
                    "2:AM": "PositionedLocalizedImageRange",
                    "3:PM": "PositionedLocalizedImageRange",
                },
            },
            "2:Date": {
                "1:YearMonthDay": "NumberSequence",
                "2:Week": "NumberSequence",
            },
            "3:Data": {
                "1:Type": "datatype",
                "3:CircleScale": {
                    "1:Angle": {
                        "1:X": "int",
                        "2:Y": "int",
                        "3:StartAngle": "float",
                        "4:EndAngle": "float",
                        "5:Radius": "float",
                    },
                    "3:Radius": "int",
                    "4:Color": "color",
                    "5:Width": "int",
                    "6:Flatness": "int",
                    "8:ImageIndex": "imgid",
                },
                "5:NumberSequence": "NumberSequence",
            },
            "4:BackgroundImageIndex": "imgid",
        },
    },
    "types": {
        "Coordinates": {"1:X": "int", "2:Y": "int"},
        "PositionedImage": {
            "1:Coordinates": "Coordinates",
            "2:ImageIndex": "imgid",
        },
        "ImageRange": {"1:ImageIndex": "imgid", "2:ImagesCount": "int"},
        "LocalizedImageRange": {"1:Language": "int", "2:ImageRange:": "ImageRange"},
        "PositionedLocalizedImageRange": {
            "1:Coordinates": "Coordinates",
            "2:ImageRange": "LocalizedImageRange",
        },
        "PositionedImageRangeWithExtra": {
            "1:X": "int",
            "2:Y": "int",
            "3:NoDataImageIndex": "imgid",
            "4:ImageRange": "LocalizedImageRange",
            "5:DecimalPointImageIndex": "imgid",
            "6:SuffixImage": "LocalizedImageRange",
            "7:DelimiterImageIndex": "imgid",
        },
        "Text": {
            "1:Image": "PositionedImageRangeWithExtra",
            "2:SystemFont": {
                "2:Coordinates": "Coordinates",
                "3:Angle": "int",
                "4:Size": "int",
                "5:Color": "color",
                "6:AppendUnit": "bool",
            },
            "3:Alignment": "halignment",
            "4:Spacing": "int",
            "5:ZeroPadding": "int",
            "6:Unknown6": "int",
        },
        "NumberSequence": {
            "1:Type": "int",
            "2:Independent": "bool",
            "3:Text": "Text",
            "4:Separator": "PositionedImage",
        },
        "Pointer": {
            "1:X": "int",
            "2:Y": "int",
            "3:BackgroundImage": "PositionedLocalizedImageRange",
            "4:PointerImage": "PositionedImage",
            "5:CenterImage": "PositionedImage",
            "6:StartAngle": "float",
            "7:EndAngle": "float",
        },
    },
}

ALIGNMENT = {"TopLeft": 18, "Top": 16, "TopRight": 20, "CenterLeft": 66, "Center": 72,
             "CenterRight": 68, "BottomLeft": 34, "Bottom": 32, "BottomRight": 36,
             "Left": 2, "Right": 4, "HCenter": 8, "VCenter": 64}
HALIGNMENT = {"Left": 0, "Center": 1, "Right": 2}
DATATYPE = {"Battery": 1, "Steps": 2, "Calories": 3, "HeartRate": 4, "PAI": 5,
            "Distance": 6, "Unknown7": 7, "Weather": 8, "UVindex": 9,
            "AirQuality": 10, "Humidity": 11}
ALIGNMENT_INV = {v: k for k, v in ALIGNMENT.items()}
HALIGNMENT_INV = {v: k for k, v in HALIGNMENT.items()}
DATATYPE_INV = {v: k for k, v in DATATYPE.items()}


def _split_schema_key(key):
    parts = str(key).split(":")
    return int(parts[0]), parts[1] if len(parts) > 1 else ""


def _schema_by_id(desc):
    out = {}
    for key, subtype in desc.items():
        sid, name = _split_schema_key(key)
        out[sid] = (name, subtype)
    return out


def _schema_by_name(desc):
    out = {}
    for key, subtype in desc.items():
        sid, name = _split_schema_key(key)
        out[name] = (sid, subtype)
    return out


def _format_value(value, vtype):
    if vtype == "bool":
        return bool(value)
    if vtype == "color":
        return "0x%08X" % (int(value) & 0xFFFFFFFF)
    if vtype == "halignment":
        return HALIGNMENT_INV.get(value, value)
    if vtype == "alignment":
        return ALIGNMENT_INV.get(value, value)
    if vtype == "datatype":
        return DATATYPE_INV.get(value, value)
    return value


def _parse_value(rep, vtype):
    if vtype == "bool":
        return 1 if rep else 0
    if vtype == "color":
        return int(str(rep), 16)
    if vtype == "halignment":
        return HALIGNMENT[rep] if isinstance(rep, str) else int(rep)
    if vtype == "alignment":
        return ALIGNMENT[rep] if isinstance(rep, str) else int(rep)
    if vtype == "datatype":
        return DATATYPE[rep] if isinstance(rep, str) else int(rep)
    return rep


def _resolve_type(subtype):
    if isinstance(subtype, dict):
        return subtype
    return SCHEMA["types"].get(subtype, subtype)


def ids_to_names(node, desc=None):
    """Ubah parameter ber-id angka menjadi nama (untuk dibaca manusia)."""
    if desc is None:
        desc = _schema_by_id(SCHEMA["parameters"])
    if isinstance(node, (int, float)):
        return _format_value(node, desc) if isinstance(desc, str) else node
    if isinstance(node, list):
        return [ids_to_names(v, desc) for v in node]
    out = {}
    for key, value in node.items():
        key = int(key)
        if key not in desc:
            out[key] = ids_to_names(value)
            continue
        name, subtype = desc[key]
        subtype = _resolve_type(subtype)
        if isinstance(subtype, dict):
            subtype = _schema_by_id(subtype)
        out[name] = ids_to_names(value, subtype)
    return out


def names_to_ids(node, desc=None):
    """Ubah parameter bernama menjadi id angka siap pack."""
    if desc is None:
        desc = _schema_by_name(SCHEMA["parameters"])
    if isinstance(node, list):
        return [names_to_ids(v, desc) for v in node]
    if not isinstance(node, dict):
        return _parse_value(node, desc) if isinstance(desc, str) else node
    out = {}
    for name, value in node.items():
        if name not in desc:
            if str(name).lstrip("-").isdigit():
                out[int(name)] = names_to_ids(value)
                continue
            raise ValueError("nama parameter tak dikenal: %r" % name)
        sid, subtype = desc[name]
        subtype = _resolve_type(subtype)
        if isinstance(subtype, dict):
            subtype = _schema_by_name(subtype)
        converted = names_to_ids(value, subtype)
        out[sid] = converted
    return out


def color_to_int(text):
    return int(text, 16)


def main(argv):
    if len(argv) < 3:
        print("pakai: trexpro_wf.py unpack file.bin out_dir | pack in_dir out.bin")
        return 1
    if argv[1] == "unpack":
        from PIL import Image
        data = Path(argv[2]).read_bytes()
        params, images, _ = unpack(data)
        out = Path(argv[3])
        out.mkdir(parents=True, exist_ok=True)
        with open(out / "params_ids.json", "w") as f:
            json.dump(params, f, indent=2, default=str)
        for i, blob in enumerate(images):
            try:
                w, h, px = decode_image(blob)
                Image.frombytes("RGBA", (w, h), px).save(out / f"{i}.png")
            except Exception as e:
                print("gambar %d gagal decode: %s" % (i, e))
        print("ok: %d gambar" % len(images))
    elif argv[1] == "pack":
        print("gunakan tools/pack_watchface.py untuk packing dari folder proyek")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
