# TEL-U Watchface — Amazfit T-Rex Pro

Watch face **Amazfit T-Rex Pro** bertema **Telkom University (TEL-U)** —
gaya "MIDNIGHT BLAZE": tipografi condensed italic memimpin (Anton + Rajdhani),
hitam dominan + merah Tel-U tajam, monogram T angular raksasa, chip data,
lockup branding kotak-T. Round-safe (lolos validator lingkaran r=175).

> ✅ **Status: SELESAI — `out/telu_trex_pro.bin` siap import ke jam.**
> Build satu perintah (`python tools/build_all.py`), terverifikasi parse balik.

---

## Spesifikasi Perangkat (Terverifikasi dari docs resmi Zepp)

| Parameter | Nilai |
|---|---|
| Model | Amazfit T-Rex Pro |
| Platform | **Non-Zepp OS** (firmware legacy) |
| deviceSource | `83` (global), `200` (China) |
| Resolusi layar | **360 × 360 px** |
| Preview image | 220 × 220 px |
| deviceSource | `83` (global), `200` (China) |
| Format output | `.bin` (watchface legacy Amazfit) |
| Tombol fisik | 4 (UP / SELECT / DOWN / BACK) |



> ⚠️ **Koreksi dari panduan lama:** panduan sebelumnya menyebut T-Rex Pro 454×454 + Zepp OS.
> Berdasarkan [device list resmi](https://docs.zepp.com/docs/reference/related-resources/device-list/),
> T-Rex Pro ada di daftar **Non-Zepp OS Devices** dengan layar 360×360.
> Panduan lama tetap disimpan di `docs/guide/` sebagai referensi historis.

---

## Tema Warna Telkom University

| Warna | Hex | Kegunaan di watch face |
|---|---|---|
| Merah Tel-U | `#ED1E28` | Aksen utama, arc progress, penanda AM/PM |
| Merah Marun | `#B6252A` | Aksen sekunder, penanda jam (marker arc) |
| Abu Gelap | `#55565B` | Teks sekunder, garis pembatas |
| Abu Terang | `#959597` | Ikon, elemen non-prioritas |
| Putih | `#FFFFFF` | Angka jam utama |
| Hitam | `#000000` | Background |

*(Sumber: [it.telkomuniversity.ac.id — kode warna resmi](https://it.telkomuniversity.ac.id/kode-warna-logo-telkom-university/))*

---

## Layout (Tiruan Watch Face Rigger)

```
┌──────────────────────────────────┐
│  KCAL              🔥 05:45      │   <- kolom kiri + jam kecil + ikon aktivitas
│   29                             │
│  ──────          ┌────────┐      │
│  STEP           │        │      │
│  1115           │  05    │      │   <- jam digital BESAR (putih)
│  ──────         │  32    │      │   <- menit digital BESAR (putih)
│  HR             │        │      │
│   97        ►AM │        │      │   <- penanda AM/PM (merah Tel-U)
│  ╱arc           └────────┘      │
│  ╱progress       SAT 12         │   <- tanggal (merah Tel-U)
└──────────────────────────────────┘
```

**Elemen watch face:**
- Jam digital besar (HH / MM putih, font tebal)
- Indikator AM/PM dengan panah merah Tel-U
- Kolom kiri: KCAL, STEP, HR (label abu + angka putih)
- Arc progress baterai (merah Tel-U → marun)
- Jam kecil atas (HH:MM + ikon aktivitas)
- Tanggal (SAT 12) merah Tel-U
- Ornamen TEL-U: logo/teks branding + ring marun halus di tepi

---

## Struktur Repo

```
telu-amazfit-trex-pro-watchface/
├── README.md                    <- file ini
├── preview.html                 <- halaman inspeksi visual (buka langsung)
├── out/
│   └── telu_trex_pro.bin        <- WATCHFACE JADI, siap import ke jam
├── design/
│   ├── telu-theme.md            <- aturan tema warna + ornamen TEL-U
│   ├── LAYOUT.md                <- spesifikasi layout final + peta indeks gambar
│   └── watchface.json           <- layout machine-readable (lama, lihat build/)
├── build/                       <- output pipeline (gitignored, reproducible)
│   └── telu/                    <- PNG bernomor 0..41 + preview.png + watchface.json
├── assets/
│   ├── 360x360/                 <- bg final + arsip skema lama
│   └── preview/                 <- mockup final + render dari .bin
├── tools/
│   ├── build_all.py             <- SATU perintah build penuh + verifikasi
│   ├── gen_telu.py              <- generator desain (gambar + watchface.json)
│   ├── render_mockup.py         <- render mockup dari folder build / dari .bin
│   ├── pack_watchface.py        <- pack folder build jadi .bin
│   ├── trexpro_wf.py            <- packer/unpacker mandiri format UIHH_GT2
│   ├── verify_bin.py            <- verifikasi .bin vs sumber desain
│   ├── LICENSE.watchface-js    <- atribusi skema/format (GPL-3.0)
│   ├── gen_assets.py            <- generator lama (arsip)
│   └── gen_digits.py            <- generator lama (arsip)
└── docs/
    ├── build-install.md         <- cara build + instalasi ke jam
    ├── guide/                   <- panduan lama (referensi)
    └── research/                <- hasil riset (device, warna, editor, format .bin)
```

---

## Roadmap

- [x] Riset spesifikasi device (T-Rex Pro = 360×360, non-Zepp OS)
- [x] Riset palet warna resmi Telkom University
- [x] Setup repo + README
- [x] Tema & spesifikasi layout (`design/`)
- [x] Generator asset PNG 360×360 (`tools/gen_assets.py`, `tools/gen_digits.py`)
- [x] Asset hasil generate: bg, branding, ampm, digit 0–9, preview mockup
- [x] `design/watchface.json` (layout machine-readable)
- [x] Panduan build `.bin` via editor komunitas (`docs/build-install.md`)
- [x] Packer `.bin` mandiri (`tools/trexpro_wf.py`, format UIHH_GT2 tereverse
      dari 4 file asli + validasi round-trip melawan implementasi referensi)
- [x] Watchface jadi `out/telu_trex_pro.bin` (43 gambar, preview 220×220)
- [x] Verifikasi visual: mockup + uji tepi + render ulang dari isi `.bin`
- [ ] Foto hasil di jam (verifikasi final oleh pemilik jam)

---

## Instalasi

File jadi: **`out/telu_trex_pro.bin`** (770 KB, 43 gambar, preview 220×220).

1. Aktifkan Developer Mode di Zepp App (tap logo Zepp 5-7x di About)
2. HP + laptop satu WiFi → di laptop: `cd out` lalu `python -m http.server 8000`
3. Buka `assets/qr_install.png` di layar laptop
4. Zepp: Developer Mode → **+** → **Scan** → scan QR → unduh → sync ke jam

Build ulang dari nol (butuh Python + Pillow): `python tools/build_all.py`.
Detil: `docs/build-install.md`.

---

## Referensi

- [Zepp OS Device List (T-Rex Pro = non-Zepp OS, 360×360)](https://docs.zepp.com/docs/reference/related-resources/device-list/)
- [Kode Warna Logo Telkom University](https://it.telkomuniversity.ac.id/kode-warna-logo-telkom-university/)
- [Makna Lambang Telkom University](https://telkomuniversity.ac.id/makna-lambang-telkom-university/)
- [Amazfit Watchface Editor (Android)](https://play.google.com/store/apps/details?id=paolo4c.zepp.wfeditor)
- Panduan lama: `docs/guide/zepp-os-watchface-guide-original.md`
