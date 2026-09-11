# Build & Instalasi — TEL-U Watchface (T-Rex Pro)

## Tahap Saat Ini

Repo ini berisi **design kit lengkap**: tema warna TEL-U, layout 360×360,
asset PNG (background, branding, AM/PM, digit 0–9), dan mockup preview.
Mockup `assets/preview/preview_360.png` menampilkan hasil akhir yang dituju.

## Cara Menjadikan .bin di T-Rex Pro

Karena T-Rex Pro adalah perangkat **non-Zepp OS**, build dilakukan lewat editor
komunitas yang mendukung model T-Rex Pro (360×360):

### Opsi A — Amazfit Watchface Editor (Android, paling mudah)
1. Install dari Play Store: *Amazfit Watchface Editor* (paolo4c).
2. Pilih model **T-Rex Pro**.
3. Buat layout kosong, lalu import/letakkan asset dari `assets/360x360/`:
   - `bg.png` → background full
   - `digits/0..9.png` → digit jam besar (posisi lihat `design/LAYOUT.md`)
   - `ampm.png` → penanda AM/PM
   - `branding.png` → ornamen bawah
4. Tambahkan data fields: KCAL, STEP, HR, baterai, tanggal (warna: merah
   `#ED1E28`, marun `#B6252A`, abu `#959597` — lihat `design/telu-theme.md`).
5. Export → `.bin` + preview.

### Opsi B — SashaCX75 AmazFit Watchface Editor (Windows)
1. Download dari GitHub: SashaCX75/AmazFit_Watchface_Editor (releases).
2. Pilih profil T-Rex (360×360).
3. Rekonstruksi layout sesuai `design/LAYOUT.md` + `design/watchface.json`.
4. Save/Export `.bin`.

### Opsi C — Biner legacy (manual)
1. Ambil watch face bawaan T-Rex Pro yang mirip (mis. rigger), unpack dengan
   tool packer/unpacker `.bin` komunitas.
2. Timpa image + ubah koordinat sesuai `design/watchface.json`.
3. Pack ulang → `telu_trex_pro.bin`.

## Instalasi ke Jam

1. **Zepp App** → Profile → Settings → About → tap logo Zepp 5–7×
   → "Developer mode activated".
2. Profile → device **T-Rex Pro** → Developer → Watch Face → **+**.
3. Scan QR (dari editor Android) **atau** pilih file `.bin` hasil export.
4. Sync ke jam → pilih watch face TEL-U di jam.

## Catatan Preview Katalog

Preview untuk katalog Zepp: **220×220** — sudah disediakan di
`assets/preview/preview_220.png`.
