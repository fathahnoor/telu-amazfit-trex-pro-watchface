# TEL-U Watchface — Amazfit T-Rex Pro

Watch face **Amazfit T-Rex Pro** bertema **Telkom University (TEL-U)** — tiruan layout
watch face rigger digital (jam besar di kanan, kolom KCAL/STEP/HR di kiri, arc progress),
dengan ornamen & palet warna resmi Telkom University.

> 🚧 **Status: ON PROGRESS — Dikembangkan bertahap, commit kecil per bagian.**

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
├── design/
│   ├── telu-theme.json          <- tema warna + font + ornamen
│   └── LAYOUT.md                <- spesifikasi layout per elemen (koordinat 360x360)
├── assets/
│   ├── 360x360/                 <- PNG per elemen (background, angka, ikon)
│   └── preview/                 <- preview 220x220
├── src/
│   ├── watchface.json           <- deskripsi layout (kompatibel editor legacy T-Rex Pro)
│   └── gen_preview.py           <- generator preview PNG dari watchface.json
├── tools/
│   └── build.py                 <- packer .bin (TBD — tahap berikutnya)
├── docs/
│   ├── guide/                   <- panduan lama (referensi)
│   └── research/                <- hasil riset (device list, warna, dsb.)
└── examples/                    <- contoh watch face rigger asli (referensi visual)
```

---

## Roadmap

- [x] Riset spesifikasi device (T-Rex Pro = 360×360, non-Zepp OS)
- [x] Riset palet warna resmi Telkom University
- [x] Setup repo + README
- [x] Tema & spesifikasi layout (`design/`)
- [ ] Generator asset PNG 360×360 (`assets/`)
- [ ] `watchface.json` + preview renderer
- [ ] Packer `.bin` untuk T-Rex Pro
- [ ] Instruksi instalasi (Developer Mode Zepp App)

---

## Instalasi (Nanti, Setelah Build Berhasil)

1. Aktifkan Developer Mode di Zepp App (tap logo Zepp 5-7x di About)
2. Device → T-Rex Pro → Developer → Watch Face → +
3. Scan QR / pilih file `.bin` hasil build

---

## Referensi

- [Zepp OS Device List (T-Rex Pro = non-Zepp OS, 360×360)](https://docs.zepp.com/docs/reference/related-resources/device-list/)
- [Kode Warna Logo Telkom University](https://it.telkomuniversity.ac.id/kode-warna-logo-telkom-university/)
- [Makna Lambang Telkom University](https://telkomuniversity.ac.id/makna-lambang-telkom-university/)
- [Amazfit Watchface Editor (Android)](https://play.google.com/store/apps/details?id=paolo4c.zepp.wfeditor)
- Panduan lama: `docs/guide/zepp-os-watchface-guide-original.md`
