# Research: Workflow Editor & Pembuatan .bin T-Rex Pro

**Tanggal:** 2026-09-12

## Rangkuman Temuan

1. **Zepp OS Watchface Maker (official)** — docs.zepp.com. Perangkat yang didukung
   adalah Zepp OS saja; **T-Rex Pro tidak masuk daftar** (non-Zepp OS). QR deploy
   dari tool ini tidak akan valid untuk T-Rex Pro.
2. **Amazfit Watchface Editor (paolo4c, Android)** — Play Store, rating 4.1 (763 ulasan).
   Alur: pilih model → desain → export → install. Mendukung model klasik T-Rex.
3. **SashaCX75 AmazFit Watchface Editor (Windows)** — GitHub releases; changelog
   menyebut dukungan T-Rex (sejak Feb 2021).
4. **amazfitwatchfaces.com** — katalog + forum "How to create watch face [T-Rex Pro]".
5. Tool legacy (v1ack watchfaceEditor, YueErro) — untuk Bip/Cor; konsep unpack/pack
   .bin sama tapi format beda antar generasi device.

## Keputusan

- Repo ini menghasilkan **design kit** (asset + koordinat + preview) yang
  editor-agnostic: bisa direkonstruksi di editor Android maupun Windows.
- Packer `.bin` mandiri ditunda sampai format binary T-Rex Pro tereverse
  lebih jauh (butuh sampel .bin asli untuk dibandingkan).

## Link

- https://docs.zepp.com/docs/reference/related-resources/device-list/
- https://play.google.com/store/apps/details?id=paolo4c.zepp.wfeditor
- https://github.com/SashaCX75/AmazFit_Watchface_Editor
- https://amazfitwatchfaces.com/forum/viewtopic.php?t=3605
