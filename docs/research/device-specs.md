# Research: Spesifikasi Amazfit T-Rex Pro (untuk watchface)

**Tanggal riset:** 2026-09-12
**Sumber utama:** [Device Basic Information - docs.zepp.com](https://docs.zepp.com/docs/reference/related-resources/device-list/)

## Fakta Resmi dari Zepp Docs

T-Rex Pro terdaftar di bagian **"Non-Zepp OS Devices"**:

| Parameter | Nilai |
|---|---|
| Equipment name | Amazfit T-Rex Pro |
| deviceSource | `83, 200` (200 = versi Mainland China) |
| Screen shape | Round |
| Screen resolution | **360 x 360** |
| Physical keys | 4 |
| Watchface preview image resolution | **220 x 220** |

## Implikasi untuk Development

1. **Tidak bisa pakai Zepp OS SDK/CLI** (`@zeppos/cli`, `createWidget`, dsb.) - T-Rex Pro bukan perangkat Zepp OS.
2. Format watchface = `.bin` legacy Amazfit (sama keluarga dengan T-Rex / GTR 2e era firmware lama).
3. Toolchain umum yang dipakai komunitas:
   - **Amazfit Watchface Editor** (Android, paolo4c) - mendukung model T-Rex klasik.
   - **SashaCX75 AmazFit Watchface Editor** (Windows) - mendukung T-Rex.
   - **amazfitwatchfaces.com** - katalog + forum + tools.
4. Rute paling pragmatis untuk repo ini:
   - Desain asset & layout di sini (PNG 360x360 + koordinat).
   - Rekonstruksi layout jadi file yang bisa dibuka editor legacy, atau pak `"T-Rex Pro"` template bawaan editor dan timpa asset.

## Catatan

- Preview official di Zepp App = 220x220 (dipakai saat upload ke katalog).
- T-Rex Pro tidak mendukung AOD interaktif ala Zepp OS; elemen statis + data fields saja.
