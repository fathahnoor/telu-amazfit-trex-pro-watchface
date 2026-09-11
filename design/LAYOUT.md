# TEL-U Watchface — Layout Spec (360 × 360)

Tiruan watch face "rigger" digital dengan tema Telkom University.
Semua koordinat dalam px, origin kiri-atas, layar **360×360**.

## Zona

```
(0,0)
  ┌────────────────────────────────────┐
  │            [zona jam kecil]        │  y: 8–40
  │  [kolom kiri]   [zona jam besar]   │  x kiri: 8–150 ; x kanan: 150–352
  │                 [penanda AM/PM]    │  y: 150–210
  │  [arc progress]                    │  ring radius ~170
  │           [branding TEL-U]         │  y: 330–352
  └────────────────────────────────────┘
```

## Elemen

| # | Elemen | Type | Posisi (x, y) | Ukuran | Warna | Catatan |
|---|---|---|---|---|---|---|
| 1 | Background | IMG | 0, 0 | 360×360 | hitam + ornamen | `bg.png` |
| 2 | Ring ornamen marun | IMG (di bg) | pusat 180,180 | r=170 | `#B6252A` | tipis, alpha rendah |
| 3 | Arc progress baterai | ARC | center 180,180, r=158, 135°→45° (kiri) | lw=6 | `#ED1E28` | level = baterai |
| 4 | Jam kecil (HH:MM) | TEXT | 196, 12 | w=150 h=28 | putih | format 12h, prefix ikon aktivitas |
| 5 | Label KCAL | TEXT | 16, 48 | w=110 h=24 | `#959597` | |
| 6 | Nilai KCAL | TEXT | 16, 74 | w=110 h=32 | putih | |
| 7 | Separator 1 | IMG/line | 16, 112 | w=110 h=2 | `#55565B` | |
| 8 | Label STEP | TEXT | 16, 122 | w=110 h=24 | `#ED1E28` | |
| 9 | Nilai STEP | TEXT | 16, 148 | w=110 h=32 | putih | |
| 10 | Separator 2 | IMG/line | 16, 186 | w=110 h=2 | `#55565B` | |
| 11 | Label HR | TEXT | 16, 196 | w=110 h=24 | `#ED1E28` | |
| 12 | Nilai HR | TEXT | 16, 222 | w=110 h=32 | putih | + ikon petir kecil utk baterai % |
| 13 | Jam besar HH | TEXT_IMG | 172, 96 | tinggi 72 | putih | font tebal, right-align di 268 |
| 14 | Jam besar MM | TEXT_IMG | 172, 180 | tinggi 72 | putih | |
| 15 | Penanda AM/PM | IMG | 268, 168 | 36×28 | `#ED1E28` | segitiga + teks |
| 16 | Tanggal (SAB 12) | TEXT | 172, 268 | w=150 h=26 | `#ED1E28` | hari merah, tanggal putih |
| 17 | Branding TEL-U | IMG | pusat, y=330 | ~140×20 | putih + merah | teks "TELKOM UNIVERSITY" |

## Font

- Jam besar: font tebal internal editor (atau digit PNG custom 48-72px tinggi).
- Label & angka kecil: font bawaan system (atau PNG 24px).

## Catatan AMOLED

- Background hitam murni `#000000` — piksel mati = hemat baterai.
- Ornamen marun alpha 30-40% supaya tidak mengganggu keterbacaan.
