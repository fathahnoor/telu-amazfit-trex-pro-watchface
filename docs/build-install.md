# Build & Instalasi — TEL-U Watchface (T-Rex Pro)

## Status: SIAP IMPORT

File **`out/telu_trex_pro.bin`** adalah watchface jadi untuk Amazfit T-Rex Pro
(360×360, format UIHH_GT2). Terverifikasi: parse balik 43 gambar + parameter
identik dengan desain, dan mockup dirender ulang dari isi `.bin` itu sendiri
(lihat `assets/preview/frombin_360.png`).

## Build Ulang (satu perintah)

Butuh Python + Pillow saja, tanpa tool lain:

```powershell
python tools/build_all.py
```

Alurnya: `tools/gen_telu.py` (gambar + `watchface.json`) → `tools/render_mockup.py`
(mockup) → `tools/pack_watchface.py` (pack jadi `.bin` via `tools/trexpro_wf.py`)
→ `tools/verify_bin.py` (verifikasi otomatis, gagal bila beda).

Packer `tools/trexpro_wf.py` mandiri (tanpa dependency selain Pillow untuk
unpack ke PNG): format UIHH_GT2 di-reverse dari file asli katalog komunitas
dan divalidasi round-trip byte-identik melawan implementasi referensi
(watchface-js). Catatan format ada di `docs/research/format-uihh-gt2.md`.

## Instalasi ke Jam

> Koreksi penting: Zepp App versi sekarang TIDAK bisa memasang `.bin` legacy
> lewat Developer Mode → Scan. Menu Scan/Bridge di aplikasi adalah alur
> dev-bridge **Zepp OS** (butuh JS runtime di jam); T-Rex Pro adalah RTOS
> legacy sehingga QR URL biasa ditolak ("unrecognized QR code"). Pakai salah
> satu jalur di bawah.

### Opsi A — Gadgetbridge (terverifikasi di source code)

Source Gadgetbridge (`AmazfitTRexProFirmwareInfo`) mengenali file berformat
ini (`UIHH` + version 1/2) sebagai `WATCHFACE` untuk `AMAZFITTREXPRO`:

1. Install Gadgetbridge (Android, F-Droid) dan pair-kan T-Rex Pro di sana.
2. Salin `out/telu_trex_pro.bin` ke HP.
3. Buka file `.bin` tersebut lewat Gadgetbridge (file manager → Open with →
   Gadgetbridge) → konfirmasi instalasi watchface → sync ke jam.

### Opsi B — AmazFaces (aplikasi komunitas)

1. Install AmazFaces di HP dan salin `out/telu_trex_pro.bin` ke HP.
2. Di AmazFaces: impor file `.bin` → pilih T-Rex Pro → install ke jam.
3. (Katalog amazfitwatchfaces.com memang menyalurkan file `.bin` T-Rex Pro
   lewat aplikasi ini.)

## Catatan Preview Katalog

Preview untuk katalog Zepp: **220×220** — tertanam di dalam `.bin` sebagai
gambar terakhir (index 42), dibuat dari `build/mockup_220.png`.

## Konvensi yang Dipakai Desain Ini (hasil riset file asli)

- Weekday 7 gambar berurutan **TUE..MON** (teramati pada 3 file T-Rex Pro asli
  dari 2 author berbeda; firmware menampilkan index 0 saat Selasa).
- `stored count` = jumlah gambar + 1 (quirk packer umum, diikuti agar kompatibel).
- Arc baterai: 0° = atas, searah jarum jam; dipakai simetris di bawah (135→225)
  agar robust.
- File ditulis **uncompressed** (byte 40 = 0xFF); jam dan parser referensi
  sama-sama mendukungnya.
