# Research: Format .bin T-Rex Pro (UIHH_GT2)

**Tanggal:** 2026-09-12
**Metode:** unduh 4 file T-Rex Pro asli dari amazfitwatchfaces.com, bedah biner,
validasi silang dengan implementasi referensi (watchface-js, Nadeflore).

## Temuan Utama

1. T-Rex Pro **bukan** format "HMDIAL" (dipakai GTR/Verge/T-Rex gen 1 via
   WatchFace.exe EXOMODE), melainkan kontainer **"UIHH" versi 2** — satu
   keluarga dengan GTR 2. Signature 4 byte pertama: `55 49 48 48` ("UIHH").
2. File asli di katalog umumnya **terkompresi** (chunk LZ77 kustom mulai byte 40,
   magic `0x4F`/`0x4E`). Packer repo ini menulis **uncompressed** (byte 40 =
   `0xFF`) — didukung reader referensi dan (sesuai struktur format) jam.
3. Layout 88-byte header: signature (0-3), version `02 00` (4-5),
   `maxParamLength` u32 di offset 76, `paramsInfoSize` u32 di offset 80.
   Byte lain (12-23, 32-35, ...) berbeda antar file asli dan diabaikan reader —
   disalin dari template yang juga berasal dari file asli.
4. Parameters: struktur protobuf-like (varint 7-bit; key = descriptor>>3;
   flag `0x02` = punya anak (blok N byte); flag `0x05` = float32 LE).
   Top-level: `1` = info `{1: totalParamsSize, 2: storedImageCount}`,
   `3` = Background, `4` = Time, `5` = System, `10` = IdleScreen (AOD).
5. Images: tabel offset u32 (sebanyak `stored-1` entri) lalu blob gambar.
   `stored = jumlah_gambar + 1` pada semua file asli (quirk, diikuti).
   Blob gambar: signature `BM` (byte `42 4D`), lalu 16-bit indexed (palet),
   24-bit (alpha + RGB565 BE), 32-bit, atau kompresi RLE `0x65`.
6. Preview 220×220 adalah gambar biasa di dalam tabel (atau referensi
   menggantung pada sebagian file); packer repo ini selalu menanam preview
   valid sebagai gambar terakhir dan merujuknya dengan benar.
7. Skema parameter lengkap (nama field) diadaptasi dari
   `UIHH_GT2.json` milik watchface-js. Elemen yang dipakai desain ini:
   Background, Time.Digital (HoursMinutesSeconds Type 0/1 + badge AM/PM),
   System.Date (YearMonthDay Type 2 + Week 7 gambar), System.Data
   (Battery CircleScale + NumberSequence, Steps, Calories, HeartRate),
   IdleScreen (jam + weekday + arc baterai).
8. Weekday: lihat bagian Konvensi di `docs/build-install.md`.

## Validasi Packer Repo Ini (`tools/trexpro_wf.py`)

- Dekompresor: **byte-identik** dengan referensi pada file asli 430 KB.
- Unpack file asli: 79/79 gambar **piksel-identik** dengan referensi.
- Pack ulang file asli → parse referensi: 79 gambar + parameter **identik**.
- Pack desain TEL-U → parse balik: 43 gambar + parameter **identik**
  (toleransi kuantisasi RGB565 ≤ 7 pada tepi antialias).
