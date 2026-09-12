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

## Instalasi ke Jam (via Scan QR)

Aplikasi Zepp versi sekarang tidak menyediakan pilih file langsung — instalasi
lewat **Developer Mode → + → Scan** memakai QR berisi URL unduhan `.bin`:

1. Pastikan HP dan laptop tersambung ke **WiFi yang sama**.
2. Di laptop, jalankan server file dari folder `out/` (sudah berisi `.bin`):
   ```powershell
   cd out
   python -m http.server 8000
   ```
   Biarkan jendela ini terbuka selama instalasi.
3. Buka gambar **`assets/qr_install.png`** di laptop (tampilkan penuh di layar).
   QR ini mengarah ke `http://192.168.100.29:8000/telu_trex_pro.bin`
   (sesuaikan IP bila WiFi berbeda, lalu generate ulang QR-nya).
4. Di Zepp App: Developer Mode → **+** → **Scan** → scan QR di layar laptop.
5. Tunggu unduhan selesai → pilih T-Rex Pro → sync ke jam → pilih
   watchface TEL-U di jam.

Catatan:
- Bila scan gagal mengunduh (mis. aplikasi menolak `http`), alternatifnya:
  push repo ini lalu buat QR dari URL raw GitHub
  `https://raw.githubusercontent.com/fathahnoor/telu-amazfit-trex-pro-watchface/main/out/telu_trex_pro.bin`
  (https, selalu bisa diunduh HP).
- Matikan server (`Ctrl+C`) setelah selesai.

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
